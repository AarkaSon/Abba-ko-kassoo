"""
Parity test: the browser calculator must agree with the Python engine.

WHY THIS EXISTS
---------------
web/index.html contains a JavaScript port of src/pavement/*.py so the free public
calculator runs entirely client-side (no server cost, works offline, collects no
personal data). A port that silently diverges from the reference implementation is
worse than no port at all: it would publish wrong engineering numbers under our name.

This test extracts the JS engine from the HTML, runs it under Node, and compares
every computed quantity against the Python reference. Tolerance is 1e-9 relative.

Skips cleanly (exit 0) if Node is unavailable.
"""

from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

HTML = ROOT / "web" / "index.html"
TOL = 1e-9

CASES = [
    dict(h=300, E=30000, mu=.15, k=.08, mr=4.5, L=4500, W=3500, axle=15, p=.8,
         reps=500000, dTd=16.8, dTn=8.4, alpha=10e-6),
    dict(h=250, E=28000, mu=.15, k=.05, mr=4.0, L=4000, W=3500, axle=12, p=.7,
         reps=200000, dTd=13.0, dTn=6.5, alpha=9e-6),
    dict(h=350, E=32000, mu=.15, k=.12, mr=5.0, L=5000, W=3750, axle=20, p=.85,
         reps=1000000, dTd=18.0, dTn=9.0, alpha=11e-6),
    dict(h=200, E=25000, mu=.15, k=.03, mr=3.8, L=3500, W=3500, axle=10, p=.7,
         reps=100000, dTd=11.0, dTn=5.5, alpha=8e-6),
    # zero temperature differential -> must reduce to the load-only case
    dict(h=300, E=30000, mu=.15, k=.08, mr=4.5, L=4500, W=3500, axle=15, p=.8,
         reps=500000, dTd=0.0, dTn=0.0, alpha=10e-6),
]


def extract_js() -> str:
    src = HTML.read_text(encoding="utf-8")
    m = re.search(r"const EULER.*?(?=\nfunction num\()", src, re.S)
    if not m:
        raise AssertionError("Could not locate the JS engine block in web/index.html")
    return m.group(0)


def run_node(js: str) -> list[dict]:
    harness = (
        js
        + "\nconst cases=" + json.dumps(CASES) + ";\n"
        + "console.log(JSON.stringify(cases.map(v=>{const r=analyse(v);"
          "return{l:r.l,a:r.a,sLoad:r.sLoad,Cg:r.Cg,wDay:r.wDay,wNit:r.wNit,"
          "sBUC:r.sBUC,sTDC:r.sTDC,srG:r.srG,cfd:r.cfd,gov:r.gov};})));\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(harness)
        path = fh.name
    out = subprocess.run(["node", path], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(f"Node failed: {out.stderr[:400]}")
    return json.loads(out.stdout)


def python_reference(v: dict) -> dict:
    from src.design.westergaard import SlabProperties, WheelLoad, stress_edge
    from src.pavement.damage import allowable_repetitions_fatigue
    from src.pavement.thermal import check_both_mechanisms

    slab = SlabProperties(h=v["h"], E=v["E"], mu=v["mu"], k=v["k"])
    P = v["axle"] * 1000 * 9.81 / 2
    wl = WheelLoad.from_pressure(P=P, p=v["p"])
    s_load = stress_edge(slab, wl)
    r = check_both_mechanisms(
        s_load, slab.E, v["dTd"], v["dTn"], v["L"], v["W"], slab.l, v["mr"],
        alpha=v["alpha"],
    )
    n = allowable_repetitions_fatigue(r["governing"].stress_ratio)
    cfd = v["reps"] / n if math.isfinite(n) else 0.0
    return {
        "l": slab.l, "a": wl.a, "sLoad": s_load,
        "Cg": max(r["bradbury_C_length"], r["bradbury_C_width"]),
        "wDay": r["BUC"].warping_stress, "wNit": r["TDC"].warping_stress,
        "sBUC": r["BUC"].total_stress, "sTDC": r["TDC"].total_stress,
        "srG": r["governing"].stress_ratio, "cfd": cfd,
        "gov": r["governing"].mechanism,
    }


def test_js_matches_python():
    if shutil.which("node") is None:
        print("  SKIP  node not available")
        return
    js_results = run_node(extract_js())
    assert len(js_results) == len(CASES)

    worst = 0.0
    for i, (v, jr) in enumerate(zip(CASES, js_results), 1):
        pr = python_reference(v)
        assert jr["gov"] == pr["gov"], (
            f"case {i}: governing mechanism differs "
            f"(js={jr['gov']}, py={pr['gov']})"
        )
        for key, pv in pr.items():
            if key == "gov":
                continue
            jv = jr[key]
            err = abs(pv - jv) / max(abs(pv), 1e-12)
            worst = max(worst, err)
            assert err < TOL, (
                f"case {i}, {key}: python={pv!r} js={jv!r} rel.err={err:.3e}"
            )
    print(f"  (worst relative error {worst:.2e} across "
          f"{len(CASES)} cases)")


def test_zero_gradient_case_reduces_to_load_only():
    """The final case has dT = 0; BUC must equal the load-only stress exactly."""
    v = CASES[-1]
    pr = python_reference(v)
    assert math.isclose(pr["sBUC"], pr["sLoad"], rel_tol=1e-12)
    assert pr["wDay"] == 0.0


def test_html_has_required_disclaimer():
    """Liability control: the advisory disclaimer must not be removed."""
    src = HTML.read_text(encoding="utf-8").lower()
    for phrase in ("decision-support", "licensed engineer", "advisory"):
        assert phrase in src, f"missing required disclaimer text: {phrase!r}"


def test_html_collects_no_personal_data():
    """DPDP posture: the calculator must not collect personal data or call out."""
    src = HTML.read_text(encoding="utf-8").lower()
    for banned in ("<form", "fetch(", "xmlhttprequest", "google-analytics",
                   'type="email"', 'type="password"'):
        assert banned not in src, f"calculator must stay offline/anonymous: {banned!r}"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    fails = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            fails += 1
            print(f"  FAIL  {fn.__name__}: {exc}")
    print(f"\n{len(fns) - fails}/{len(fns)} passed")
    sys.exit(1 if fails else 0)

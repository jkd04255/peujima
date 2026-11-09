"""PJM-012 build-only checks: no real key, no upload, no public deploy."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from build_pages import build_site, ANCHOR

DUMMY_KEY="a"*32


def main():
    original=(ROOT/"index.html").read_text(encoding="utf-8")
    assert original.count(ANCHOR)==1
    assert "window.PRZIMA_KAKAO_JS_KEY =" not in original
    with tempfile.TemporaryDirectory(prefix="przima-build-") as tmp:
        dist=Path(tmp)/"output"
        build_site(dist,DUMMY_KEY)
        html=(dist/"index.html").read_text(encoding="utf-8")
        assert "window.PRZIMA_KAKAO_JS_KEY = " in html
        assert DUMMY_KEY in html
        assert html.index("window.PRZIMA_KAKAO_JS_KEY = ") < html.index(ANCHOR)
        assert (dist/"pjm012-nearby.js").is_file()
        assert (dist/"pjm012-nearby.css").is_file()
        assert (dist/".nojekyll").is_file()
        assert set(x.name for x in dist.iterdir())=={"index.html","pjm012-nearby.js","pjm012-nearby.css",".nojekyll"}
        try:
            build_site(dist,"short")
        except ValueError:
            pass
        else:
            raise AssertionError("Must reject invalid Kakao JavaScript keys")
        without_key=subprocess.run(
            [sys.executable,str(ROOT/"scripts/build_pages.py"),"--output",str(Path(tmp)/"bad")],
            env={k:v for k,v in os.environ.items() if k!="PJM012_KAKAO_JS_KEY"},
            capture_output=True,text=True
        )
        assert without_key.returncode != 0
        assert not (Path(tmp)/"bad"/"index.html").exists()
        assert (ROOT/"index.html").read_text(encoding="utf-8")==original
    workflow=(ROOT/".github/workflows/pjm-012-pages-release.yml").read_text(encoding="utf-8")
    assert "  workflow_dispatch:" in workflow.splitlines()
    assert "  push:" not in workflow.splitlines() and "  pull_request:" not in workflow.splitlines()
    assert workflow.count("github.ref == 'refs/heads/main'")==2
    assert workflow.count("inputs.g3_release == 'PJM-012_G3_APPROVED'")==2
    assert "actions/deploy-pages@v4" in workflow
    print("PASS: Pages release workflow requires explicit G3 input on main and has no automatic trigger")
    print("PASS: build injects synthetic public JS key BEFORE nearby script and excludes secrets from committed source")
    print("PASS: deployment build fails closed when the real release key is missing")
    print("PASS: no deployment or persistent release artifact created")


if __name__=="__main__":main()

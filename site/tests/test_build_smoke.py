import subprocess, sys, pathlib
REPO = pathlib.Path(__file__).resolve().parents[2]
def test_strict_build_succeeds():
    # phlipped.json must exist first (gen script reads it)
    subprocess.run([sys.executable, "-m", "build.build"], cwd=REPO, check=True)
    r = subprocess.run(["mkdocs", "build", "--strict", "-f", "site/mkdocs.yml"],
                       cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr

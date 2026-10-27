import subprocess, sys, pathlib

import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]


def test_strict_build_succeeds():
    # phlipped.json must exist first (gen script reads it)
    subprocess.run([sys.executable, "-m", "build.build"], cwd=REPO, check=True)
    r = subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict", "-f", "site/mkdocs.yml"],
                       cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    # site/hooks.py excludes the generated literate-nav sources from the output
    assert list((REPO / "_site").glob("**/SUMMARY.md")) == []


def test_nav_has_all_sections():
    cfg = yaml.safe_load((REPO / "site/mkdocs.yml").read_text())
    flat = str(cfg["nav"])
    for label in ["Start", "Catalog", "Detect", "Mitigation", "Matrix", "Mapping",
                  "Assessment", "Hardening", "Reference"]:
        assert label in flat

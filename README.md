# PHLIPPED

![ci](https://github.com/phlipped-fw/phlipped/actions/workflows/ci.yml/badge.svg)

A defensive framework for physical electronic attacks: badge cloning, keystroke
injection, drop devices and rogue radios. PHLIPPED catalogs the threats, scores
how exposed an organisation is, and maps each threat to a concrete detection and
fix.

Live site: **https://phlipped.n0t.space**

## Layout

```
catalog/   threat source (PHL-T-NNN.md) + JSON schema + build.py -> catalog.json
tools/assess/    phlipped-assess: CLI that scores posture (PSPS) and reports gaps
rules/     detection rules (Sigma + Wazuh), PHL-D-NNN, mapped 1:1 to threats
lab/       docker-compose Wazuh lab for validating rules (documented)
site/      static site generator -> site/public (deployed to phlipped.n0t.space)
docs/      narrative docs: the worked thread and the about page
```

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

python catalog/build.py        # validate threats + build catalog.json
pytest tools/assess -q               # run the assessment tool's tests
python site/build.py           # build the static site into site/public
python site/linkcheck.py       # check internal links
```

Run an assessment:

```bash
phlipped-assess run --out assessment.json
phlipped-assess report --in assessment.json --out report.html
```

## Status

Alpha. The catalog holds ten threats, the assessment tool and one fully-worked
thread (MIFARE badge cloning, `PHL-T-003`) are complete, and the site deploys on
push. Full detection-rule coverage and a live validation lab are roadmap, not in
this release.

## License

MIT. See [LICENSE](LICENSE).

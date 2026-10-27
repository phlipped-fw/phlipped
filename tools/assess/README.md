# phlipped-assess

Python CLI that runs the PHLIPPED assessment checklist and produces a **Physical Security Posture Score (PSPS)** between 0 and 100, plus an HTML/PDF report with prioritised gaps.

## Install

```bash
pipx install phlipped-assess         # once published
# or, from source:
pip install -e .
```

## Use

```bash
python -m build.build                     # from the repo root: writes phlipped.json
phlipped-assess run                       # interactive checklist
phlipped-assess run --answers answers.yml # non-interactive
phlipped-assess report --out report.html
```

Assessment items are read from the built `phlipped.json` (default `./phlipped.json`, override with `--data` on `run`, `report` and `list-items`).

## License

MIT.

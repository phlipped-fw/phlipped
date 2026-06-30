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
phlipped-assess run                       # interactive checklist
phlipped-assess run --answers answers.yml # non-interactive
phlipped-assess report --out report.html
```

## License

MIT.

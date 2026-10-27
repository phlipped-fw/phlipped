# PHLIPPED

![ci](https://github.com/phlipped-fw/phlipped/actions/workflows/ci.yml/badge.svg)

A defensive framework for physical electronic attacks: badge cloning, keystroke
injection, drop devices and rogue radios. PHLIPPED catalogs the threats, scores how
exposed an organisation is, and maps each threat to a detection, a mitigation, and
the compliance frameworks that require it.

The framework is one validated dataset. Per-object source files under `data/` are
compiled by a Python build into a single `phlipped.json`; the site and the
assessment tool are consumers of that artifact.

Live site: **https://phlipped.n0t.space**

## Layout

```
data/        source of truth, one file per object:
               techniques/ tactics/ data_sources/ detections/ mitigations/ mappings/ assessment/
schema/      a JSON Schema per object type
build/       the build: validate + resolve cross-references + emit phlipped.json
tools/assess/  phlipped-assess: CLI that scores posture (PSPS) off the built artifact
docs/        the data model, design decisions, build guide, and narrative pages
lab/         docker-compose Wazuh lab for validating detections (roadmap)
```

See [docs/data-model.md](docs/data-model.md) for the object graph and
[docs/building.md](docs/building.md) to get started.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

python -m build.build                 # validate the graph + build phlipped.json
pytest build/tests tools/assess -q    # run the build and tool tests
```

Run an assessment:

```bash
phlipped-assess run --data phlipped.json --out assessment.json
phlipped-assess report --in assessment.json --out report.html
```

## Status

Alpha. The data layer is complete: ten techniques, a provisional tactic axis, eight
data sources, three detections, eighteen mitigations, six assessment items, and
twenty-nine MITRE mappings, all validated by the build and covered by tests. The
taxonomy is provisional and is refined by a systematic literature review. The
documentation site is built with Material for MkDocs from `phlipped.json` and
deploys through Cloudflare Pages (see `DEPLOY.md`). Full detection coverage
and a live validation lab are roadmap, not in this release.

## License

MIT. See [LICENSE](LICENSE).

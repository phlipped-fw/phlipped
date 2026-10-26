# phlipped-catalog

Canonical Threat Catalog for the PHLIPPED framework. Markdown source of truth + JSON build artifact.

Entries are identified `PHL-T-NNN`. Each entry includes:

- Unique ID and short name
- Prerequisites (physical access, time, hardware, skill 1-5)
- MITRE ATT&CK mapping (Enterprise)
- Observable indicators (logs, network, physical)
- Known tools (Flipper Zero, Proxmark3, ChameleonMini, …)
- Severity baseline (physical-adapted CVSS)

## Layout

```
threats/        # one .md per threat (PHL-T-NNN.md)
schema/         # JSON schema for build artifact
catalog.json    # generated - do not edit by hand
```

## Build

```bash
python build.py   # produces catalog.json from threats/*.md frontmatter
```

## License

MIT.

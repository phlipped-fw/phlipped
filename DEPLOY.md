# Deploying the site

The site is built from `phlipped.json` and the prose in `docs/` with Material for MkDocs, and hosted on Cloudflare Pages. CI runs the same strict build on every push, so a broken link or a bad generated page fails before it reaches Pages.

## Cloudflare Pages build

Create (or edit) the Pages project for this repo with these settings.

| Setting | Value |
| --- | --- |
| Production branch | `main` |
| Build command | `pip install -r requirements-site.txt && python -m build.build && mkdocs build -f site/mkdocs.yml` |
| Build output directory | `_site` |
| Root directory | repo root (leave empty) |

Environment variables, set for both production and preview:

| Variable | Value |
| --- | --- |
| `PYTHON_VERSION` | `3.12` |
| `NO_MKDOCS_2_WARNING` | `1` |

The order in the build command is fixed. `python -m build.build` validates the data and emits `phlipped.json`; the page generator in `site/gen/gen_pages.py` reads that file, so `mkdocs build` has to run after it. The Pages build omits `--strict` because CI already enforces it on the same commit; add it if you want Pages to refuse a broken build on its own.

To reproduce the build locally:

```bash
pip install -r requirements-site.txt
python -m build.build
mkdocs build --strict -f site/mkdocs.yml
```

The output lands in `_site/`.

## Cutover runbook

Run by hand, not by CI or any script. These steps touch live DNS and a public site.

1. In the Cloudflare dashboard, point the `phlipped.n0t.space` Pages project at this repository and apply the settings above.
2. Push or merge to `main` and open the preview build. Check that the technique catalog, the tactic matrix and the MITRE mappings table all render, and that internal links between them resolve.
3. Promote the build and attach the custom domain `phlipped.n0t.space` to the project. Confirm the site loads over HTTPS on that domain.
4. Retire `docs.n0t.space`: remove its custom domain and take the old Pages project down. Do not set up a redirect: the old address is retired outright.
5. Decoupling the separate n0t.space repo from the old docs app happens only after step 3 is confirmed live. Do not begin it earlier.

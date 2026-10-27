"""MkDocs hooks for the PHLIPPED site."""
from mkdocs.plugins import event_priority
from mkdocs.structure.files import InclusionLevel


@event_priority(-200)  # after literate-nav (-100), which reads the SUMMARY.md files in on_files
def on_files(files, config):
    """Keep the generated per-section SUMMARY.md nav sources out of the built site."""
    for f in files:
        if f.src_uri.endswith("/SUMMARY.md") or f.src_uri == "SUMMARY.md":
            f.inclusion = InclusionLevel.EXCLUDED
    return files

import pathlib
import sys

# `site` shadows the stdlib module, so the generator is imported by its top-level
# name from site/gen rather than as a package.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "gen"))

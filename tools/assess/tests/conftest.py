import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from build.build import build, build_matrix  # noqa: E402


@pytest.fixture(scope="session")
def data_path(tmp_path_factory) -> Path:
    """A phlipped.json assembled from the real data/, built into a tmp dir so
    the tests never depend on a pre-existing artifact in the repo."""
    graph, errors = build()
    assert errors == []
    path = tmp_path_factory.mktemp("built") / "phlipped.json"
    path.write_text(json.dumps(dict(graph, mappings_matrix=build_matrix(graph))), encoding="utf-8")
    return path

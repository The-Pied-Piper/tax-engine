from collections.abc import Iterator
from pathlib import Path

import pytest

from tax_calculator.adapters.outbound.yaml_support import YamlNode

_REPOSITORY = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session", autouse=True)
def _parse_repository_yaml_once() -> Iterator[None]:
    """Parse each YAML file of the repository once per test process, not once per computation.

    Every computed return reads the manifest and the datasets again, so most of a run was spent
    parsing the same files. Files outside the repository (a test's `tmp_path`) are read as usual,
    and a cached file is re-read when its size or modification time changes.
    """
    parsed: dict[tuple[Path, str, int, int], YamlNode] = {}
    load = YamlNode.load

    def load_once(cls: type[YamlNode], path: Path, label: str) -> YamlNode:
        resolved = path.resolve()
        if not resolved.is_relative_to(_REPOSITORY):
            return load(path, label)
        stat = resolved.stat()
        key = (resolved, label, stat.st_mtime_ns, stat.st_size)
        if key not in parsed:
            parsed[key] = load(path, label)
        return parsed[key]

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(YamlNode, "load", classmethod(load_once))
        yield

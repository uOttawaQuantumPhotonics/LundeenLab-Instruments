"""Test source-preserving CERCuO importer without network/hardware."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


def _load_importer():
    path = Path(__file__).resolve().parents[1] / 'scripts' / 'import_cercuo.py'
    spec = importlib.util.spec_from_file_location('import_cercuo', path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_source_copies_verbatim_and_manifest(tmp_path):
    importer = _load_importer()
    source = tmp_path / 'Python' / 'Core'
    for dirname in ('Dependencies', 'Drivers', 'Methods'):
        (source / dirname).mkdir(parents=True)
    source_code = b'# example original\r\nvalue = "\xc3\xb1"\r\n'
    (source / 'Drivers' / 'Example.py').write_bytes(source_code)
    (source / 'Drivers' / 'raw.csv').write_text('1,2\n')
    dest = tmp_path / 'out'
    assert importer.copy_sources(importer.source_files(source.parent), dest, 'test') == 1
    assert (dest / 'Core' / 'Drivers' / 'Example.py').read_bytes() == source_code
    assert not (dest / 'Core' / 'Drivers' / 'raw.csv').exists()
    manifest = json.loads((dest / 'CERCUO_MANIFEST.json').read_text())
    assert manifest['files']['Core/Drivers/Example.py'] == hashlib.sha256(source_code).hexdigest()
    assert (dest / 'Core' / 'Drivers' / '__init__.py').exists()


def test_importer_refuses_implicit_overwrite(tmp_path):
    importer = _load_importer()
    root = tmp_path / 'Core'
    for dirname in ('Dependencies', 'Drivers', 'Methods'):
        (root / dirname).mkdir(parents=True)
    f = root / 'Drivers' / 'Device.py'
    f.write_text('pass\n')
    dest = tmp_path / 'out'
    importer.copy_sources(importer.source_files(root), dest, 'test')
    f.write_text('print("change")\n')
    with pytest.raises(FileExistsError):
        importer.copy_sources(importer.source_files(root), dest, 'test')
    assert importer.copy_sources(importer.source_files(root), dest, 'test', overwrite=True) == 1


def test_missing_source_raises(tmp_path):
    importer = _load_importer()
    with pytest.raises(ValueError, match='Source'):
        list(importer.source_files(tmp_path))


def test_legacy_requires_imported_sources(monkeypatch, tmp_path):
    import lundeen_instruments.legacy as legacy

    monkeypatch.setattr(legacy, "__file__", str(tmp_path / "__init__.py"))
    with pytest.raises(FileNotFoundError, match="not bundled"):
        legacy.enable_legacy_imports()

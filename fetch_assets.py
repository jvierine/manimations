"""Restore optional build inputs from juha.no; keep binary assets out of Git."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import tarfile
import tempfile
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true', help='check local assets without downloading')
    options = parser.parse_args()
    manifest = json.loads((ROOT / 'asset_manifest.json').read_text())
    missing = []
    for entry in manifest['files']:
        path = (ROOT / entry['path']).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError('Asset path escapes the checkout')
        if not path.is_file() or digest(path) != entry['sha256']:
            missing.append(entry)
    if options.verify and missing:
        raise SystemExit(f'{len(missing)} assets are missing or changed; run fetch_assets.py')
    if missing:
        with tempfile.TemporaryDirectory(prefix='manimations-assets-') as folder:
            archive = Path(folder) / 'assets.tar.gz'
            with urlopen(manifest['url'], timeout=120) as source, archive.open('wb') as output:
                shutil.copyfileobj(source, output)
            if digest(archive) != manifest['sha256']:
                raise ValueError('Asset archive checksum mismatch')
            with tarfile.open(archive, 'r:gz') as bundle:
                for entry in missing:
                    member = bundle.getmember(entry['path'])
                    if not member.isfile():
                        raise ValueError('Asset archive member is not a regular file')
                    temporary = Path(folder) / 'asset'
                    with bundle.extractfile(member) as source, temporary.open('wb') as output:
                        shutil.copyfileobj(source, output)
                    if digest(temporary) != entry['sha256']:
                        raise ValueError(f"Asset checksum mismatch: {entry['path']}")
                    target = ROOT / entry['path']
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(temporary, target)
    print(f"Verified {len(manifest['files'])} external build assets; restored {len(missing)}.")


if __name__ == '__main__':
    main()

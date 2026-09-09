#!/usr/bin/env python3
"""Build a clean Linux distribution, optionally with an offline wheelhouse."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tarfile
from release_files import release_files

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'release/centro-operaciones-linux.tar.gz')
    parser.add_argument('--wheelhouse', type=Path)
    args = parser.parse_args()
    required = ['static/dist/dashboard.js', 'static/dist/dashboard.css', 'templates/_assets.html',
                'static/brand/fh2xhikcentral.png', 'requirements.lock']
    for name in required:
        if not (ROOT / name).is_file():
            parser.error(f'Falta {name}. Ejecuta npm ci && npm run build antes de empaquetar.')
    manifest = (ROOT / 'templates/_assets.html').read_text()
    versions = json.loads(re.search(r'{% set versions = (.*?) %}', manifest, re.S)[1])
    for name, digest in versions.items():
        if hashlib.sha256((ROOT / 'static' / name).read_bytes()).hexdigest()[:12] != digest:
            parser.error(f'El recurso {name} cambió: ejecuta npm run build.')
    wheel_files = []
    if args.wheelhouse:
        wheel_files = sorted(args.wheelhouse.glob('*.whl'))
        if not wheel_files:
            parser.error('El wheelhouse no contiene archivos .whl.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(args.output, 'w:gz') as archive:
        for path in release_files(ROOT):
            archive.add(path, arcname='centro-operaciones/' + str(path.relative_to(ROOT)), recursive=False)
        for path in wheel_files:
            if path.is_symlink():
                parser.error('No se permiten enlaces simbólicos en wheelhouse.')
            archive.add(path, arcname='centro-operaciones/wheelhouse/' + path.name, recursive=False)
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.output.with_name(args.output.name + '.sha256').write_text(f'{digest}  {args.output.name}\n')
    print(args.output)
    print(f'SHA256: {digest}')
    print('Sin .env, cámaras, workflows, logs, entornos virtuales ni archivos Git.')


if __name__ == '__main__':
    main()

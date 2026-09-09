"""Explicit distribution allowlist: never package site data or credentials."""
from pathlib import Path

ROOT_FILES = [
    'app.py', 'config.py', 'manager.py', 'cameras.py', 'setup.py',
    'install.sh', 'diagnose.sh', 'requirements.txt', 'requirements.lock',
    '.env.example', 'cameras.json.example', 'workflows.json.example',
    'README.md', 'CHANGELOG.md', 'VERSION', 'package.json', 'package-lock.json',
]
DIRECTORIES = {
    'routes': {'.py'}, 'services': {'.py'}, 'templates': {'.html'},
    'static': {'.js', '.css', '.png', '.txt'}, 'icons': {'.png', '.jpg'},
    'frontend': {'.jsx', '.css', '.mjs', '.md'}, 'scripts': {'.py', '.sh'},
    'docs': {'.md'}, 'tests': {'.py'},
}


def release_files(root):
    root = Path(root).resolve()
    for name in ROOT_FILES:
        path = root / name
        if path.is_file() and not path.is_symlink():
            yield path
    for directory, suffixes in DIRECTORIES.items():
        for path in sorted((root / directory).rglob('*')):
            if path.is_file() and path.suffix in suffixes and not path.is_symlink():
                if any(part.startswith('.') or part == '__pycache__' for part in path.relative_to(root).parts):
                    continue
                if not path.resolve().is_relative_to(root):
                    raise ValueError(f'Ruta fuera del proyecto: {path}')
                yield path

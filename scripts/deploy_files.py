#!/usr/bin/env python3
"""Copy application files without replacing runtime data in the destination."""
from pathlib import Path
import shutil
import sys
from release_files import release_files

source, target = (Path(arg).resolve() for arg in sys.argv[1:3])
if source != target:
    for path in release_files(source):
        destination = target / path.relative_to(source)
        if destination.is_symlink() or not destination.resolve().is_relative_to(target):
            raise ValueError(f'Destino no seguro: {destination}')
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)

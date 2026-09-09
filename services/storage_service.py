"""Atomic file writes and one inter-process lock for camera/workflow changes."""
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
import fcntl
import json
import os
import tempfile

LOCK_FILE = Path(__file__).resolve().parent.parent / '.data.lock'


@contextmanager
def data_lock():
    with open(LOCK_FILE, 'a', encoding='utf-8') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def locked(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        with data_lock():
            return function(*args, **kwargs)
    return wrapper


def atomic_text(filename, text):
    path = Path(filename)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name + '.')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as output:
            output.write(text)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def atomic_json(filename, data):
    atomic_text(filename, json.dumps(data, ensure_ascii=False, indent=4) + '\n')

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from scripts.release_files import release_files

ROOT = Path(__file__).resolve().parent.parent


class DistributionTests(unittest.TestCase):
    def test_private_files_never_enter_distribution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ['app.py', '.env', 'cameras.json', 'workflows.json', '.env.example', 'requirements.lock']:
                (root / name).write_text('example')
            (root / 'logs').mkdir()
            (root / 'logs/events.json').write_text('private')
            (root / 'static').mkdir()
            (root / 'static/secret.js').symlink_to(root / '.env')
            names = {str(p.relative_to(root)) for p in release_files(root)}
            self.assertEqual(names, {'app.py', '.env.example', 'requirements.lock'})

    def test_deploy_preserves_runtime_data(self):
        with tempfile.TemporaryDirectory() as directory:
            source, target = Path(directory) / 'source', Path(directory) / 'target'
            source.mkdir(); target.mkdir()
            (source / 'app.py').write_text('new code')
            for name in ['.env', 'cameras.json', 'workflows.json']:
                (source / name).write_text('do not copy')
                (target / name).write_text('preserved')
            subprocess.run([sys.executable, str(ROOT / 'scripts/deploy_files.py'), str(source), str(target)], check=True)
            self.assertEqual((target / 'app.py').read_text(), 'new code')
            for name in ['.env', 'cameras.json', 'workflows.json']:
                self.assertEqual((target / name).read_text(), 'preserved')

    def test_shortcut_installs_without_opening_a_browser(self):
        import os
        with tempfile.TemporaryDirectory() as directory:
            environment = dict(os.environ, XDG_DATA_HOME=directory)
            subprocess.run(['bash', str(ROOT / 'scripts/install-shortcut.sh'), 'http://127.0.0.1:5000/dashboard'], env=environment, check=True, capture_output=True)
            shortcut = Path(directory) / 'applications/centro-operaciones.desktop'
            self.assertIn('Exec=xdg-open http://127.0.0.1:5000/dashboard', shortcut.read_text())
            self.assertTrue((Path(directory) / 'icons/centro-operaciones.png').is_file())

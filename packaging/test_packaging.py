import tempfile
import unittest
from pathlib import Path
import build_installer


class PackagingTests(unittest.TestCase):
    def test_uninstall_is_exact_and_non_recursive(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            (root / 'plugins/gui').mkdir(parents=True)
            (root / 'plugins/gui/qt.dll').write_bytes(b'test')
            (root / 'vlc.exe').write_bytes(b'test')
            (root / 'sdk').mkdir()
            (root / 'sdk/header.h').write_bytes(b'test')
            install, uninstall, count = build_installer.manifests(root)
            self.assertEqual(count, 2)
            self.assertNotIn('header.h', install)
            self.assertNotIn('RMDir /r', uninstall)
            self.assertIn('Delete "$INSTDIR\\vlc.exe"', uninstall)
            self.assertLess(uninstall.index('plugins\\gui"'), uninstall.index('RMDir "$INSTDIR\\plugins"'))

    def test_nsis_escape(self):
        self.assertEqual(build_installer.escape('a$b"c'), 'a$$b$\\"c')

    def test_no_stock_registration(self):
        source = Path(__file__).with_name('juxtopposed.nsi').read_text('utf-8')
        self.assertNotIn('HKLM', source)
        self.assertNotIn('HKCR', source)
        self.assertNotIn('RMDir /r', source)
        self.assertIn('RequestExecutionLevel user', source)
        self.assertIn('Software\\Quite\\VLCJuxtopposed', source)


if __name__ == '__main__':
    unittest.main()

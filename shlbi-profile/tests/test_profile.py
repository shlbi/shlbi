"""Offline checks. Run: python -m unittest discover -s tests -v"""
import copy
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import update_activity as activity
import build_art

class ActivityTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'data/activity.json').read_text())
    def test_valid_snapshot(self):
        self.assertEqual(activity.validate(self.data)['schema'],1)
    def test_private_repository_rejected(self):
        self.data['repositories'][0]['public']=False
        with self.assertRaises(ValueError):activity.validate(self.data)
    def test_unknown_repository_rejected(self):
        self.data['repositories'][0]['repo']='shlbi/private-example'
        with self.assertRaises(ValueError):activity.validate(self.data)
    def test_profile_repository_excluded(self):
        self.assertNotIn('shlbi/shlbi',activity.REPOS)
    def test_duplicate_repository_rejected(self):
        self.data['repositories'][1]=copy.deepcopy(self.data['repositories'][0])
        with self.assertRaises(ValueError):activity.validate(self.data)
    def test_bad_sha_rejected(self):
        self.data['repositories'][0]['sha']='not-a-sha'
        with self.assertRaises(ValueError):activity.validate(self.data)
    def test_foreign_commit_link_rejected(self):
        self.data['repositories'][0]['url']='https://example.com/untrusted'
        with self.assertRaises(ValueError):activity.validate(self.data)
    def test_multiline_subject_rejected(self):
        self.data['repositories'][0]['subject']='first line\nextra data'
        with self.assertRaises(ValueError):activity.validate(self.data)
    def test_unsafe_subject_is_escaped(self):
        self.data['repositories'][0]['subject']='<script>alert(1)</script> & extra'
        output=activity.draw(activity.validate(self.data))
        self.assertNotIn('<script>',output)
        self.assertIn('&lt;script&gt;',output)
        ET.fromstring(output)
    def test_desktop_and_mobile_svg_parse(self):
        for mobile in (False,True):
            root=ET.fromstring(activity.draw(self.data,mobile))
            self.assertEqual(root.tag,'{http://www.w3.org/2000/svg}svg')
    def test_draw_is_reproducible(self):
        self.assertEqual(activity.draw(self.data),activity.draw(self.data))
    def test_missing_readme_markers_preserves_files(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'README.md').write_text('unchanged')
            with self.assertRaises(ValueError):activity.publish(self.data,root)
            self.assertEqual((root/'README.md').read_text(),'unchanged')
            self.assertFalse((root/'data/activity.json').exists())
    def test_publish_preserves_surrounding_readme(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'README.md').write_text('BEFORE\n'+activity.START+'\nold\n'+activity.END+'\nAFTER')
            activity.publish(self.data,root)
            text=(root/'README.md').read_text()
            self.assertTrue(text.startswith('BEFORE\n'))
            self.assertTrue(text.endswith('\nAFTER'))
            self.assertEqual(json.loads((root/'data/activity.json').read_text()),self.data)
            self.assertTrue((root/'assets/mobile/activity.svg').exists())
    def test_api_failure_does_not_publish(self):
        with patch.object(sys,'argv',['update_activity.py']),patch.object(activity,'fetch_snapshot',side_effect=RuntimeError('simulated offline error')),patch.object(activity,'publish') as publish:
            self.assertEqual(activity.main(),1)
            publish.assert_not_called()

class RepositoryTests(unittest.TestCase):
    def test_all_artwork_is_valid_script_free_svg(self):
        paths=list((ROOT/'assets').rglob('*.svg'))
        self.assertGreaterEqual(len(paths),12)
        for path in paths:
            with self.subTest(path=path.name):
                root=ET.fromstring(path.read_text())
                self.assertEqual(root.tag,'{http://www.w3.org/2000/svg}svg')
                for node in root.iter():
                    name=node.tag.split('}')[-1]
                    self.assertNotIn(name,('script','foreignObject','iframe'))
                    self.assertFalse(any(k.lower().startswith('on') for k in node.attrib))
                    for key,value in node.attrib.items():
                        if key.endswith('href'):
                            self.assertFalse(value.startswith(('http','javascript:')))
    def test_all_readme_images_exist(self):
        text=(ROOT/'README.md').read_text()
        paths=re.findall(r'(?:src|srcset)="(\./[^\"]+)"',text)
        self.assertGreaterEqual(len(paths),12)
        for path in paths:self.assertTrue((ROOT/path).is_file(),path)
    def test_correct_name_in_readme_and_hero(self):
        self.assertIn('Saif Alshalabi',(ROOT/'README.md').read_text())
        for path in ['assets/hero.svg','assets/mobile/hero.svg']:
            self.assertIn('Saif Alshalabi',(ROOT/path).read_text())
    def test_reduced_motion_in_animated_assets(self):
        for path in (ROOT/'assets').rglob('*.svg'):
            text=path.read_text()
            if '@keyframes' in text:self.assertIn('prefers-reduced-motion:reduce',text)
    def test_no_distributed_font_files(self):
        for path in ROOT.rglob('*'):
            self.assertNotIn(path.suffix.lower(),('.ttf','.otf','.woff','.woff2'))
    def test_generated_art_matches_source(self):
        for mobile in (False,True):
            base=ROOT/'assets'/('mobile' if mobile else '')
            for name,fn in [('hero',build_art.hero),('repot',build_art.repot),('footer',build_art.footer)]:
                self.assertEqual((base/f'{name}.svg').read_text(),fn(mobile))
    def test_workflow_does_not_use_personal_token_or_force_push(self):
        text=(ROOT/'.github/workflows/refresh-profile.yml').read_text()
        self.assertIn('github.token',text)
        self.assertNotIn('secrets.PAT',text)
        self.assertNotIn('--force',text)
        self.assertIn("github.repository == 'shlbi/shlbi'",text)

if __name__=='__main__':unittest.main()

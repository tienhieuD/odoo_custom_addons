from odoo.modules.module import get_manifest
from odoo.tests import TransactionCase, tagged

MODULE = 'listview_sticky_header_and_column'


@tagged('post_install', '-at_install')
class TestAssets(TransactionCase):
    """The module is pure front-end: check that its files are shipped in the backend bundle."""

    def test_backend_bundle_contains_module_files(self):
        paths = [p[0] for p in self.env['ir.asset']._get_asset_paths('web.assets_backend', css=True, js=True)]
        self.assertIn('/%s/static/src/js/main.js' % MODULE, paths)
        self.assertIn('/%s/static/src/scss/main.scss' % MODULE, paths)

    def test_scss_compiles_without_error(self):
        qweb = self.env['ir.qweb']
        files, _remains = qweb._get_asset_content('web.assets_backend')
        bundle = qweb._get_asset_bundle('web.assets_backend', files, env=self.env, css=True, js=False)
        css = bundle.css()
        content = css.raw.decode()
        self.assertIn('.display-on-hover', content, "SCSS of the module is missing from the compiled CSS")
        self.assertIn('.o_list_renderer thead > tr > th:hover .display-on-hover', content)
        self.assertNotIn('css_error_message', content)

    def test_manifest_matches_series(self):
        manifest = get_manifest(MODULE)
        self.assertTrue(manifest['version'].startswith('16.0.'), manifest['version'])
        self.assertEqual(set(manifest['depends']), {'base', 'web'})
        self.assertFalse(manifest.get('data'), "pure front-end module: no data files expected")

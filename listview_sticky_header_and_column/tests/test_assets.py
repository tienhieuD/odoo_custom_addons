import base64

from odoo.modules.module import load_information_from_description_file
from odoo.tests import TransactionCase, tagged

MODULE = 'listview_sticky_header_and_column'


@tagged('post_install', '-at_install')
class TestAssets(TransactionCase):
    """The module is pure front-end: check that its files are shipped in the backend bundle."""

    def test_backend_bundle_contains_module_files(self):
        files, _remains = self.env['ir.qweb']._get_asset_content('web.assets_backend', {})
        urls = [f['url'] for f in files]
        self.assertIn('/%s/static/src/js/main.js' % MODULE, urls)
        self.assertIn('/%s/static/src/scss/main.scss' % MODULE, urls)

    def test_scss_compiles_without_error(self):
        qweb = self.env['ir.qweb']
        files, _remains = qweb._get_asset_content('web.assets_backend', {})
        bundle = qweb.get_asset_bundle('web.assets_backend', files, env=self.env)
        attachments = bundle.css()
        self.assertFalse(bundle.css_errors, bundle.css_errors)
        content = ''.join(base64.b64decode(a.datas).decode() for a in attachments)
        self.assertIn('.display-on-hover', content, "SCSS of the module is missing from the compiled CSS")
        self.assertIn('.o_list_view thead > tr > th:hover .display-on-hover', content)
        self.assertIn('.table-responsive.lshc-sticky-head', content)
        self.assertNotIn('css_error_message', content)

    def test_manifest_matches_series(self):
        manifest = load_information_from_description_file(MODULE)
        self.assertTrue(manifest['version'].startswith('13.0.'), manifest['version'])
        self.assertEqual(set(manifest['depends']), {'base', 'web'})
        self.assertEqual(manifest['data'], ['views/assets.xml'])

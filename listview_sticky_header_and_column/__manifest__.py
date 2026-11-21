{
    'name': "List View Sticky Header & Freeze Column",
    'summary': "Keep the list view header and first column visible while scrolling. Keywords: sticky header, fixed header, freeze header, freeze column, frozen column, sticky column, list view header, tree view header, fixed column, table header.",
    'description': """
        Fixed Header when scrolling vertically,
        Fixed Column when scrolling horizontally.
    """,
    'website': 'https://duotek.io.vn',
    'support': 'hello@duotek.io.vn',
    'author': "DuoTEK",
    'license': 'OPL-1',
    # 'website': "https://www.nissho-vn.com/en/",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '13.0.0.8.0',
    'live_test_url': 'https://demo-sticky.duotek.io.vn',
    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],
    # always loaded
    'data': [
        'views/assets.xml',
    ],
    "images": ['static/description/banner.png', 'static/description/theme_screenshot.png'],
    'price': 18.44,
    'currency': 'EUR',
    'external_dependencies': {}
}

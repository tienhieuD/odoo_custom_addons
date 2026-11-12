{
    'name': "List View Sticky Header & Freeze Column",
    'summary': """
        Fixed Header when scrolling vertically,
        Fixed Column when scrolling horizontally.
    """,
    'description': """
        Fixed Header when scrolling vertically,
        Fixed Column when scrolling horizontally.
    """,
    'website': 'https://duotek.io.vn',
    'support': 'hello@duotek.io.vn',
    'author': "DUO-TEK Software Vietnam",
    'license': 'LGPL-3',
    # 'website': "https://www.nissho-vn.com/en/",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '15.0.0.5.0',
    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],
    # always loaded
    'data': [
        # 'views/assets.xml',
    ],
    "images": ['static/description/banner.png', 'static/description/theme_screenshot.png'],
    'assets': {
        'web.assets_backend': [
            '/listview_sticky_header_and_column/static/src/scss/main.scss',
            '/listview_sticky_header_and_column/static/src/js/main.js',
        ],
        'web.assets_tests': [
            '/listview_sticky_header_and_column/static/tests/tours/**/*',
        ]
    },
    'price': 21.44,
    'currency': 'EUR',
    'external_dependencies': {}
}

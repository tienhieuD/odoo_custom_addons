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
    'website': 'https://live.staticflickr.com/65535/50701330062_5a6a35cd36_o.gif',
    'author': "DUO-TEK Software Vietnam",
    'license': 'LGPL-3',
    # 'website': "https://www.nissho-vn.com/en/",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '16.0.0',
    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],
    # always loaded
    'data': [
        # 'views/assets.xml',
    ],
    # 'qweb': ['static/src/xml/*.xml'],
    "images": ['static/description/banner.png', 'static/description/theme_screenshot.png'],
    'assets': {
        'web._assets_primary_variables': [
            'account/static/src/scss/variables.scss',
        ],
        'web.assets_backend': [
            'listview_sticky_header_and_column/static/src/scss/main.scss',
            'listview_sticky_header_and_column/static/src/js/main.js',
            'listview_sticky_header_and_column/static/src/xml/*.xml',
        ]
    },
    'price': 21.44,
    'currency': 'EUR',
    'external_dependencies': {}
}

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
    'license': 'OPL-1',
    'category': 'Extra Tools',
    'version': '18.0.0.7.0',
    'depends': ['base', 'web'],
    'data': [],
    "images": ['static/description/banner.png', 'static/description/theme_screenshot.png'],
    'assets': {
        'web.assets_backend': [
            'listview_sticky_header_and_column/static/src/scss/main.scss',
            'listview_sticky_header_and_column/static/src/js/main.js',
            'listview_sticky_header_and_column/static/src/xml/*.xml',
        ],
        'web.assets_tests': [
            'listview_sticky_header_and_column/static/tests/tours/**/*',
        ]
    },
    'price': 34.00,
    'currency': 'EUR',
    'external_dependencies': {}
}

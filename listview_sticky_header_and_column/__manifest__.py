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
    'category': 'Tools',
    'version': '18.0.0.1',
    'depends': ['base', 'web'],
    'data': [],
    "images": ['static/description/banner.png', 'static/description/theme_screenshot.png'],
    'assets': {
        'web.assets_backend': [
            'listview_sticky_header_and_column/static/src/scss/main.scss',
            'listview_sticky_header_and_column/static/src/js/main.js',
            'listview_sticky_header_and_column/static/src/xml/*.xml',
        ]
    },
    'price': 42.00,
    'currency': 'EUR',
    'external_dependencies': {}
}

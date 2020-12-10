{
    'name': "List View Sticky Header & Column",
    'summary': """
        Fixed Header when scrolling vertically,
        Fixed Column when scrolling horizontally.
    """,
    'description': """
        Fixed Header when scrolling vertically,
        Fixed Column when scrolling horizontally.
    """,
    'website': 'https://i.imgur.com/42fbqjS.gif',
    'author': "RainOnMe",
    'license': 'LGPL-3',
    # 'website': "https://www.nissho-vn.com/en/",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '0.2',
    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],
    # always loaded
    'data': [
        'views/assets.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    "images": ['static/description/banner.png', 'static/description/theme_screenshot.png'],
    'price': 19.99,
    'currency': 'EUR',
    'external_dependencies': {}
}

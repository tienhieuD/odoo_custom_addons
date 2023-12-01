# -*- coding: utf-8 -*-
{
    'name': "awesome_tshirt",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'awesome_tshirt/static/src/xml/**/*',
        ],
        'web.assets_backend': [
            'awesome_tshirt/static/src/scss/split_view.scss',
            'awesome_tshirt/static/src/js/split_listview.js',
            'awesome_tshirt/static/src/js/split_formview.js',
            'awesome_tshirt/static/src/js/split_view.js',
        ],
    }
}

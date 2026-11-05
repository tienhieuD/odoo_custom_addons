{
    'name': "List View Sticky - Test Lab",
    'summary': "Developer test bed: wide fake lists to try the sticky header / freeze column module.",
    'description': """
Developer-only test bed for listview_sticky_header_and_column.
Top-level app: List Sticky Test Lab.
The models have no table and no view: rows are generated on the fly by SQL (_table_query).
Do not publish this module.
    """,
    'author': "DUO-TEK Software Vietnam",
    'license': 'LGPL-3',
    'category': 'Hidden/Tools',
    'version': '19.0.1.0.0',
    'depends': ['base', 'web', 'listview_sticky_header_and_column'],
    'data': [
        'security/ir.model.access.csv',
        'views/lshc_test_views.xml',
        'views/lshc_test_menus.xml',
    ],
    'assets': {
        'web.assets_tests': ['listview_sticky_test_lab/static/tests/tours/*.js'],
    },
    'installable': True,
    'application': True,
}

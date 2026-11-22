{
    'name': "Demo: List View Sticky Header & Freeze Column",
    'summary': "Demo for listview_sticky_header_and_column: wide lists (52 columns, search panel, forms full of x2many lists) with 10 editable sample records.",
    'description': """
Demo module for listview_sticky_header_and_column: wide lists, a form full of x2many lists
(demo users come from demo_users).
Top-level app: List Sticky Test Lab. The 10 sample records and their lines are real rows (inserted at install), so they can be edited.
    """,
    'author': "DuoTEK",
    'license': 'OPL-1',
    'category': 'Hidden/Tools',
    'version': '19.0.2.0.0',
    'depends': ['demo_users', 'base', 'web', 'listview_sticky_header_and_column'],
    'data': [
        'security/ir.model.access.csv',
        'data/demo_partners.xml',
        'views/lshc_test_views.xml',
        'views/lshc_test_menus.xml',
    ],
    'assets': {
        'web.assets_tests': ['demo_listview_sticky_header_and_column/static/tests/tours/*.js'],
    },
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
}

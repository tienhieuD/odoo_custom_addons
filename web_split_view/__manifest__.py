{
    'name': 'Web Split View',
    'summary': 'Dual-view layout, seamlessly dividing the screen into list and detail sections for CRUD operations.',
    'description': """
Web Split View
==============
Adds a "Split" view type: the screen is divided into a list on the left and the form of the
selected record on the right, so records can be browsed, created, edited and deleted without
leaving the list.

Features:
- Resizable list / form panes (the width is remembered per view)
- Create, edit, save, discard and delete from the right pane; the list refreshes automatically
- The list keeps its own search bar, filters, grouping and pager
- Sub views by external id (list_view_ref / form_view_ref) or defined inline in the <split> tag
- Debug menu entries to add / remove a split view on any action
    """,
    'author': 'DUO-TEK Software Vietnam',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=DUO-TEK%20Software%20Vietnam',
    'license': 'LGPL-3',
    'category': 'Technical',
    'version': '19.0.1.0.0',
    'depends': ['web'],
    'data': [
        'security/ir.model.access.csv',
        'views/create_view_split_wizard.xml',
    ],
    'demo': [
        'data/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'web_split_view/static/src/split_view/**/*',
        ],
        'web.assets_tests': [
            'web_split_view/static/tests/tours/**/*',
        ],
    },
    'images': ['static/description/banner.png'],
    'uninstall_hook': '_uninstall_hook',
    'installable': True,
    'application': False,
}

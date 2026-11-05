{
    'name': 'Web Split View',
    'summary': 'Dual-view layout, seamlessly dividing the screen into list and detail sections for CRUD operations.',
    'description': """
Web Split View
==============
Adds a "Split" mode to the view switcher of every window action that has a list and a form view:
the screen is divided into a list on the left and the form of the selected record on the right, so
records can be browsed, created, edited and deleted without leaving the list. Nothing to configure:
the split view is derived from the action (its list, form and search views).

Features:
- Resizable list / form panes (the width is remembered per view)
- Create, edit, save, discard and delete from the right pane; the list refreshes automatically
- The list keeps its own search bar, filters, grouping and pager
- Sub views by external id (list_view_ref / form_view_ref) or defined inline in the <split> tag
- Settings > Split View switches the automatic mode on/off; a window action can opt out (No split view)
- Explicit <split> views and debug menu entries to add / remove a custom split view on an action
    """,
    'author': 'DUO-TEK Software Vietnam',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=DUO-TEK%20Software%20Vietnam',
    'license': 'OPL-1',
    'category': 'Technical',
    'version': '16.0.1.0.0',
    'depends': ['web'],
    'data': [
        'security/ir.model.access.csv',
        'views/create_view_split_wizard.xml',
        'views/res_config_settings_views.xml',
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
    'price': 39.00,
    'currency': 'USD',
    'uninstall_hook': '_uninstall_hook',
    'installable': True,
    'application': False,
}

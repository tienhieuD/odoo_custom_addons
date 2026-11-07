# -*- coding: utf-8 -*-
{
    'name': "Web Split View",
    'summary': """Dual-view layout, seamlessly dividing the screen into list and detail sections for CRUD operations.""",
    'author': "DUO-TEK Software Vietnam",
    'support ': 'tienhieu1212@gmail.com',
    'website': "https://apps.odoo.com/apps/modules/browse?author=DUO-TEK%20Software%20Vietnam",
    'license': 'OPL-1',
    'category': 'Extra Tools',
    'version': '15.0.1.0.0',
    'price': 35.00,
    'currency': 'EUR',
    'depends': ['base', 'web', 'web_editor'],
    'data': [
        'data/demo.xml',
        'security/ir.model.access.csv',
        'views/create_view_split_wizard.xml',
        'views/res_config_settings_views.xml',
    ],
    "images": ['static/description/banner.png'],
    'assets': {
        # the html editor of a form shown in the split pane (e.g. the terms of a sales order) fails to start
        # without a toolbar element: the fix is needed in every bundle that ships the wysiwyg
        'website.assets_wysiwyg': [
            'web_split_view/static/src/js/fix_wysiwyg.js',
        ],
        'web_editor.assets_wysiwyg': [
            'web_split_view/static/src/js/fix_wysiwyg.js',
        ],
        'web.assets_qweb': [
            'web_split_view/static/src/xml/**/*',
        ],
        'web.assets_tests': [
            'web_split_view/static/tests/tours/**/*',
        ],
        'web.assets_backend': [
            'web_split_view/static/src/scss/split_view.scss',
            'web_split_view/static/src/js/split_listview.js',
            'web_split_view/static/src/js/split_formview.js',
            'web_split_view/static/src/js/split_view.js',
            'web_split_view/static/src/js/debug_items.js',
        ],
    },
    'uninstall_hook': '_uninstall_hook',
    'description': """
Web Split View
==============
Adds a "Split" mode to the view switcher of every window action that has a list and a form view:
the screen is divided into a list on the left and the form of the selected record on the right, so
records can be browsed, created, edited and deleted without leaving the list. Nothing to configure:
the split view is derived from the action (its list, form and search views).

Features:
- Resizable list / form panes (the width is remembered for each action)
- Create, edit, save, discard and delete from the right pane; the list refreshes automatically
- An expand button opens the record in the normal full form view; coming back restores the split view
- The record shown on the right is reopened after a page reload
- Settings > Split View switches the automatic mode on/off; a window action can opt out (No split view)
- Explicit <split> views and debug menu entries to add / remove a custom split view on an action
    """,
}

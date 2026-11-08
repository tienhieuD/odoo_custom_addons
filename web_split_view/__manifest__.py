# -*- coding: utf-8 -*-
{
    'name': "Web Split View",
    'summary': """Dual-view layout, seamlessly dividing the screen into list and detail sections for CRUD operations.""",
    'author': "DUO-TEK Software Vietnam",
    'website': 'https://duotek.io.vn',
    'support': 'hello@duotek.io.vn',
    'license': 'OPL-1',
    'category': 'Extra Tools',
    'version': '14.0.1.0.0',
    'depends': ['web'],
    'data': [
        'views/assets.xml',
        'views/res_config_settings_views.xml',
    ],
    'qweb': ['static/src/xml/split_view.xml'],
    "images": ['static/description/banner.png'],
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
- Explicit <split> views (list_view_ref / form_view_ref or inline) for a custom split view on an action
    """,
}

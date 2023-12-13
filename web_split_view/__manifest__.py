# -*- coding: utf-8 -*-
{
    'name': "Web Split View",
    'summary': """Dual-view layout, seamlessly dividing the screen into list and detail sections for CRUD operations.""",
    'author': "DUO-TEK Software Vietnam",
    'support ': 'tienhieu1212@gmail.com',
    'website': "https://apps.odoo.com/apps/modules/browse?author=DUO-TEK%20Software%20Vietnam",
    'license': 'LGPL-3',
    'category': 'Technical',
    'version': '15.0.0',
    'price': 200,
    'currency': 'EUR',
    'depends': ['base', 'web', 'web_editor'],
    'data': [
        'data/demo.xml',
        'security/ir.model.access.csv',
        'views/create_view_split_wizard.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'web_split_view/static/src/xml/**/*',
        ],
        'web.assets_backend': [
            'web_split_view/static/src/scss/split_view.scss',
            'web_split_view/static/src/js/fix_wysiwyg.js',
            'web_split_view/static/src/js/split_listview.js',
            'web_split_view/static/src/js/split_formview.js',
            'web_split_view/static/src/js/split_view.js',
            'web_split_view/static/src/js/debug_items.js',
        ],
    },
    'uninstall_hook': '_uninstall_hook',
    'description': """
        The "Web Split View" is an add-on for the Odoo framework designed to enhance the user interface and user
        experience by introducing a new custom view. The primary purpose of this add-on is to provide a split-screen
        view, dividing the interface into two distinct sections: a list view and a detail form view.
        
        Key Features:
        
        1. Split-Screen Interface:
            The add-on introduces a split-screen interface, allowing users to simultaneously view a list of items
            and the detailed information of a selected item.
        2. List View:
            The list view presents a comprehensive list of items, enabling users to quickly scan and identify the
            items they are interested in.
        3. Detail Form View:
            The detail form view displays in-depth information about a selected item. It provides a closer look at
            the details, attributes, and related information associated with the chosen item.
        4. Interactive Selection:
            Users have the ability to interactively select items from the list view, triggering the display of
            corresponding details in the adjacent form view.
        5. Create, Edit, Delete Functionality:
            The detail form view supports essential CRUD (Create, Read, Update, Delete) operations. Users can create
            new items, edit existing ones, and delete items directly from the detail form view.
        6. Enhanced User Productivity:
            The Web Split View aims to enhance user productivity by streamlining the workflow. Users can efficiently
            navigate between the list view and detail form view to manage and interact with data.
        7. Customizable and Flexible:
            The add-on is designed with customization in mind, providing flexibility for developers and administrators
            to adapt the split view functionality to meet specific business requirements.
        8. Seamless Integration with Odoo:
            As an Odoo add-on, Web Split View seamlessly integrates into the Odoo framework, leveraging its robust
            features and maintaining consistency with the overall Odoo user experience.
        
        Overall, the Web Split View add-on brings a modern and intuitive interface to Odoo, facilitating a more
        efficient and enjoyable user interaction with data through the innovative split-screen design.
    """,
}

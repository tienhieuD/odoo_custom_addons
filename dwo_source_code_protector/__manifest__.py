{
    'name': 'Source Code Protector',
    'version': '20.0.2.0.0',
    'summary': 'Protect your Odoo module source code: compile business logic to native binaries',
    'description': 'Upload a module .zip and get back the same module with its business logic '
                    'compiled to native binaries. Requires the jprotect and pyzipper Python '
                    'packages, and a C compiler with Python headers on the server for Cython.',
    'category': 'Tools',
    'author': 'DUO-TEK Software Vietnam',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=DUO-TEK%20Software%20Vietnam',
    'license': 'OPL-1',
    'depends': ['base', 'base_setup', 'bus'],
    'price': 100.00,
    'currency': 'EUR',
    'support': 'tienhieu1212@gmail.com',
    'external_dependencies': {
        'python': ['jprotect', 'pyzipper'],
    },
    'data': [
        'security/ir.access.csv',
        'wizards/protect_source_wizard_views.xml',
        'views/dwo_protect_job_views.xml',
        'views/res_config_settings_views.xml',
        'data/ir_cron_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dwo_source_code_protector/static/src/js/protect_job_notifications.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
}

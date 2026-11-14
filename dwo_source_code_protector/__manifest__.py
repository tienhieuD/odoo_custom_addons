{
    'name': 'Source Code Protector',
    'version': '12.0.2.1.2',
    'summary': 'Protect your Odoo module source code: compile business logic to native binaries',
    'description': 'Upload a module .zip and get back the same module with its business logic '
                    'compiled to native binaries. Requires the jprotect and pyzipper Python '
                    'packages, and a C compiler with Python headers on the server for Cython.',
    'category': 'Extra Tools',
    'author': 'DUO-TEK Software Vietnam',
    'website': 'https://duotek.io.vn',
    'license': 'OPL-1',
    'depends': ['base', 'base_setup'],
    'price': 100.00,
    'currency': 'EUR',
    'support': 'hello@duotek.io.vn',
    'external_dependencies': {
        'python': ['jprotect', 'pyzipper'],
    },
    'data': [
        'security/ir.model.access.csv',
        'wizards/protect_source_wizard_views.xml',
        'views/dwo_protect_job_views.xml',
        'views/res_config_settings_views.xml',
        'data/ir_cron_data.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
}

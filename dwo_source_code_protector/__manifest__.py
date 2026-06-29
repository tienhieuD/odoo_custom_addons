{
    'name': 'Source Code Protector',
    'version': '18.0.1.0.0',
    'summary': 'Protect & compile your Odoo module source code in one click',
    'description': """
Source Code Protector
=====================
Upload an Odoo module .zip, protect its business logic, compile it to native
binaries, and download a ready-to-ship protected module — all from the UI.
""",
    'category': 'Tools',
    'author': 'DUO-TEK Software Vietnam',
    'website': 'https://github.com/your-org/jprotect',
    'license': 'OPL-1',
    'depends': ['base'],
    'price': 100.00,
    'currency': 'EUR',
    'external_dependencies': {
        'python': ['jprotect', 'pyzipper'],
    },
    'data': [
        'security/ir.model.access.csv',
        'wizards/protect_source_wizard_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
}

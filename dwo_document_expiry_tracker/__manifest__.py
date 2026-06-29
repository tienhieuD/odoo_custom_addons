{
    'name': 'Document Expiry Tracker',
    'version': '17.0.3.0.0',
    'category': 'Tools',
    'author': 'DUO-TEK Software Vietnam',
    'website': 'https://dwo.marketplace/document-expiry',
    'license': 'OPL-1',
    'summary': 'Simple expiry rule and notification tracker',
    'description': '''
Document Expiry Tracker
=======================

Universal expiry automation for any Odoo model.

Features:
---------
* Configure expiry rules by model and domain
* Support field-based and custom date mode
* Notify users by Odoo bus or email
* Dashboard with tracked upcoming/expired records
* Form-view warning and user dismiss/mute controls
* Cron scanning with retention cleanup by autovacuum

Use Cases:
----------
* Contract renewal reminders
* License and certification tracking
* Compliance and audit readiness
* Document lifecycle governance

Support & Demo:
---------------
See feature tour at https://dwo.marketplace/document-expiry
    ''',
    'depends': ['base', 'web', 'mail', 'bus'],
    'data': [
        'security/expiry_security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/expiry_rule_views.xml',
        'views/expiry_record_views.xml',
        'views/expiry_user_views.xml',
        'views/expiry_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dwo_document_expiry_tracker/static/src/js/form_expiry_alerts.js',
        ],
        'web.tests_assets': [
            'dwo_document_expiry_tracker/static/tests/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'price': 129.00,
    'currency': 'EUR',
}

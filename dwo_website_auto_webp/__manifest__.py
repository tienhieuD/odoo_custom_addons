{
    'name': 'Website Auto WebP',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Automatically serve all /web/image URLs as WebP for supporting browsers — zero config, built-in cache.',
    'description': """
Auto WebP Image Conversion for Odoo 18
=======================================
Automatically converts every /web/image response to WebP format for browsers that support it.
WebP files are 25–35% smaller than JPEG/PNG with the same visual quality.

Features:
- Zero configuration — install and it just works
- Built-in ir.attachment cache — converts once, serves instantly after
- Per-website toggle (enable/disable per website)
- Auto-vacuum: cached WebP files removed when source record is deleted
- Safe fallback: non-WebP browsers receive original images unchanged
- Supports JPEG, PNG, BMP, TIFF → WebP
- SVG and already-WebP images are skipped automatically
    """,
    'author': 'DUO-TEK Software Vietnam',
    'website': 'https://apps.odoo.com/apps/modules/browse?author=DUO-TEK%20Software%20Vietnam',
    'license': 'OPL-1',
    'depends': ['web', 'website'],
    'data': [
        'views/website_config_views.xml',
    ],
    'images': ['static/description/banner.png', 'static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'price': 36.00,
    'currency': 'EUR',
}

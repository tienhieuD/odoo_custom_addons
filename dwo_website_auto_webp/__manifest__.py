{
    'name': 'Website Auto WebP',
    'version': '16.0.1.0.0',
    'category': 'Website',
    'summary': 'Automatically serve all /web/image URLs as WebP for supporting browsers — zero config, built-in cache.',
    'description': """
Auto WebP Image Conversion for Odoo
===================================
Automatically converts every /web/image response to WebP format for browsers that support it.
WebP files are 25–35% smaller than JPEG/PNG with the same visual quality.

Features:
- Zero configuration — install and it just works
- Built-in ir.attachment cache — converts once, serves instantly after
- Per-website toggle (enable/disable per website)
- Auto-vacuum: cached WebP files removed when source record is deleted
- Safe fallback: non-WebP browsers receive original images unchanged
- Supports JPEG, PNG, BMP, TIFF → WebP
- SVG, GIF (may be animated) and already-WebP images are skipped automatically

Requirements: Pillow with the WebP encoder (libwebp) on the Odoo server. A built-in test checks it for you.
    """,
    'author': 'DUO-TEK Software Vietnam',
    'website': 'https://duotek.io.vn',
    'support': 'hello@duotek.io.vn',
    'license': 'OPL-1',
    'depends': ['web', 'website'],
    'data': [
        'views/website_config_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'price': 17.00,
    'currency': 'EUR',
}

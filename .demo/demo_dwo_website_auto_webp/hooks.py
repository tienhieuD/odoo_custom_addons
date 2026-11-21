# -*- coding: utf-8 -*-
"""Creates large generated pictures and a public page that shows them (the home page of the demo website)."""
import io
import random

from PIL import Image, ImageDraw, ImageFilter

PICTURES = [("Mountain lake (PNG)", "PNG", (1800, 1000), 3), ("City at dusk (JPEG)", "JPEG", (1800, 1000), 11),
            ("Autumn field (PNG)", "PNG", (1800, 1000), 23)]
PALETTES = [((20, 60, 110), (240, 170, 90)), ((40, 20, 80), (250, 120, 100)), ((30, 90, 50), (240, 200, 80))]


def _picture(size, seed, palette):
    """A photo-like picture: a sky gradient, soft hills, some light and film grain."""
    rnd = random.Random(seed)
    width, height = size
    top, bottom = palette
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / height
        draw.line([(0, y), (width, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    for layer in range(5):
        base = int(height * (0.45 + layer * 0.1))
        shade = tuple(max(0, int(c * (0.7 - layer * 0.1))) for c in bottom)
        points = [(0, height)] + [(x, base + rnd.randint(-70, 70)) for x in range(0, width + 150, 150)] + [(width, height)]
        draw.polygon(points, fill=shade)
    image = image.filter(ImageFilter.GaussianBlur(6))
    noise = Image.effect_noise(size, 40).convert("RGB")
    return Image.blend(image, noise, 0.12)


def post_init_hook(env):
    Attachment = env["ir.attachment"]
    figures = []
    for index, (title, fmt, size, seed) in enumerate(PICTURES):
        buffer = io.BytesIO()
        _picture(size, seed, PALETTES[index]).save(buffer, fmt, **({"quality": 92} if fmt == "JPEG" else {}))
        raw = buffer.getvalue()
        attachment = Attachment.create({
            "name": "%s.%s" % (title.split(" (")[0].lower().replace(" ", "-"), "jpg" if fmt == "JPEG" else "png"),
            "raw": raw, "public": True, "res_model": "ir.ui.view", "res_id": 0})
        figures.append('<figure class="mb-4"><img class="img img-fluid" src="/web/image/%d" alt="%s"/>'
                       '<figcaption class="text-muted">%s: original %d KB</figcaption></figure>'
                       % (attachment.id, title, title, len(raw) // 1024))
    arch = ('<t name="WebP demo" t-name="website.webp_demo_page"><t t-call="website.layout"><div id="wrap" class="oe_structure container py-4">'
            '<h1>Website Auto WebP</h1>'
            '<p>These pictures are PNG and JPEG on the server. Open the browser developer tools, Network tab, and reload: '
            'the browser receives <b>WebP</b>, a lot smaller. The module converts on the fly and keeps a cache.</p>%s'
            '</div></t></t>') % "".join(figures)
    website = env["website"].search([], limit=1)
    page = env["website.page"].create({
        "name": "WebP demo", "url": "/webp-demo", "type": "qweb", "website_published": True, "is_published": True,
        "website_id": website.id, "arch": arch})
    website.write({"homepage_url": "/webp-demo"})

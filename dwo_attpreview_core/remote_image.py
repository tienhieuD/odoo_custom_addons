# -*- coding: utf-8 -*-
# Copyright 2026 Duotek. Licensed under the GNU Lesser General Public License v3.0 (LGPL-3).
"""Fetch a remote picture of an email or text file on behalf of the user (the image proxy, #79, #87).

The browser of the user never calls the outside world: the Odoo server downloads the picture and sends it back,
so the address, location, browser and cookies of the user stay private. The URL comes from an email written by
anyone, so the download is guarded against server-side request forgery (SSRF):

- only ``https`` (and ``http`` when allowed), default ports only, no user name or password in the URL;
- the host name is resolved here and EVERY address must be a public internet address (no loopback, private,
  link-local / cloud metadata, multicast or reserved range); the connection goes to that checked address, so a
  second DNS answer cannot point it elsewhere (no DNS rebinding);
- redirects are followed by hand (at most 3) and each target is checked again;
- an address that ends like a program or script (``.exe``, ``.sh``, ``.js``...) is refused before any download;
- no cookie, no referer, short timeouts, at most 5 MB read;
- the answer must be a PNG, JPEG, GIF or WebP picture; it is decoded and encoded again with Pillow (SVG and
  anything else refused), so only clean pixels reach the browser.
"""
import io
import ipaddress
import socket
import time
from collections import OrderedDict
from urllib.parse import urljoin, urlsplit

import urllib3
from PIL import Image

MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 40_000_000
MAX_REDIRECTS = 3
TIMEOUT = urllib3.Timeout(connect=3.0, read=5.0)
FORMATS = {"PNG": "image/png", "JPEG": "image/jpeg", "GIF": "image/gif", "WEBP": "image/webp"}
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; image-proxy)", "Accept": "image/avif,image/webp,image/png,image/*;q=0.8"}


# endings that can never be a picture: refused without a download (the real check is the content, see clean_picture)
BLOCKED_ENDINGS = (".exe", ".sh", ".bat", ".cmd", ".com", ".msi", ".dll", ".scr", ".ps1", ".vbs", ".js", ".mjs", ".jar",
                   ".apk", ".dmg", ".app", ".bin", ".run", ".svg", ".zip", ".rar", ".7z", ".gz", ".tar", ".pdf", ".doc", ".docx", ".xls", ".xlsx")


class RemoteImageError(ValueError):
    """The picture cannot be fetched (refused address, not a picture, too large, network error).

    ``str(error)`` is a short fixed reason (the viewer turns it into a sentence for the user)."""


def resolve(host, port):
    """The public addresses of ``host``; refuses the host when ANY of its addresses is not public."""
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except (socket.gaierror, UnicodeError, ValueError) as e:
        raise RemoteImageError("host not found") from e
    addresses = []
    for info in infos:
        ip = ipaddress.ip_address(info[4][0].split("%")[0])
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        if not ip.is_global or ip.is_multicast or ip.is_reserved or ip.is_loopback or ip.is_link_local or ip.is_private:
            raise RemoteImageError("address not allowed")
        addresses.append(str(ip))
    if not addresses:
        raise RemoteImageError("host not found")
    return addresses


def check_url(url, https_only=True):
    """``(scheme, host, port, path_with_query)`` of an allowed URL, else ``RemoteImageError``."""
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as e:
        raise RemoteImageError("bad address") from e
    scheme = (parts.scheme or "").lower()
    if scheme not in (("https",) if https_only else ("https", "http")):
        raise RemoteImageError("scheme not allowed")
    if parts.username or parts.password or not parts.hostname:
        raise RemoteImageError("bad address")
    default = 443 if scheme == "https" else 80
    if port not in (None, default):
        raise RemoteImageError("port not allowed")
    path = parts.path or "/"
    if path.lower().endswith(BLOCKED_ENDINGS):
        raise RemoteImageError("not a picture")
    if parts.query:
        path += "?" + parts.query
    return scheme, parts.hostname, default, path


def _get(scheme, host, port, path, address):
    """One GET to the checked ``address``, with the real host name for Host and TLS (SNI + certificate)."""
    headers = dict(HEADERS, Host=host if port in (80, 443) else "%s:%s" % (host, port))
    if scheme == "https":
        pool = urllib3.HTTPSConnectionPool(address, port, server_hostname=host, assert_hostname=host,
                                           cert_reqs="CERT_REQUIRED", timeout=TIMEOUT, retries=False, maxsize=1)
    else:
        pool = urllib3.HTTPConnectionPool(address, port, timeout=TIMEOUT, retries=False, maxsize=1)
    try:
        response = pool.urlopen("GET", path, headers=headers, redirect=False, preload_content=False,
                                assert_same_host=False)
        try:
            if response.status in (301, 302, 303, 307, 308):
                return response.status, response.headers.get("Location"), b""
            if response.status != 200:
                raise RemoteImageError("http %s" % response.status)
            body = response.read(MAX_BYTES + 1, decode_content=True)
            if len(body) > MAX_BYTES:
                raise RemoteImageError("picture too large")
            return 200, None, body
        finally:
            response.release_conn()
    except urllib3.exceptions.HTTPError as e:
        raise RemoteImageError("network error") from e
    finally:
        pool.close()


def clean_picture(body):
    """Decode and encode again: ``(bytes, mimetype)`` of a PNG/JPEG/GIF/WebP picture, else ``RemoteImageError``."""
    try:
        with Image.open(io.BytesIO(body)) as img:
            fmt = img.format
            if fmt not in FORMATS:
                raise RemoteImageError("not a picture")
            if img.width * img.height > MAX_PIXELS:
                raise RemoteImageError("picture too large")
            img.load()  # first frame only: an animated picture becomes still
            out = io.BytesIO()
            if fmt == "JPEG":
                img.convert("RGB").save(out, "JPEG", quality=90)
                return out.getvalue(), "image/jpeg"
            if img.mode not in ("RGB", "RGBA", "L", "LA", "P"):
                img = img.convert("RGBA")
            img.save(out, "PNG")
            return out.getvalue(), "image/png"
    except RemoteImageError:
        raise
    except Exception as e:  # noqa: BLE001 - Pillow raises many kinds of errors on damaged or hostile data
        raise RemoteImageError("not a picture") from e


def fetch_picture(url, https_only=True):
    """``(bytes, mimetype)`` of the clean picture at ``url`` (see the module docstring for the guards)."""
    for _hop in range(MAX_REDIRECTS + 1):
        scheme, host, port, path = check_url(url, https_only)
        address = resolve(host, port)[0]
        status, location, body = _get(scheme, host, port, path, address)
        if status == 200:
            return clean_picture(body)
        if not location:
            raise RemoteImageError("bad redirect")
        url = urljoin(url, location)
    raise RemoteImageError("too many redirects")


class _Cache:
    """Small in-memory cache of fetched pictures (per server process), so a reopened email does not download them
    again. Failures are kept for a short time too."""

    def __init__(self, max_items=200, max_bytes=40 * 1024 * 1024, ttl=3600, error_ttl=300):
        self.items, self.size = OrderedDict(), 0
        self.max_items, self.max_bytes, self.ttl, self.error_ttl = max_items, max_bytes, ttl, error_ttl

    def get(self, key):
        item = self.items.get(key)
        if item is None:
            return None
        expires, value = item
        if expires < time.time():
            self._drop(key)
            return None
        self.items.move_to_end(key)
        return value

    def put(self, key, value, error=False):
        self._drop(key)
        size = len(value[0]) if not error else 0
        self.items[key] = (time.time() + (self.error_ttl if error else self.ttl), value)
        self.size += size
        while len(self.items) > self.max_items or self.size > self.max_bytes:
            self._drop(next(iter(self.items)))

    def _drop(self, key):
        item = self.items.pop(key, None)
        if item is not None and isinstance(item[1], tuple):
            self.size -= len(item[1][0])

    def clear(self):
        self.items.clear()
        self.size = 0


CACHE = _Cache()


def cached_picture(url, https_only=True, fetch=None):
    """``fetch_picture`` with the cache. Raises ``RemoteImageError`` (also for a cached failure)."""
    key = (url, https_only)
    hit = CACHE.get(key)
    if isinstance(hit, tuple):
        return hit
    if isinstance(hit, str):
        raise RemoteImageError(hit)
    try:
        value = (fetch or fetch_picture)(url, https_only)
    except RemoteImageError as e:
        CACHE.items[key] = (time.time() + CACHE.error_ttl, str(e))
        raise
    CACHE.put(key, value)
    return value


# --- pictures with a strange address (#87) -------------------------------------------------------------------------
# html_sanitize silently drops a bad ``src`` (``javascript:``, a script, a path...): before it runs, such a picture is
# swapped for a text token (it survives the sanitizer), and the token becomes a visible error marker afterwards.
import html as _html
import re as _re

_IMG_TAG = _re.compile(r"<img\b[^>]*>", _re.I)
_SRC_ATTR = _re.compile(r"""\ssrc\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", _re.I)
_ALT_ATTR = _re.compile(r"""\salt\s*=\s*(?:"([^"]*)"|'([^']*)')""", _re.I)
_TOKEN = _re.compile(r"DWOBADIMG(\d+)X")
MAX_BAD_MARKERS = 100


def mark_bad_images(html):
    """``(html, alts)``: each ``<img>`` whose address is not http(s), ``data:image`` or ``cid:`` (and not empty) is
    replaced by the token ``DWOBADIMG<n>X``; ``alts[n]`` is its alt text."""
    alts = []

    def swap(match):
        tag = match.group(0)
        src = _SRC_ATTR.search(tag)
        if not src:
            return tag
        value = _html.unescape(next(g for g in src.groups() if g is not None)).strip().lower()
        if not value or value.startswith(("http://", "https://", "data:image/", "cid:")) or len(alts) >= MAX_BAD_MARKERS:
            return tag
        alt = _ALT_ATTR.search(tag)
        alts.append(_html.unescape(next((g for g in alt.groups() if g is not None), "")) if alt else "")
        return "DWOBADIMG%dX" % (len(alts) - 1)

    return _IMG_TAG.sub(swap, html), alts


def restore_bad_images(html, alts):
    """The tokens of ``mark_bad_images`` become ``<img data-dwo-bad="unsupported address" hidden alt="...">``."""
    def back(match):
        n = int(match.group(1))
        alt = _html.escape(alts[n], quote=True) if n < len(alts) else ""
        return '<img data-dwo-bad="unsupported address" hidden alt="%s">' % alt

    return _TOKEN.sub(back, html)

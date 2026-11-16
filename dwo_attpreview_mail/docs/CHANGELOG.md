# CHANGELOG - dwo_attpreview_mail

## 2026-11-16 - 17.0.2.1.0 - Remote pictures through the server (#79)

17.0 port of 19.0.2.1.0: remote pictures of an email are downloaded by the Odoo server (image proxy, SSRF-safe),
with the same settings, guards and tests (details in the 19.0.2.1.0 entry below).

**17.0 differences:** `/dwo_attpreview_mail/remote_settings` is `type="json"`; the viewer gets `rpc` from
`useService("rpc")`; tour through `dwoAddTour`, `/web#...` URL. `parsers/remote.py` unchanged (urllib3 2.0.7 /
1.26 and Pillow 10 of Odoo 17 have the calls it uses). Details in `dwo_attpreview_core/docs/PORTING.md`.

## 2026-11-16 - 17.0.2.0.0 - 17.0 port of 19.0.2.0.0 (via 18.0) (#73)

- Same features and behaviour as 19.0.2.0.0 (ported from the 18.0 port); the entries below are the history of the 18.0 and 19.0 series. Needs dwo_attpreview_core 17.0.1.1.0.
- `_()` instead of `env._`. Tests: 17 tour runner, `/web#...` URL. Details in `dwo_attpreview_core/docs/PORTING.md`.

## 2026-11-16 - 18.0.2.0.0 - 18.0 port of 19.0.2.0.0 (#73)

- Same features and behaviour as 19.0.2.0.0; the entries below are the history of the 19.0 series. Needs dwo_attpreview_core 18.0.1.1.0.
- No code change; tour only: chatter file cards are `.o-mail-AttachmentCard`. Details in `dwo_attpreview_core/docs/PORTING.md`.

## 2026-11-16 - 19.0.2.1.0 - Remote pictures through the server (#79)

**Added:** pictures that an email links from the internet are downloaded by the Odoo server and shown from there
(image proxy). The browser of the user never contacts the sender's servers: the IP address, location, browser and
cookies of the user stay private. The sender can still see that the email was opened, from the server's address.
- Settings > Attachment Preview > Email preview: "Load remote pictures through the server" and "Only secure (HTTPS)
  pictures", both on by default (`ir.config_parameter` `dwo_attpreview_mail.remote_images` /
  `.remote_https_only`, data file `noupdate`). Off: pictures stay blocked, with a "Load them through the server"
  button per email.
- Engine (version 3): each `<img src="http(s)://...">` of the sanitized body becomes `<img data-dwo-remote="N" hidden>`
  (no address in the page); `remote_images` / `remote_insecure` counts in the result. Source sets, backgrounds and
  CSS `url()` stay removed.
- Route `/dwo_attpreview_mail/remote_image?<source_ref>&path=&index=N` (auth user): checks the access to the email
  like `/part_info`, takes the address from the email itself (the browser only sends a position, so it is no open
  proxy) and downloads it with `parsers/remote.py`: http(s) only (https only by default), default ports, no user
  info; every resolved address must be public (no loopback, private, link-local / cloud metadata, multicast,
  reserved, IPv4-mapped); connection to the checked address (no DNS rebinding), redirects followed by hand (3) and
  checked again; no cookie or referer; 3 s / 5 s timeouts, 5 MB; decoded and encoded again with Pillow (PNG, JPEG,
  GIF, WebP in; PNG or JPEG out; SVG refused; first frame only); in-memory cache per process (1 h, failures 5 min).
  Answer with `nosniff`, `Content-Security-Policy: default-src 'none'`, `Referrer-Policy: no-referrer`, private cache.
- Viewer: loads the pictures with the session (4 at a time), turns them into `data:` URIs and draws the frame once;
  the frame policy is unchanged (`img-src data:`). Banner: "loaded through your Odoo server" / blocked + button.
- Listing and duotek pages: the sentences "remote pictures blocked / opening tells the sender nothing" replaced by
  "remote pictures load through your server, your IP address stays private"; screenshot 01 taken again.

**Tests:** `tests/test_remote.py` (URL rules, private address ranges incl. one private answer among public ones,
connection to the checked address, redirects to internal or plain http refused, redirect loop, clean pictures only,
cache; engine order of URLs; defaults on; route: position only and extra parameters ignored, headers, https-only
setting, access of the email (portal, public, not an email)); the tour checks the picture is replaced by the proxied one.
Core `test_settings`: an engine module may add its own fields to the Attachment Preview app.

## 2026-11-16 - 19.0.2.0.0 - Secure Email Preview: EML, MSG, ICS, VCF (#78)

Rewritten. Needs dwo_attpreview_core 19.0.1.1.0 (result type `json`, files inside a file, dialog width by kind).
The dialog of an email, invitation or contact card is `medium` (about 1080px) instead of the full width used for
Office files (user feedback on #78).

**Name and price:** `Secure Email Preview: EML, MSG, ICS, VCF`, 30 EUR (was 15), author `Duotek`.

**Formats:** `.eml`, `.emlx` (Apple Mail), `.msg` and `.oft` (Outlook), `.ics`, `.vcf`. The first bytes decide: an
Outlook file renamed `.eml`, or a MIME email saved as `.msg`, still opens. Not in this version: `winmail.dat`
(TNEF, the only library is LGPL), `.mbox`, `.p7m`, `.mht`, `.pst`.

**How it reads (server side, pure Python in `parsers/`, no Odoo code):**
- EML/EMLX: the standard library `email` package (what Odoo uses for incoming mail); unknown charsets and malformed
  headers fall back to a lenient decoding; an attached email (`message/rfc822`) is one attachment (`<subject>.eml`).
- MSG/OFT: an OLE file read with `olefile` 0.47 (BSD-2, shipped unmodified in `thirdparty/olefile/` with its license, no
  pip install), following [MS-OXMSG]: subject, sender (an Exchange address is shown as the name only), recipients,
  dates, plain/HTML/RTF bodies, attachments. 8 bit strings use the message code page, else the code page of the
  message language, else the internet code page; the binary HTML body uses the internet code page first. An
  Outlook message attached to the message becomes an `.eml`. RTF-only bodies are decompressed ([MS-OXRTFCP]) and
  shown as text. msg-parser and extract-msg (GPL) are not used.
- ICS: events (summary, start/end with time zone, location, organizer, attendees with answer, description,
  recurrence, method). VCF 2.1/3.0/4.0: name, organization, title, emails, phones, addresses, birthday, website, note
  (quoted-printable decoded). Photos and binary values are dropped.

**Safety:** the HTML body goes through Odoo's `html_sanitize` (scripts, event handlers, forms, unsafe styles),
then every remaining outside reference is removed (remote pictures, tracking pixels, CSS `url()`; a banner says so);
`cid:` pictures become `data:` URIs (max 3 MB each, 15 MB in all). `bgcolor` and `background` shorthands become
`background-color` first, else coloured table headers lose their colour. The viewer shows the body in a frame
sandboxed without scripts and without same origin, with `Content-Security-Policy: default-src 'none'; img-src data:;
style-src 'unsafe-inline'`; links open in a new tab without referrer. Nothing in the file is executed.

**Viewer** (`static/src/js/mail_viewer.js`, registry `dwo_attpreview.viewers` key `mail`): headers, attachment chips
(Preview opens the attachment in a second, smaller dialog with the engines installed; Download), body; cards for
invitations and contacts. Pictures of the body are not listed again as attachments.

**Tests:** `tests/test_engine.py`: EML headers/attachments/safe body, backgrounds kept and blocked pictures dropped,
bogus charset, malformed headers, garbage refused, EMLX, parts (attached email, nested part), MSG plain, code pages
(Traditional Chinese, Cyrillic HTML), MSG attachments + embedded message, inline pictures, damaged/renamed files,
ICS, VCF, through the Core cache and `/part_info`; tour `dwo_attpreview_mail_tour` (escaped subject, sandbox + CSP,
attachment opens in a second dialog, email dialog is medium width). MSG samples: Apache POI test data (Apache-2.0, `tests/files/NOTICE`).

## 2026-11-15 - #72

- Manifest `description`: "Engine for Secure Attachment Preview (dwo_attpreview_core)." (the core was renamed). Nothing else changed.

## 2026-11-15 - #66

Theo core #66: test dùng `dwo.attpreview.engine._dwo_find_engine` thay cho `dwo.attpreview.engine.config`. Engine không đổi. Mô tả ngắn của engine nằm ở catalog của core (`dwo_attpreview_core/static/catalog/dwo_attpreview_mail/`) vì chưa có `index.html`.

## 2026-11-15 - 19.0.1.0.0 (bản đầu, #58)

**Thêm:** eml (header, body HTML/text, ảnh cid inline dạng data URI, danh sách đính kèm; chặn ảnh/CSS remote, script bị core sanitize), ics, vcf (bảng trường). Chưa có: msg, winmail.dat (cần pip extract-msg/tnefparse).

**Test:** xem `tests/test_engine.py` (chạy trên Odoo 19, DB tạm). Bộ file mẫu được sinh trong test (hợp lệ, hỏng, độc hại); chưa có file mẫu thật/lớn trên đĩa.
**Chưa làm:** listing (`_listings`), icon/banner, duotek, bản dịch vi, kiểm tra fidelity với file thật.

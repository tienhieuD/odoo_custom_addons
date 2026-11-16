# CHANGELOG - dwo_attpreview_mail

## 2026-11-15 - #72

- Manifest `description`: "Engine for Secure Attachment Preview (dwo_attpreview_core)." (the core was renamed). Nothing else changed.

## 2026-11-15 - #66

Theo core #66: test dùng `dwo.attpreview.engine._dwo_find_engine` thay cho `dwo.attpreview.engine.config`. Engine không đổi. Mô tả ngắn của engine nằm ở catalog của core (`dwo_attpreview_core/static/catalog/dwo_attpreview_mail/`) vì chưa có `index.html`.

## 2026-11-15 - 19.0.1.0.0 (bản đầu, #58)

**Thêm:** eml (header, body HTML/text, ảnh cid inline dạng data URI, danh sách đính kèm; chặn ảnh/CSS remote, script bị core sanitize), ics, vcf (bảng trường). Chưa có: msg, winmail.dat (cần pip extract-msg/tnefparse).

**Test:** xem `tests/test_engine.py` (chạy trên Odoo 19, DB tạm). Bộ file mẫu được sinh trong test (hợp lệ, hỏng, độc hại); chưa có file mẫu thật/lớn trên đĩa.
**Chưa làm:** listing (`_listings`), icon/banner, duotek, bản dịch vi, kiểm tra fidelity với file thật.

# Changelog

## 2026-11-14 - search box (14.0.2.0.0, no version bump)
- Search box on the chip row (always visible, placeholder "Search messages..."): searches `body`, `subject`, author name and `email_from`, case-insensitive, 300 ms after the last key, AND with the chosen chip. The x button and Esc clear it; leaving the record resets it.
- Server: like the chip, the text travels inside the domain of `mail.message.message_fetch` as the leaf `("dwo_search", "=", text)`; `dwo_filter_chips(res_model, res_id, search=None)` makes the chip counts follow the text; helper `_dwo_search_domain(text)`. No new field/model/migration.
- JS: `chatter.dwoSearch`, `chatter.dwoSetSearch(text)`; Odoo's own search button is left as it is.
- Tests: `test_search_in_body_subject_author_and_email`, `test_counts_follow_the_search` (green on Odoo 14). No new tour: the tours of this version are skipped here (no browser), so the JS is not run by any test.
- Trade-off: `body` is HTML, so the match is on the stored HTML (a word inside a tag name can match).

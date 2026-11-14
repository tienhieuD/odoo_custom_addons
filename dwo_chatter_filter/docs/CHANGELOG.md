# Changelog

## 2026-11-14 - search box (19.0.2.0.0, no version bump)
- Search box on the chip row (always visible): searches `body`, `subject`, author name and `email_from`, case-insensitive, 300 ms after the last key, AND with the chosen chip. X button and Esc clear it.
- Server: `mail.message._message_fetch(..., dwo_search=)` and `dwo_filter_chips(res_model, res_id, search=None)` (chip counts follow the text); helper `_dwo_search_domain(text)`. No new field/model/migration.
- JS: `thread.dwoSearch`, `thread.dwoSetSearch(text)`; Odoo's own search button is left as it is.
- Tests: `test_search_in_body_subject_author_and_email`, `test_counts_follow_the_search`, tour `dwo_chatter_filter_search` (32 tests green on Odoo 19).
- Trade-off: `body` is HTML, so the match is on the stored HTML (a word inside a tag name can match). No highlight (decided on issue #14).

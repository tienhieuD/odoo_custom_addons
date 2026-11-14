# Changelog

## 2026-11-14 - search box (12.0.2.0.0, no version bump)
- Search box on the chip row (always visible, placeholder "Search messages..."): searches `body`, `subject`, author name and `email_from`, case-insensitive, 300 ms after the last key, AND with the chosen chip. The x button and Esc clear it; leaving or changing the record resets it.
- Server: `mail.message.dwo_filter_ids(res_model, res_id, chip_id, search=None)` returns the ids of the chip and/or the text (the Odoo 12 chatter shows messages by id); `dwo_filter_chips(res_model, res_id, search=None)` makes the chip counts follow the text; helper `_dwo_search_domain(text)`. No new field/model/migration.
- JS: `DocumentThread.dwoSetSearch(text)`; the chips are drawn in their own container so the input keeps its focus; Odoo's own search button is left as it is.
- Tests: `test_search_in_body_subject_author_and_email`, `test_counts_follow_the_search` (green on Odoo 12). No new tour; the JS is not run by a test here (no browser).
- Trade-off: `body` is HTML, so the match is on the stored HTML (a word inside a tag name can match).

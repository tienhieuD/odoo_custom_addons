# Changelog

## 19.0.1.0.0 (2026-11-18)
- New module "Orphan Mail Router" (idea from the market need for routing lost emails; own code, views and images).
- `mail.thread.message_route` is extended: an incoming email with no route (ValueError) or rejected with a catch-all bounce is stored as `dwo.mail.orphan` (HTML sanitized, attachments kept, duplicates by Message-Id ignored). The standard bounce still goes out; if storing fails the standard behaviour is kept.
- Models: `dwo.mail.orphan` (inbox), `dwo.mail.orphan.suggestion` (top 3 targets), `dwo.mail.orphan.rule`, wizard `dwo.mail.orphan.route.wizard` (bulk routing, same sender / same thread), fields `dwo_orphan_all_aliases` and `dwo_orphan_alias_ids` on `res.users`.
- Suggestions: reply headers (In-Reply-To / References), codes of the subject against `name`, `ref`, `number`, `client_order_ref`, `reference`, `partner_ref`, `code`, alias parent record, sender partner and its recent records.
- Routing posts the email in the chatter (`message_post`, same Message-Id, attachments, sender as author); re-routing moves the posted message. Needs write access on the target record (checked as the user).
- Group "Orphan Mail Manager"; record rules by assigned alias; settings: enable, allowed target models, follow sender, daily digest, retention days.
- Cron "daily digest and clean-up": digest mail per manager (mail.mail), purge of routed/ignored emails older than the retention.
- Tests: 25 (TransactionCase). Trade-off: no HttpCase tour; UI checked by hand with Playwright.

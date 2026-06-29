# Document Expiry Tracker — Technical Design Document

> **Module**: `dwo_document_expiry_tracker`
> **Version**: 17.0.3.0.0
> **Odoo Compatibility**: 17.0
> **License**: OPL-1
> **Author**: DUO-TEK Software Vietnam
> **Last Updated**: 2026-04-29

---

## Table of Contents

1. [Overview](#1-overview)
2. [Actors & Roles](#2-actors--roles)
3. [Functional Requirements](#3-functional-requirements)
4. [Features Summary](#4-features-summary)
5. [Architecture & Module Structure](#5-architecture--module-structure)
6. [Data Models](#6-data-models)
7. [Business Logic — Method Reference](#7-business-logic--method-reference)
8. [Security Design](#8-security-design)
9. [Views & UI](#9-views--ui)
10. [JavaScript (Frontend)](#10-javascript-frontend)
11. [Cron & Automation](#11-cron--automation)
12. [Notification Flow](#12-notification-flow)
13. [Anti-Abuse & Throttling](#13-anti-abuse--throttling)
14. [Performance Considerations](#14-performance-considerations)
15. [Test Plan & Test Flow](#15-test-plan--test-flow)
16. [Configuration Guide](#16-configuration-guide)
17. [Known Limitations](#17-known-limitations)
18. [Glossary](#18-glossary)

---

## 1. Overview

**Document Expiry Tracker** is a universal expiry automation module for Odoo 17. It allows administrators and authorized users to define rules that monitor any Odoo model for upcoming or expired records based on datetime fields or fixed datetime values. When conditions are met, the module sends notifications via Odoo bus (in-app), email, and/or form-view popup alerts.

### Core Workflow

```
Rule Configuration → Cron Scan → Expiry Detection → Dashboard Tracking → Notification Dispatch
```

### Key Value Propositions

- **Model-agnostic**: works with any non-transient Odoo model (contacts, contracts, invoices, etc.)
- **Dual date modes**: field-based (dynamic per-record) or custom (fixed datetime for all records)
- **Multi-channel notifications**: bus, email, and form-view alerts
- **Role-based access**: admin full control, custom users self-only, basic users read-only
- **Anti-spam**: throttling, mute, dismiss, and non-admin recipient restrictions
- **Zero configuration for end users**: form alerts work automatically after rule setup

---

## 2. Actors & Roles

| Actor | Odoo Group | Capabilities |
|-------|-----------|--------------|
| **System Administrator** | `base.group_system` | Full CRUD on rules and records. Configure any recipient (users, groups, domains, formulas). Delete rules. Access all menu items. |
| **Custom Expiry User** | `group_expiry_custom_user` (implies `base.group_user`) | Create and manage **own** rules only (record rule enforced). Cannot configure recipients for others — system forces self-only policy. Cannot delete rules. |
| **Internal User** | `base.group_user` | Read-only access to rules and tracked records. Receives form-view alerts and bus notifications. Can mute/dismiss personal notifications. |
| **Portal/Public User** | N/A | No access. Excluded from all notification targets via `share=False` filter. |

### Actor Interaction Matrix

| Action | Admin | Custom User | Internal User |
|--------|-------|-------------|---------------|
| Create rule | ✅ | ✅ (own only) | ❌ |
| Edit rule | ✅ | ✅ (own only) | ❌ |
| Delete rule | ✅ | ❌ | ❌ |
| Run Scan button | ✅ | ✅ (own only) | ❌ |
| Test Notification button | ✅ | ✅ (own only) | ❌ |
| View rules list | ✅ | ✅ (own only) | ✅ (read-only) |
| View tracked records | ✅ | ✅ | ✅ (read-only) |
| Configure recipients | ✅ | ❌ (forced self) | ❌ |
| Receive bus notification | ✅ | ✅ | ✅ |
| Receive form-view alerts | ✅ | ✅ | ✅ |
| Mute notifications | ✅ | ✅ | ✅ |
| Dismiss notifications | ✅ | ✅ | ✅ |

---

## 3. Functional Requirements

### FR-01: Rule Configuration
- Admin can create expiry rules targeting any non-transient Odoo model.
- Each rule belongs to one company and one owner.
- Rules are processed in `sequence` order.

### FR-02: Date Mode — Field Based
- Rule uses a date/datetime field from the target model as the base datetime.
- An offset (days) is added to compute the notification datetime.
- Negative offsets mean "notify N days before the field value".

### FR-03: Date Mode — Custom
- Rule uses a fixed `specific_datetime` value as the notification datetime.
- Offset fields are hidden and ignored in this mode.

### FR-04: Domain Filtering
- Rules include an `additional_domain` to filter which records are scanned.
- Domains are validated using `safe_eval` + `normalize_domain` on save.

### FR-05: Notification Channels
- **Bus**: In-app notification via `bus.bus._sendone` with configurable message template.
- **Email**: Via `mail.template` or fallback `mail.mail` with HTML-escaped body.
- **Form View**: Popup alert when user opens a matching record's form view.

### FR-06: Recipient Resolution
Admin can configure recipients via 5 sources (merged, deduplicated, limited):
1. `notify_to_user_field_id` — relation field on target model pointing to `res.users`
2. `notify_to_user_ids` — explicit M2M list of users
3. `notify_to_notify_group_ids` — users from security groups
4. `notify_to_user_domain` — domain on `res.users`
5. `notify_to_formular` — Python expression returning user IDs

### FR-07: Non-Admin Anti-Spam Policy
- Non-admin users are forced to `rule_user_id = self`, recipients = self only, limit = 1.
- Enforced in both `create()` and `write()`.

### FR-08: Notification Throttling
- Same state + same record: re-notify only after 24 hours.
- State change (upcoming ↔ expired): immediate re-notify.

### FR-09: User Mute & Dismiss
- Users can permanently mute via `expiry_notify_muted` (Boolean).
- Users can temporarily dismiss via `expiry_dismiss_until` (Datetime) with preset durations.
- Both fields are in `SELF_WRITEABLE_FIELDS` so non-admin users can self-manage.

### FR-10: Dashboard
- Tracked records table (`dwo.expiry.record`) with tree/form/pivot/graph views.
- "Open Record" button navigates to the source business record (with access check).

### FR-11: Retention Cleanup
- `@api.autovacuum` deletes tracked records older than 30 days in batches of 1000.

### FR-12: Test Notification
- "Test Notification" button on rule form sends a sample bus notification to the current user.

---

## 4. Features Summary

| # | Feature | Channel | Trigger |
|---|---------|---------|---------|
| 1 | Cron-based expiry scan | — | Every 15 minutes (configurable) |
| 2 | Bus notification | In-app | Cron scan / Manual scan |
| 3 | Email notification | Email | Cron scan / Manual scan |
| 4 | Form-view popup alert | JS popup | User opens matching record |
| 5 | Summarized notification | JS popup | Multiple alerts → 1 message |
| 6 | Dismiss buttons | JS popup | User clicks dismiss (5min–30d) |
| 7 | "View All" button | JS popup | Opens tracked records list |
| 8 | Test Notification button | In-app | Admin clicks button on rule form |
| 9 | Manual "Run Scan" button | — | Admin clicks button on rule form |
| 10 | Dashboard (pivot/graph) | UI | Navigate to tracked records |
| 11 | Autovacuum cleanup | — | Odoo autovacuum cron |
| 12 | User mute/dismiss prefs | UI | User profile settings |

---

## 5. Architecture & Module Structure

```
dwo_document_expiry_tracker/
├── __init__.py                          # Package init → imports models/
├── __manifest__.py                      # Module metadata, dependencies, assets
├── data/
│   └── ir_cron.xml                      # Cron job: scan every 15 minutes
├── docs/
│   └── DESIGN.md                        # This document
├── models/
│   ├── __init__.py                      # Imports: expiry_rule, expiry_record, res_users
│   ├── expiry_rule.py                   # Core rule engine (~720 lines)
│   ├── expiry_record.py                 # Dashboard tracked records (~65 lines)
│   └── res_users.py                     # User mute/dismiss preferences (~76 lines)
├── security/
│   ├── expiry_security.xml              # Groups, categories, record rules
│   └── ir.model.access.csv             # Access rights matrix
├── static/
│   ├── src/js/
│   │   └── form_expiry_alerts.js        # FormController patch for popup alerts (~131 lines)
│   └── tests/
│       └── form_expiry_alerts_tests.js  # QUnit JS tests (~6 tests)
├── tests/
│   ├── __init__.py
│   └── test_expiry_rule_engine.py       # Python unit tests (27 tests, ~415 lines)
└── views/
    ├── expiry_menu.xml                  # Top-level menu and sub-menus
    ├── expiry_rule_views.xml            # Rule tree/form/search + window action
    ├── expiry_record_views.xml          # Record tree/form/search/pivot/graph + window action
    └── expiry_user_views.xml            # Inherited user form views (simple + full)
```

### Dependencies

| Module | Purpose |
|--------|---------|
| `base` | Core Odoo models (`ir.model`, `ir.model.fields`, `res.users`, `res.company`) |
| `web` | Frontend assets bundle (`web.assets_backend`) |
| `mail` | Mail thread, mail template, mail.mail for email sending |
| `bus` | `bus.bus._sendone` for real-time in-app notifications |

---

## 6. Data Models

### 6.1 `dwo.expiry.rule` — Expiry Rule

**Inherits**: `mail.thread`, `mail.activity.mixin`
**Order**: `sequence asc, id asc`
**SQL Constraints**: `unique(name, company_id)`

#### Fields

| Field | Type | Required | Default | Indexed | Description |
|-------|------|----------|---------|---------|-------------|
| `name` | Char | ✅ | — | ✅ | Rule display name. Tracked. |
| `active` | Boolean | — | `True` | ✅ | Archive toggle. |
| `sequence` | Integer | — | `10` | ✅ | Processing order (lower = first). |
| `company_id` | Many2one → `res.company` | ✅ | Current company | ✅ | Company scope. |
| `rule_user_id` | Many2one → `res.users` | ✅ | Current user | ✅ | Rule owner. Auto-set for non-admins. |
| `description` | Text | — | — | — | Business purpose description. |
| `model_id` | Many2one → `ir.model` | ✅ | — | ✅ | Target model. Domain: `transient=False`. Tracked. |
| `model_name` | Char | — | Related (`model_id.model`) | ✅ | Stored technical model name. |
| `additional_domain` | Text | ✅ | `"[]"` | — | Domain filter for record scanning. Validated by `safe_eval`. |
| `date_mode` | Selection | ✅ | `"field_based"` | — | `field_based` or `custom`. Tracked. |
| `datetime_field_id` | Many2one → `ir.model.fields` | — | — | — | Source datetime field (field-based mode). Domain: date/datetime fields of target model. |
| `specific_datetime` | Datetime | — | — | — | Fixed notification datetime (custom mode). |
| `expired_after_year` | Integer | — | `0` | — | Year offset. Supports negative. |
| `expired_after_month` | Integer | — | `0` | — | Month offset. Supports negative. |
| `expired_after_day` | Integer | — | `0` | — | Day offset. Supports negative. Shown inline in form. |
| `expired_after_hour` | Integer | — | `0` | — | Hour offset. Supports negative. |
| `expired_after_minute` | Integer | — | `0` | — | Minute offset. Supports negative. |
| `total_expired_after_minutes` | Integer | — | Computed | ✅ | `= years*525600 + months*43200 + days*1440 + hours*60 + minutes`. Stored. |
| `notify_on_form_view` | Boolean | — | `True` | — | Enable JS form-view popup alerts. |
| `notify_bus` | Boolean | — | `True` | — | Enable bus notifications during scan. |
| `notify_bus_template` | Text | — | `"[{rule_name}] ..."` | — | Template with `{placeholder}` and `${expr}` support. |
| `notify_email` | Boolean | — | `False` | — | Enable email notifications during scan. |
| `notify_email_template` | Many2one → `mail.template` | — | — | — | Optional. Must match rule model. |
| `notify_to_user_field_id` | Many2one → `ir.model.fields` | — | — | — | Relation field → `res.users` on target model. Admin only. |
| `notify_to_user_ids` | Many2many → `res.users` | — | — | — | Explicit user list. Admin only. |
| `notify_to_notify_group_ids` | Many2many → `res.groups` | — | — | — | Security groups. Admin only. |
| `notify_to_user_domain` | Text | — | `"[]"` | — | Domain on `res.users`. Admin only. |
| `notify_to_formular` | Char | — | — | — | Python expression. Admin only. |
| `limit_record` | Integer | — | `1000` | — | Max records per scan. 0 or negative = no limit. |
| `limit_notify_user` | Integer | — | `200` | — | Max users per notification. 0 or negative = no limit. |
| `last_run_at` | Datetime | — | — | — | Readonly. Updated after each scan. |
| `last_run_summary` | Char | — | — | — | Readonly. E.g. "Processed 150 records, tracked 42." |

### 6.2 `dwo.expiry.record` — Tracked Expiry Record

**Order**: `expiry_datetime asc, id asc`
**Rec Name**: `record_name`
**SQL Constraints**: `unique(rule_id, model, res_id)`

| Field | Type | Required | Indexed | Description |
|-------|------|----------|---------|-------------|
| `state` | Selection (`upcoming`/`expired`) | ✅ | ✅ | Current expiry state. |
| `record_name` | Char | ✅ | — | Source record `display_name` snapshot. |
| `expiry_field_id` | Many2one → `ir.model.fields` | — | — | Source field (field-based mode only). |
| `expiry_datetime` | Datetime | ✅ | ✅ | Computed notification datetime. |
| `rule_id` | Many2one → `dwo.expiry.rule` | ✅ | ✅ | Parent rule. Cascade delete. |
| `rule_user_id` | Many2one → `res.users` | — | ✅ | Related stored from `rule_id.rule_user_id`. |
| `model` | Char | ✅ | ✅ | Source model technical name. |
| `res_id` | Integer | ✅ | ✅ | Source record ID. |
| `company_id` | Many2one → `res.company` | ✅ | ✅ | Company scope. |
| `last_seen_at` | Datetime | ✅ | — | Last scan observation time. |
| `last_notified_at` | Datetime | — | — | Last notification dispatch time. |
| `last_notified_state` | Selection (`upcoming`/`expired`) | — | — | State at last notification. Used for throttling. |

### 6.3 `res.users` — User Preferences (Inherited)

| Field | Type | Default | Self-Writable | Description |
|-------|------|---------|---------------|-------------|
| `expiry_notify_muted` | Boolean | `False` | ✅ | Permanently mute all expiry notifications. |
| `expiry_dismiss_until` | Datetime | — | ✅ | Temporarily suppress until this datetime. |
| `expiry_access_alert_mute` | Boolean (related) | — | — | Legacy alias → `expiry_notify_muted`. |
| `expiry_access_alert_dismiss_until` | Datetime (related) | — | — | Legacy alias → `expiry_dismiss_until`. |
| `expiry_access_alert_mode` | Selection | `"summary"` | — | Legacy compatibility. Not used by current logic. |
| `expiry_access_alert_limit` | Integer | `20` | — | Legacy compatibility. Not used by current logic. |
| `expiry_access_alert_ignore_until` | Datetime (related) | — | — | Legacy alias → `expiry_dismiss_until`. |

**`SELF_WRITEABLE_FIELDS`**: `["expiry_notify_muted", "expiry_dismiss_until"]`
This allows non-admin users to toggle mute and set dismiss-until on their own profile without `sudo()`.

---

## 7. Business Logic — Method Reference

### 7.1 `dwo.expiry.rule` Methods

| Method | Decorator | Description |
|--------|-----------|-------------|
| `_compute_total_expired_after_minutes()` | `@api.depends(...)` | Converts year/month/day/hour/minute offsets to total minutes. Stored computed field. |
| `_check_datetime_field()` | `@api.constrains(...)` | Validates: field-based requires `datetime_field_id`; custom requires `specific_datetime`. |
| `_check_domains()` | `@api.constrains(...)` | Validates `additional_domain` and `notify_to_user_domain` via `safe_eval`. |
| `_check_email_template_model()` | `@api.constrains(...)` | Ensures email template targets same model as rule. |
| `_check_notify_user_field_relation()` | `@api.constrains(...)` | Ensures notify field is m2o/m2m/o2m with `relation='res.users'`. |
| `create(vals_list)` | `@api.model_create_multi` | Applies `_enforce_non_admin_policy` before super. |
| `write(vals)` | — | Applies `_enforce_non_admin_policy` before super. |
| `_enforce_non_admin_policy(vals)` | — | Forces self-only recipients for non-admin users. |
| `_safe_eval_domain(domain_text, ...)` | — | `safe_eval` + `normalize_domain`. Context: `uid`, `user`, `today`, `now`, `object`. |
| `_safe_eval_formula_user_ids(record)` | — | Evaluates `notify_to_formular` expression → `res.users` recordset. |
| `_resolve_users_from_field(record)` | — | Reads m2o/m2m/o2m `res.users` value from target record. |
| `_collect_target_users(record)` | — | Merges all 5 recipient sources → dedup → filter active non-share → limit. |
| `_compute_expiry_datetime(record)` | — | Custom mode: returns `specific_datetime`. Field-based: returns `field_value + offset`. |
| `_record_matches_additional_domain(record)` | — | Re-checks if record matches domain (used in form alerts). |
| `_render_template(template, record, state, dt)` | — | Replaces `${expr}` via `safe_eval` then `{placeholder}` via `.format()`. |
| `_upsert_expiry_record(record, state, dt)` | — | Creates or updates `dwo.expiry.record` row. |
| `_should_send_notification(tracked, state)` | — | Throttle: True if first time, state changed, or 24h+ since last. |
| `_filter_notifiable_users(users)` | — | Excludes muted and currently-dismissed users. |
| `_send_bus_notification(users, msg, state)` | — | Calls `bus.bus._sendone` per user. Sticky if expired. |
| `_send_email_notification(record, users, msg)` | — | Uses template if available, else fallback `mail.mail` with escaped body. `force_send=False`. |
| `_notify_record(record, tracked, state, dt)` | — | Orchestrates: throttle check → collect users → filter → render → send bus/email → update tracked. |
| `_get_rule_search_order()` | — | Returns SQL order string. Field-based: `"{field} asc, id asc"`. Custom: `"id asc"`. Sanitized. |
| `_scan_single_rule()` | — | Main scan loop: search records → pre-fetch tracked → batch upsert → notify. |
| `action_run_scan()` | — | Button action. Runs scan as `rule_user_id` (not sudo). |
| `action_test_notification()` | — | Sends sample bus notification to current user with `[TEST]` prefix. |
| `_cron_scan_and_notify()` | `@api.model` | Cron entrypoint. Iterates active rules with per-rule savepoint isolation. |
| `get_form_view_alerts(model_name, res_id)` | `@api.model` | RPC endpoint for JS. Validates inputs → checks mute/dismiss → evaluates rules → returns alert payload. |

### 7.2 `dwo.expiry.record` Methods

| Method | Decorator | Description |
|--------|-----------|-------------|
| `action_open_record()` | — | Returns `act_window` action to open source record. Checks `read` access first. |
| `_autovacuum_expiry_record_retention()` | `@api.autovacuum` | Deletes records with `create_date` older than 30 days. Batches of 1000. |

### 7.3 `res.users` Methods

| Method | Decorator | Description |
|--------|-----------|-------------|
| `_allowed_dismiss_minutes()` | `@api.model` | Returns whitelist: `[5, 15, 30, 60, 120, 240, 480, 1440, 4320, 10080, 43200]`. |
| `action_set_expiry_dismiss(minutes)` | `@api.model` | Sets `expiry_dismiss_until` for current user. Validates against whitelist. |
| `action_clear_expiry_dismiss()` | `@api.model` | Clears `expiry_dismiss_until` for current user. |

---

## 8. Security Design

### 8.1 Groups

| XML ID | Name | Implied |
|--------|------|---------|
| `module_category_expiry_tracker` | Expiry Tracker (category) | — |
| `group_expiry_custom_user` | Custom Expiry User | `base.group_user` |

### 8.2 Access Rights (`ir.model.access.csv`)

| Model | Group | Read | Write | Create | Delete |
|-------|-------|------|-------|--------|--------|
| `dwo.expiry.rule` | `base.group_system` | ✅ | ✅ | ✅ | ✅ |
| `dwo.expiry.rule` | `group_expiry_custom_user` | ✅ | ✅ | ✅ | ❌ |
| `dwo.expiry.rule` | `base.group_user` | ✅ | ❌ | ❌ | ❌ |
| `dwo.expiry.record` | `base.group_system` | ✅ | ✅ | ✅ | ✅ |
| `dwo.expiry.record` | `base.group_user` | ✅ | ❌ | ❌ | ❌ |

### 8.3 Record Rules

| Name | Model | Scope | Domain |
|------|-------|-------|--------|
| Expiry Rule Company Scope | `dwo.expiry.rule` | Global | `['|', ('company_id','=',False), ('company_id','in',company_ids)]` |
| Expiry Rule Custom User Own | `dwo.expiry.rule` | `group_expiry_custom_user` | `[('rule_user_id','=',user.id)]` |
| Expiry Record Company Scope | `dwo.expiry.record` | Global | `['|', ('company_id','=',False), ('company_id','in',company_ids)]` |

### 8.4 Security Measures

- **Model-name injection prevention**: `get_form_view_alerts` validates `model_name` is a string and `res_id` is an int; checks rules exist before `self.env[model_name]`; catches `KeyError`.
- **Sudo escalation prevention**: `action_run_scan` runs as `rule_user_id` via `.with_user()`, not the caller.
- **XSS prevention**: Fallback email body uses `markupsafe.escape()`.
- **safe_eval**: All user-supplied domains and formulas go through `safe_eval` (not `eval`).
- **Access check on open**: `action_open_record` calls `check_access_rights("read")` and `check_access_rule("read")`.

---

## 9. Views & UI

### 9.1 Menu Structure

```
Expiry Tracker (root, sequence=88)
├── Expiry Rules          (admin only, sequence=10)
├── My Expiry Rules       (custom user only, sequence=20)
└── Tracked Expiry Records (all internal users, sequence=30)
```

### 9.2 Rule Views

| View Type | XML ID | Key Features |
|-----------|--------|--------------|
| Tree | `view_expiry_rule_tree` | Drag handle (`sequence`), name, active, model, owner, date_mode, offset, limit, last_run. |
| Form | `view_expiry_rule_form` | Header: Run Scan + Test Notification + Active toggle. Sheet: title, metadata group, date config group, notebook (Scope / Notifications / Performance). Chatter. |
| Search | `view_expiry_rule_search` | Fields: name, model, owner. Filters: Active, My Rules. Group By: Owner, Model. |

**Form Layout Details:**
- Date config: `date_mode` selector → conditional visibility of `datetime_field_id` (field-based) or `specific_datetime` (custom).
- Offset fields: inline `[n] days` layout using `class="oe_inline"`, hidden in custom mode.
- Notification config: admin-only recipient fields (`groups="base.group_system"`).
- All fields have `placeholder` guide text.
- Help notes use `<div class="text-muted small"><em>...</em></div>`.

### 9.3 Record Views

| View Type | XML ID | Key Features |
|-----------|--------|--------------|
| Tree | `view_expiry_record_tree` | State, name, model, rule, owner, expiry datetime, last seen, "Open Record" button. |
| Form | `view_expiry_record_form` | All fields readonly with placeholder descriptions. |
| Search | `view_expiry_record_search` | Filters: Expired, Upcoming, From My Rule. Group By: State, Rule, Owner, Model. |
| Pivot | `view_expiry_record_pivot` | Rows: Rule. Columns: State. Measure: Count. |
| Graph | `view_expiry_record_graph` | Bar chart by State with Rule grouping. |

### 9.4 User Preferences Views

Two inherited views on `res.users` (both `base.view_users_form_simple_modif` and `base.view_users_form`):
- `expiry_notify_muted` — Boolean toggle
- `expiry_dismiss_until` — Datetime, readonly
- Help text explaining dismiss button usage

---

## 10. JavaScript (Frontend)

### 10.1 `form_expiry_alerts.js`

**Bundle**: `web.assets_backend`
**Pattern**: Patches `FormController.prototype`
**Services Used**: `orm`, `notification`, `action`

#### Lifecycle

1. `setup()` — hooks `useEffect` watching `model.root.resModel`, `resId`, `isNew`.
2. On existing record load → calls `_showExpiryFormAlerts(modelName, resId)`.
3. Deduplication: caches `dwoExpiryLastKey` to avoid repeated calls for same record.

#### Alert Display Logic

```
RPC: dwo.expiry.rule.get_form_view_alerts(modelName, resId)
  ↓
If 1 alert  → show original message
If N alerts → summarize: "This record has N expiry alert(s): X expired, Y upcoming, +Z more"
  ↓
Severity: "danger" if any expired, else "warning"
Sticky: true if any expired
  ↓
Buttons: [View All] + [Dismiss 5min] + [Dismiss 1h] + [Dismiss 1d] + [Dismiss 7d] + [Dismiss 30d]
```

#### Methods

| Method | Description |
|--------|-------------|
| `_showExpiryFormAlerts(modelName, resId)` | Main RPC call + summarization + display. |
| `_buildAlertButtons()` | Returns button array: View All + 5 dismiss presets. |
| `_openExpiryRecords()` | `action.doAction` → opens `dwo.expiry.record` list filtered by current user. |
| `_dismissExpiryFor(minutes, label)` | RPC to `res.users.action_set_expiry_dismiss`. Shows confirmation. |

### 10.2 JS Tests (`form_expiry_alerts_tests.js`)

**Bundle**: `web.tests_assets`
**Framework**: QUnit

| Test | Description |
|------|-------------|
| shows single summarized notification | Multiple alerts → single notification with correct RPC params |
| does not call alerts for new records | New (unsaved) records skip RPC |
| handles empty alerts gracefully | Empty response → no notification |
| handles RPC error gracefully | Network/access error → no crash |
| shows more_count in summary | Verifies overflow count rendering |
| dismiss button calls RPC | Dismiss button triggers `action_set_expiry_dismiss` |

---

## 11. Cron & Automation

### Cron Job: `ir_cron_expiry_scan_notify`

| Setting | Value |
|---------|-------|
| Name | Expiry Tracker - Scan and Notify |
| Model | `dwo.expiry.rule` |
| Method | `_cron_scan_and_notify()` |
| Interval | 15 minutes |
| Repeat | Infinite (`numbercall=-1`) |
| Active | True |
| `noupdate` | True (won't overwrite manual changes) |

### Cron Execution Flow

```
_cron_scan_and_notify()
  │
  ├── Search all active rules (ordered by sequence)
  │
  └── For each rule:
      ├── SAVEPOINT cron_rule_{id}
      ├── _scan_single_rule()
      │   ├── Build search domain
      │   ├── Search target model records
      │   ├── Pre-fetch existing tracked records (1 query)
      │   ├── For each record:
      │   │   ├── _compute_expiry_datetime()
      │   │   ├── Determine state (expired/upcoming)
      │   │   ├── Update existing tracked row OR queue for batch create
      │   │   └── _notify_record() (if existing row)
      │   ├── Batch-create new tracked rows (1 query)
      │   ├── _notify_record() for each new row
      │   └── Update last_run_at, last_run_summary
      ├── RELEASE SAVEPOINT (on success)
      └── ROLLBACK TO SAVEPOINT + log error (on failure)
```

### Autovacuum

```
_autovacuum_expiry_record_retention()
  │
  └── Loop: search 1000 rows with create_date < now - 30 days
      └── unlink() batch → repeat until none left
```

---

## 12. Notification Flow

### 12.1 Scan Notification (Bus + Email)

```
_scan_single_rule()
  └── _notify_record(record, tracked, state, expiry_dt)
      ├── Check: notify_bus OR notify_email enabled?
      ├── _should_send_notification(tracked, state) → throttle check
      ├── _collect_target_users(record)
      │   ├── _resolve_users_from_field(record)
      │   ├── + notify_to_user_ids
      │   ├── + notify_to_notify_group_ids.users
      │   ├── + search(notify_to_user_domain)
      │   ├── + _safe_eval_formula_user_ids(record)
      │   ├── Filter: active=True, share=False
      │   ├── Non-admin → force self only
      │   └── Apply limit_notify_user
      ├── _filter_notifiable_users(users) → exclude muted/dismissed
      ├── _render_template() → message text
      ├── _send_bus_notification(users, msg, state)
      ├── _send_email_notification(record, users, msg)
      └── Update tracked: last_notified_at, last_notified_state
```

### 12.2 Form-View Alert (JS)

```
User opens form view
  └── FormController.setup() → useEffect triggers
      └── _showExpiryFormAlerts(modelName, resId)
          └── RPC: get_form_view_alerts(modelName, resId)
              ├── Check user mute/dismiss
              ├── Search active form-alert rules for this model+company
              ├── Validate model_name (injection prevention)
              ├── For each rule:
              │   ├── _record_matches_additional_domain()
              │   ├── _compute_expiry_datetime()
              │   ├── Determine state
              │   └── _render_template() → alert dict
              └── Return: {alerts: [...max 5], more_count: N}
          └── JS: Summarize → single notification + buttons
```

---

## 13. Anti-Abuse & Throttling

| Mechanism | Layer | Description |
|-----------|-------|-------------|
| Non-admin policy | Python `create`/`write` | Forces `rule_user_id=self`, clears all recipient configs, `limit_notify_user=1`. |
| Notification throttle | Python `_should_send_notification` | Same state: re-notify only after 24h. Different state: immediate. |
| User mute | Python + JS | `expiry_notify_muted=True` → all channels silenced. |
| User dismiss | Python + JS | `expiry_dismiss_until` → temporary silence with preset durations. |
| Record limit | Python `_scan_single_rule` | `limit_record` caps scanned records per rule (default 1000). |
| User limit | Python `_collect_target_users` | `limit_notify_user` caps recipients per notification (default 200). |
| Form alert limit | Python `get_form_view_alerts` | Max 5 alerts returned; JS summarizes into 1 notification. |
| JS dedup | JavaScript | `dwoExpiryLastKey` prevents repeated RPC for same record. |
| Cron isolation | Python `_cron_scan_and_notify` | Per-rule savepoints prevent one failing rule from blocking others. |

---

## 14. Performance Considerations

### Optimizations Implemented

1. **Batch pre-fetch**: `_scan_single_rule` loads all existing tracked records in 1 query before the loop.
2. **Batch create**: New tracked records are batch-created in 1 query after the loop.
3. **Async email**: `force_send=False` queues emails for mail cron instead of blocking.
4. **Selective indexing**: Only fields used in `WHERE`, `ORDER BY`, or record rules are indexed.
5. **Batched autovacuum**: Deletes in batches of 1000 to avoid table locks.
6. **Cron savepoints**: Failed rules don't block subsequent rules.

### Scaling Guidelines

| Records/Rule | Expected Performance |
|---|---|
| 1–1,000 | Fast. Default limit. |
| 1,000–5,000 | Good. Set `limit_record=5000`. |
| 5,000–10,000 | Monitor cron duration. Consider splitting into multiple rules. |
| 10,000+ | Not recommended per single rule. Use domain to partition. |

---

## 15. Test Plan & Test Flow

### 15.1 Test Infrastructure

- **Framework**: `odoo.tests.common.TransactionCase`
- **Tag**: `@tagged("post_install", "-at_install")`
- **Test file**: `tests/test_expiry_rule_engine.py`
- **Total tests**: 27

### 15.2 Test Setup (`setUpClass`)

Creates:
- 2 test users: `custom_expiry_user` (Custom Expiry group), `normal_expiry_user` (base user)
- Model metadata: `ir.model` for `res.partner` and `res.users`
- Field references: `create_date` (datetime), `user_id` (m2o→users), `color` (integer)
- 2 mail templates: one for `res.partner`, one for `res.users` (for mismatch testing)

### 15.3 Test Cases

| # | Test Method | Category | What It Verifies |
|---|-------------|----------|-----------------|
| 1 | `test_compute_total_minutes_supports_negative_values` | Compute | Negative day + positive hour → correct total minutes (-1320) |
| 2 | `test_field_based_rule_requires_datetime_field` | Constraint | Field-based mode raises `ValidationError` without `datetime_field_id` |
| 3 | `test_custom_rule_requires_specific_datetime` | Constraint | Custom mode raises `ValidationError` without `specific_datetime` |
| 4 | `test_invalid_domains_are_rejected` | Constraint | Malformed `additional_domain` and `notify_to_user_domain` both raise errors |
| 5 | `test_email_template_must_match_rule_model` | Constraint | Template for `res.users` on `res.partner` rule → error |
| 6 | `test_non_admin_create_forces_self_recipient_policy` | Security | Custom user create → `rule_user_id=self`, recipients=self, groups cleared, formula cleared, limit=1 |
| 7 | `test_non_admin_write_keeps_self_recipient_policy` | Security | Custom user write → recipients forced back to self |
| 8 | `test_safe_eval_domain_and_formula_methods` | Domain | `_safe_eval_domain` returns correct list; `_safe_eval_formula_user_ids` resolves correct user |
| 9 | `test_resolve_users_from_field_many2one` | Recipient | M2O `user_id` field → resolves correct user |
| 10 | `test_notify_user_field_must_be_user_relation_field` | Constraint | Integer field (`color`) rejected for `notify_to_user_field_id` |
| 11 | `test_collect_target_users_with_domain_formula_and_limit` | Recipient | Merges users from multiple sources; applies limit |
| 12 | `test_compute_expiry_datetime_for_both_modes` | Compute | Custom → returns `specific_datetime` exactly; field-based → `create_date - 5min` |
| 13 | `test_record_domain_match_and_template_rendering` | Domain + Template | Domain match returns True; template renders record name correctly |
| 14 | `test_upsert_record_and_throttle_logic` | Upsert + Throttle | Creates tracked row, updates on re-upsert (same ID), throttle blocks same-state re-notify, allows different-state |
| 15 | `test_filter_notifiable_users` | Filter | Muted user excluded; dismissed user excluded; both cleared → re-included |
| 16 | `test_send_bus_notification` | Bus | Mock `_sendone` called once per user (2 users → 2 calls) |
| 17 | `test_action_test_notification_sends_bus_message` | Test Button | Mock `_sendone` called once; returns `display_notification` action |
| 18 | `test_send_email_notification_fallback` | Email | Mock `MailMail.send` called for fallback email |
| 19 | `test_notify_record_updates_notified_fields` | Notify | After notify: `last_notified_state="expired"`, `last_notified_at` set |
| 20 | `test_search_order_scan_and_actions` | Scan | Order includes field name; `action_run_scan` creates tracked rows; `_cron_scan_and_notify` runs without error |
| 21 | `test_get_form_view_alerts` | Form Alert | Returns alerts for matching record; empty when muted; empty when dismissed |
| 22 | `test_expiry_record_action_and_retention` | Record | `action_open_record` returns correct action; autovacuum deletes 45-day-old row |
| 23 | `test_res_users_dismiss_methods` | User Prefs | `action_set_expiry_dismiss(5)` sets datetime; `action_clear_expiry_dismiss` clears |
| 24 | `test_non_admin_can_dismiss_notifications` | Security | Custom user can set/clear dismiss (SELF_WRITEABLE_FIELDS works) |
| 25 | `test_get_form_view_alerts_rejects_invalid_model` | Security | Invalid model name → empty alerts (no crash); integer model_name → empty |
| 26 | `test_action_open_record_checks_access` | Security | Returns action dict for accessible record |
| 27 | `test_scan_uses_batch_upsert` | Performance | 3 matching partners → 3 tracked records created via batch |

### 15.4 Test Execution

```bash
# Run all module tests
python odoo-bin -c odoo.conf -d testdb -i dwo_document_expiry_tracker \
  --test-enable --test-tags /dwo_document_expiry_tracker \
  --stop-after-init --no-http

# Expected: 0 failed, 0 error(s) of 27 tests
```

### 15.5 Test Coverage Matrix

| Component | Methods Tested | Coverage |
|-----------|---------------|----------|
| Constraints (5) | All 5 | ✅ Full |
| Computed fields (1) | `total_expired_after_minutes` | ✅ Full |
| CRUD overrides (2) | `create`, `write` | ✅ Full |
| Domain/Formula eval (3) | `_safe_eval_domain`, `_safe_eval_formula_user_ids`, `_record_matches_additional_domain` | ✅ Full |
| Recipient resolution (3) | `_resolve_users_from_field`, `_collect_target_users`, `_filter_notifiable_users` | ✅ Full |
| Notification (4) | `_send_bus_notification`, `_send_email_notification`, `_notify_record`, `_should_send_notification` | ✅ Full |
| Scanning (3) | `_scan_single_rule`, `action_run_scan`, `_cron_scan_and_notify` | ✅ Full |
| Form alerts (1) | `get_form_view_alerts` | ✅ Full |
| Test notification (1) | `action_test_notification` | ✅ Full |
| User prefs (2) | `action_set_expiry_dismiss`, `action_clear_expiry_dismiss` | ✅ Full |
| Record actions (2) | `action_open_record`, `_autovacuum_expiry_record_retention` | ✅ Full |
| Template rendering (1) | `_render_template` | ✅ Full |
| Upsert (1) | `_upsert_expiry_record` | ✅ Full |

---

## 16. Configuration Guide

### Step 1: Install Module
Install `dwo_document_expiry_tracker` from Apps menu or CLI.

### Step 2: Assign User Groups
- **Admin**: Already has full access.
- **Custom users**: Add to "Custom Expiry User" group (Settings → Users → Groups tab).

### Step 3: Create Rules

1. Navigate to **Expiry Tracker → Expiry Rules**.
2. Click **Create**.
3. Fill in:
   - **Name**: descriptive label (e.g. "Contract Expiry - Sales")
   - **Target Model**: select model to monitor
   - **Date Mode**:
     - *Field Based*: pick a date/datetime field + set offset days
     - *Custom*: set a specific datetime
4. Configure **Scope** tab: define domain filter for records.
5. Configure **Notifications** tab: enable channels, set template, configure recipients (admin only).
6. Click **Test Notification** to preview.
7. Click **Run Scan** to test with real data.
8. Save. The cron will process this rule every 15 minutes.

### Step 4: Monitor Dashboard
Navigate to **Expiry Tracker → Tracked Expiry Records** to see upcoming/expired records.

---

## 17. Known Limitations

1. **Offset fields**: Only `expired_after_day` is shown in the UI (year/month/hour/minute fields exist in the model but are hidden in the form view for simplicity).
2. **Legacy fields**: 5 legacy compatibility fields on `res.users` add minor overhead. Safe to remove if no external modules depend on them.
3. **JS tests**: Require a running browser (QUnit in Odoo 17). Cannot be run headlessly without additional infrastructure.
4. **Scan sudo**: `_scan_single_rule` uses `.sudo()` to read target model records. The `action_run_scan` button mitigates this by running as `rule_user_id`.
5. **No real-time**: Notifications are cron-driven (15-min default). Form alerts are real-time but only triggered on form open.
6. **Single company**: Each rule is scoped to one company. Multi-company setups need separate rules per company.

---

## 18. Glossary

| Term | Definition |
|------|-----------|
| **Rule** | A `dwo.expiry.rule` record defining what to monitor, when to notify, and whom to notify. |
| **Tracked Record** | A `dwo.expiry.record` row representing a business record matched by a rule with its computed expiry state. |
| **Date Mode** | How the notification datetime is determined: `field_based` (from record field + offset) or `custom` (fixed datetime). |
| **Offset** | Days added to the base datetime. Negative = before expiry (pre-notification). Positive = after expiry. |
| **State** | `upcoming` (expiry datetime in the future) or `expired` (expiry datetime in the past). |
| **Throttle** | Logic to prevent duplicate notifications: same state re-notified only after 24 hours. |
| **Dismiss** | Temporary notification suppression. User sets a duration (5min–30days). |
| **Mute** | Permanent notification suppression until manually re-enabled. |
| **Anti-spam policy** | Backend enforcement that restricts non-admin users to self-only recipients with limit=1. |
| **Bus notification** | Real-time in-app notification via `bus.bus._sendone`. |
| **Form alert** | Popup notification shown when user opens a matching record's form view (JS-driven). |
| **Upsert** | Create-or-update pattern for tracked records (unique per rule+model+res_id). |
| **Autovacuum** | Odoo's built-in cleanup mechanism. This module uses it to purge tracked records older than 30 days. |

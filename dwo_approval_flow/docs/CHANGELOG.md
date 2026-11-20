# Changelog

## 19.0.1.1.0 (2026-11-20)

Issue #100.

- **Guard** (`models/guard.py`): the public methods that "call method" arrows use are patched on the final registry class (idempotent, rebuilt on registry load, removed when no flow needs them; other workers are told through the registry signal). Each arrow has "Protect the method": *direct* (default, only when the call comes from `call_kw`, i.e. a button or RPC), *every call* (except `sudo`) or *none*. A guarded call by a user is turned into pressing the arrow (votes included); if the arrow is not available a `UserError` explains why. The bypass flag is a server-side thread local, not a context key, so a client cannot forge it.
- **Own-state field** `x_dwo_approval_state_id` can no longer be written directly (except by system code and by the arrows).
- **Several active flows per model**: the document is routed to the first flow (by sequence) whose "Applies to" domain matches. Native buttons are hidden only when the model has a single flow.
- **List view**: arrow option "Also allow from the list view". It creates one `ir.actions.server` named `<flow>: <button>` bound to the model (list and form Action menu). It presses the arrow on every selected document where it is available and reports what was skipped. Arrows that ask for a reason are skipped.
- **Test** button on the flow form: pick a document and a user and see which buttons show, with the reason for the hidden ones (same engine as the real buttons).
- The flow form uses the whole width and the designer fills it (taller on big screens).
- `name` of the flow and `message` of notify actions are translatable (state and button names already were). "Approvals needed" in the Who dialog is a radio list.
- Designer: arrows are curves (`static/src/designer/layout.js`, no library) that bend around boxes and spread when several arrows join the same two boxes; labels are moved along their curve so they do not overlap each other or a box; boxes cannot be dragged on top of each other and new boxes get a free spot. An any-state arrow no longer shows its button in its own target state.
- Buttons created by a flow use the outline style.
- The replaced status bar now uses the same markup and style as Odoo's own status bar (no colour dots).
- JSON: `main_step.guard` and `list_action` added to schema `dwo_approval_flow/1` (old JSON still loads).

**Not done**: two flows approving the same document in parallel (a document has one flow at a time), the "same department" approver kind (needs `hr`), email templates, multi-company and `statusbar_visible` are untested, no automated JS tests.

**Tests**: 22 Python tests. The UI was checked by hand in a real Odoo 19 with `purchase`: Action menu of the list, Test dialog, direct `button_confirm` and direct state write refused, then `button_confirm` going through the arrow.

## 19.0.1.0.0 (2026-11-20)

First version (issue #91). Odoo 19 only.

**What it does**
- A flow (`dwo.approval.flow`) is attached to one model. Its states are drawn as boxes and its buttons as arrows in a designer widget (`dwo_flow_designer`, field `graph`).
- States come from the model's own selection/many2one field (`state_mode = field`, states mirror the field, nothing can be added or deleted) or are the flow's own (`state_mode = custom`, the module creates `x_dwo_approval_state_id` on the model).
- An arrow (`dwo.approval.transition`) has: approvers (`dwo.approval.approver`: users, group, same department, user field, expression), rules (`dwo.approval.rule`: Odoo domain with `user`), approvals needed (1 / one per approver line / N), a main step (set the state, or call a public method / server action and then check the document reached the target state, rolled back otherwise), extra actions (`dwo.approval.action`: notify, email, update a field, server action), optional reason.
- An arrow without a source state starts from every state.
- `dwo.approval.log` keeps every vote and state change. Votes count since the last state change of the document.
- The form header of any model with a flow gets the buttons of the current user. This is done in `_get_view` (the arch is edited server side), so it covers every form view. The form's own status bar is kept unless `replace_statusbar` is on. Native buttons that a "call method" arrow wraps are hidden while the document is in the arrow's source state (only when the flow's domain is `[]`).
- Widgets: `dwo_approval_buttons` (header), `dwo_approval_panel` (status bar, waiting, history; options `show_statusbar`, `show_waiting`, `show_history`, `history_limit`, `statusbar_visible`).
- JSON: `graph_to_share` / `share_to_graph` (schema `dwo_approval_flow/1`, logins and xml ids instead of ids), Copy JSON / Load JSON in the designer.

**Not in this version** (planned v1.1): guard on the native method when it is called directly, several flows on the same method, approving from the list Action menu, the "Test" tab. Direct writes to the own-state field are not blocked yet. One active flow per model and company.

**Tests**: 15 Python tests (`tests/test_approval.py`). The JS was checked by hand with a browser (Playwright): designer editing, drag and connect, dialogs, JSON, form buttons and panel. There is no automated JS test yet.

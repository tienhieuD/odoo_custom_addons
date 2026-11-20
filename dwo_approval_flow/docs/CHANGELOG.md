# Changelog

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

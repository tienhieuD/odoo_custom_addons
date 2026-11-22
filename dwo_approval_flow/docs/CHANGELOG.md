# Changelog

## 18.0.2.0.0 (2026-11-22)

Issue #101: notifications. Everything is off until a flow switches it on, so upgrading never sends a mail by itself.

- **Set on each arrow, not on the flow**: not every arrow and not every step needs a message, so nothing is sent until a box is ticked (JSON: `notify` on the arrow with `followers` and `creator`, and `notify` on each approver line; everything false by default; older JSON without it still loads).
- **Who can press it > Notifications, a table at the bottom of the dialog**: one column per approver line of the "Who" list plus a column "Document followers", one row per kind of notification, and a tick in a cell tells that column in that way when the document reaches the step this button starts from. The rows are *System notification* (a pop-up through the bus), *Activity* (a "To approve" to-do, closed when the document moves, or when that person votes) and *Email (inbox)* (an email, or a Discuss message as each person prefers; the default text is translatable, or the email template chosen on the flow). The people of a line are collected from it (users, group, user field, expression) and each one is tested with the same check as the real button (rules, votes already given); only internal users who can read the document and who are not the person who just acted are told, once even when they are on several lines. An arrow that anybody can press has no line and tells nobody. A person is listed in "Waiting for my approval" when at least one box of their line is ticked.
- **Followers column**: the followers of the document who kept the new subtype **Approval** (`dwo_approval_flow.mt_approval`, on by default for new followers). System notification and Activity go to each of them; Email posts one note with that subtype naming the approvers, so they are told as they prefer. The activities of followers are closed when the document moves too.
- **Creator**: arrow option "Notify the creator of the document when this is pressed or voted" (outside the table, it is about what happened, not about the new step), with the reason, or "1/2" while other approvals are missing.
- **Reminders** stay on the flow: "Remind after (hours)" and "Reminders at most". An hourly cron (`Approval flow: remind approvers`) reminds the people who did not answer; it forgets a document that moved on (also when the state was changed outside the arrows) or a person who can no longer press.
- **Waiting for my approval**: new menu for every employee, listing the documents waiting for them with the step and the time (model `dwo.approval.pending`; a person sees only their own rows, administrators see all). It is filled by the arrows that notify their approvers.
- **Notifications log** (menu, administrators): who was told, through which channel (system, activity, email) and kind (approver, followers, creator, reminder), sent or failed with the error (`dwo.approval.notify.log`).
- A failing channel (a broken template, no mail server) never blocks an approval: each send runs in a savepoint and only writes a failed line in the log.
- Known limits: nothing is sent for the first state of a new document (nobody pressed anything), or when the document is moved by code that does not use an arrow; an arrow that calls a method which opens a wizard notifies nobody until the state really changes; own mail templates cannot use the default variables (use `object` as usual); approving by a link in the email, delegation and automatic moves over time stay for V3.
- Small fixes: the columns of "Approval history" are called From and To, and a rule such as "Estimated cost greater than 3000" no longer wraps digit by digit in the arrow panel. The listing (description page and screenshots) shows the new features.
- **AI button**: for now it only says "The AI flow builder is coming soon." (`AI_READY` in `flow_designer.js`; the dialog, the prompt and `ai_suggest` stay in place, with the model call still a mock).
- **Designer, simpler dialogs**: "Same department as the document" is no longer offered as an approver type (an arrow saved with it keeps working and still opens; the option is also gone from the AI prompt). "+ Add a condition" opens the Odoo domain editor at once, and a rule is shown as readable text ("Total greater than 1000") instead of the domain. "Who can press it" has its own "+ Set who can press it" button. "When the button is pressed" now has three choices: *Change the state*, *Run a server action*, *Call a method (advanced)*. The method is typed with an autocomplete (`dwo.approval.flow.model_methods`, flow administrators only): the public methods of the model, the ones behind buttons first, each with the first line of its docstring below the name and the full docstring as a tooltip. "Run as" shows for a server action or a method. The data and the JSON do not change (a server action is a `call_method` step without a method).
- **Protect the method, on by default, no option in the designer**: an arrow that calls a method is protected: when a user presses the original button of the form (or the web client calls that method, `/web/dataset/call_kw` and `call_button`), the press goes through the arrow instead: who may press it, votes, reason; if the user cannot, an error says why, and a document that has no arrow for it runs the method as usual. Code, scheduled actions and external RPC are not blocked. Turn it off for an arrow with `"guard": "none"` in the `main_step` of the JSON (the designer keeps the value). Implemented by overriding the two routes of the web client (`controllers/dataset.py`) with one cached lookup, no patch of the model classes.
- **The state check is always on**: after a method or server action the document must be in the target state, or the whole transaction is cancelled with an error (the option stays in the data as `verify`, default true, but the designer no longer shows it).
- New tests (`tests/test_notify.py`): right people, once only, nobody without the right, channels per arrow, followers who subscribed, arrows without approvers, ticks per approver line, activity closing (move and vote), creator told ("1/2" and the reason), a new round after a rejection, failing template, own template, reminder limit and clean-up, private queue, JSON round trip.

## 18.0.1.3.1 (2026-11-21)

- **Flow administrators without Settings**: the group "Approval Flow / Administrator" now has read-only access to `ir.model`, `ir.model.fields` and `ir.actions.server`, so a plain employee with that group can pick the model, the state field and server actions in the designer (before: "You are not allowed to access Models"). New test `test_flow_admin_without_settings`. Note: they can read the code of server actions and attach an existing one to a button.

## 18.0.1.3.0 (2026-11-21)

- **AI button** (issue #107): next to "Load JSON" in the designer. It opens a dialog to describe the flow; OK calls `dwo.approval.flow.ai_suggest`, which builds the prompt (fixed text from `docs/AI_PROMPT.md` plus a CONTEXT block read from the database), calls `_ai_complete` and checks the answer with the same code as Import (up to 3 tries, sending the errors back). The button has a magic-wand icon and works both ways: on an empty diagram it builds a flow, on a diagram that already has states and arrows it edits it (the current flow goes into the prompt as `existing_flow`, and the dialog and tooltip say "Edit"). The person then presses "Apply to diagram". `_ai_complete` is a MOCK that returns a random flow; put the real API call there.

## 18.0.1.2.0 (2026-11-20)

Issues #104, #105, #106. Upgrading creates the "Approval history" action for existing flows (`migrations/19.0.1.2.0`).

- **Approval history** (issue #104): every flow gets an `ir.actions.server` "Approval history" in the form Action menu (switch: "Approval history action" on the flow). It opens a read-only dialog (`dwo.approval.history`, a transient copy of the log, so it needs no access to the log model) with the document, the flow, the current step and every vote and move. A ready-made server action `dwo_approval_flow.server_action_dwo_approval_history` (uses `active_model`/`active_ids`) can be bound to any model or used as the action of a button or menu; the method is `dwo.approval.flow.action_history(model, ids)`.
- **Status bar visibility** (issue #105): each state has "Always show on the status bar" (like Odoo's `statusbar_visible`, default on, checkbox in the designer panel, dimmed box when off). A state that is off is shown only while the document is in it, so e.g. Approved and Rejected never show together. Stored as `visible` in the JSON (older JSON keeps every state visible). The widget attribute `statusbar_visible` still wins when set.
- **Designer, state field**: picking the "State field" (or switching to "A field of the model") loads its values into the diagram at once, before the flow is saved (`dwo.approval.flow.field_states`). Existing boxes with the same value keep their place, color and visibility; boxes that arrows still use but the field no longer has are kept and flagged. Saving a new flow drawn this way no longer fails with "at least one state is required".

## 18.0.1.1.0 (2026-11-20)

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

**Tests**: 25 Python tests. The UI was checked by hand in a real Odoo 19 with `purchase`: Action menu of the list, Test dialog, direct `button_confirm` and direct state write refused, then `button_confirm` going through the arrow.

## 18.0.1.0.0 (2026-11-20)

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

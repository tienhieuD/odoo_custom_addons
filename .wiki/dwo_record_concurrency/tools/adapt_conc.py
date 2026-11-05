"""usage: adapt_conc.py <NN>  -- adapt the 18.0 copy of dwo_record_concurrency to an older version (17 .. 12)."""
import re, sys
v = int(sys.argv[1])
base = f'/Users/hieu/Documents/Odoo/myproject/odoo_custom_addons{v}/dwo_record_concurrency/'
def edit(rel, fn):
    s = open(base + rel).read(); s2 = fn(s); open(base + rel, 'w').write(s2)
edit('__manifest__.py', lambda s: s.replace('"version": "18.0.1.1.0"', f'"version": "{v}.0.1.1.0"'))
# <list> -> <tree> (the list view is called "tree" up to 17)
edit('views/dwo_model_concurrency_views.xml', lambda s: s.replace('<list>', '<tree>').replace('</list>', '</tree>').replace('list,form', 'tree,form'))
# no has_access before 18
edit('models/ir_websocket.py', lambda s: s.replace('''            record = self.env[model].browse(int(res_id))
            return record.exists().has_access('read')''', '''            record = self.env[model].browse(int(res_id)).exists()
            if not record:
                return False
            record.check_access_rights('read')
            record.check_access_rule('read')
            return True'''))
# Record.getChanges() is public from 18 only
edit('static/src/components/FormControllerPatch/FormControllerPatch.js', lambda s: s.replace(
    "const edited = await root.getChanges();", "await root.isDirty(); // commits what the user is typing\n            const edited = root._getChanges();"))
print('adapted', v)

# ---- JS: odoo-module header (needed up to 17) and 17.0 tour syntax
import glob, os
if v <= 17:
    for f in glob.glob(base + 'static/**/*.js', recursive=True):
        s = open(f).read()
        if '@odoo-module' not in s:
            open(f, 'w').write('/** @odoo-module **/\n\n' + s)
if v <= 17:
    def tour(s):
        s = s.replace('import { rpc } from "@web/core/network/rpc";', 'import { jsonrpc as rpc } from "@web/core/network/rpc_service";')
        s = s.replace('run: `edit ${value}`', 'run: `text ${value}`')
        s = s.replace('''            trigger: ".o_form_view .o_field_widget[name=name] textarea:value(Edited by another user)",
        },''', '''            trigger: ".o_form_view .o_field_widget[name=name] textarea",
            async run() {
                for (let i = 0; i < 40 && this.$anchor.val() !== "Edited by another user"; i++) {
                    await new Promise((resolve) => setTimeout(resolve, 200));
                }
                if (this.$anchor.val() !== "Edited by another user") {
                    throw new Error("the form does not show the latest data: " + this.$anchor.val());
                }
            },
        },''')
        return s
    edit('static/tests/tours/concurrency_tour.js', tour)
print('js adapted', v)

# ---- dialog: no ".translate" prop suffix up to 17
if v <= 17:
    edit('static/src/components/ConcurrencyDialog/ConcurrencyDialog.xml', lambda s: s.replace('title.translate="Saving Record with Concurrency Warning!"', 'title="title"'))
    def dlg(s):
        s = s.replace('import { Dialog } from "@web/core/dialog/dialog";', 'import { _t } from "@web/core/l10n/translation";\nimport { Dialog } from "@web/core/dialog/dialog";')
        s = s.replace('    get lastWriter() {', '    get title() {\n        return _t("Saving Record with Concurrency Warning!");\n    }\n\n    get lastWriter() {')
        return s
    edit('static/src/components/ConcurrencyDialog/ConcurrencyDialog.js', dlg)

if v <= 17:
    # up to 17 the tour looks for the trigger *inside* the open modal
    edit('static/tests/tours/concurrency_tour.js', lambda s: s.replace('".modal .modal-title:contains', '".modal-title:contains').replace('".modal table td:contains', '"table td:contains').replace('".modal button:contains', '"button:contains'))

#!/bin/zsh
# usage: sticky_test.sh <NN> <srcdir> <url> <tourstyle: fn|arr|legacy> <th selector>
v=$1; src=$2; url=$3; style=$4; sel=${5:-"th[data-name=email]"}
M=/Users/hieu/Documents/Odoo/myproject/odoo_custom_addons$v/listview_sticky_header_and_column
mkdir -p $M/tests $M/static/tests
echo "from . import test_tmp_sticky" > $M/tests/__init__.py
if [ "$v" = "12" ]; then
cat > $M/tests/test_tmp_sticky.py <<PY
from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install', 'tmp_sticky')
class TestTmpSticky(HttpCase):
    def test_tour(self):
        self.browser_js('$url', "odoo.__DEBUG__.services['web_tour.tour'].run('tmp_sticky_tour')", "odoo.__DEBUG__.services['web_tour.tour'].tours.tmp_sticky_tour.ready", login='admin', timeout=120)
PY
else
cat > $M/tests/test_tmp_sticky.py <<PY
from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install', 'tmp_sticky')
class TestTmpSticky(HttpCase):
    def test_tour(self):
        self.start_tour('$url', 'tmp_sticky_tour', login='admin')
PY
fi
python3 - <<PY
sel = "$sel"
style = "$style"
run_pin = """() => { document.querySelector("%s .js_pin_this_column").click(); }""" % sel
check = """() => {
            const th = document.querySelector("%s");
            const idx = [...th.parentNode.children].indexOf(th) + 1;
            const t = document.querySelector(".o_list_view thead th:nth-child(" + idx + ")");
            if (getComputedStyle(t).position !== "sticky") { throw new Error("pinned th not sticky: " + getComputedStyle(t).position); }
            if (getComputedStyle(document.querySelector(".o_list_view thead th")).position !== "sticky") { throw new Error("header not sticky"); }
            document.querySelector("%s .js_pin_this_column").click();
        }""" % (sel, sel)
steps = """[
        { trigger: ".o_list_view .o_data_row" },
        { trigger: ".o_list_view thead %s:has(.js_pin_this_column)", run: %s },
        { trigger: ".o_list_view .o_data_row", run: async () => {
            await new Promise((r) => setTimeout(r, 800));
            if (!document.head.querySelector("style[name=listview_sticky_header_and_column]")) { throw new Error("style not injected"); }
            await (%s)();
        } },
        { trigger: ".o_list_view .o_data_row", run: () => {
            if (document.querySelector("style[name=listview_sticky_header_and_column]")) { throw new Error("style not removed"); }
        } },
    ]""" % (sel, run_pin, check)
if style in ("reg", "regc"):
    sync = """[
        { trigger: ".o_list_view .o_data_row", run: () => {} },
        { trigger: ".o_list_view thead %s:has(.js_pin_this_column)", run: () => {
            (async () => {
                try {
                    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
                    document.querySelector("%s .js_pin_this_column").click();
                    await sleep(1000);
                    if (!document.head.querySelector("style[name=listview_sticky_header_and_column]")) { throw new Error("style not injected"); }
                    const th = document.querySelector("%s");
                    const idx = [...th.parentNode.children].indexOf(th) + 1;
                    const t = document.querySelector(".o_list_view thead th:nth-child(" + idx + ")");
                    if (getComputedStyle(t).position !== "sticky") { throw new Error("pinned th not sticky: " + getComputedStyle(t).position); }
                    if (getComputedStyle(document.querySelector(".o_list_view thead th")).position !== "sticky") { throw new Error("header not sticky"); }
                    document.querySelector("%s .js_pin_this_column").click();
                    await sleep(500);
                    if (document.head.querySelector("style[name=listview_sticky_header_and_column]")) { throw new Error("style not removed"); }
                    document.body.classList.add("tmp_done");
                } catch (e) { console.error("STICKYFAIL " + e.message); }
            })();
        } },
        { trigger: "body.tmp_done", run: () => {} },
    ]""" % (sel, sel, sel, sel)
    steps = sync
    if style == "regc":
        js = "odoo.define('tmp_sticky.tour', function (require) {\n'use strict';\nvar tour = require('web_tour.tour');\ntour.register('tmp_sticky_tour', { test: true }, %s);\n});\n" % steps
    else:
        js = '/** @odoo-module **/\nimport tour from "web_tour.tour";\ntour.register("tmp_sticky_tour", { test: true }, %s);\n' % steps
elif style == "fn":
    js = '/** @odoo-module **/\nimport { registry } from "@web/core/registry";\nregistry.category("web_tour.tours").add("tmp_sticky_tour", {\n    steps: () => %s,\n});\n' % steps
else:
    js = '/** @odoo-module **/\nimport { registry } from "@web/core/registry";\nregistry.category("web_tour.tours").add("tmp_sticky_tour", {\n    test: true,\n    steps: %s,\n});\n' % steps
open("$M/static/tests/tmp_tour.js","w").write(js)
m = open("$M/__manifest__.py").read()
if style == "regc":
    open("$M/views/tmp_assets.xml","w").write('<?xml version="1.0" encoding="utf-8"?><odoo><template id="tmp_tour_assets" name="tmp" inherit_id="web.assets_$([ "$v" = 12 ] && echo backend || echo tests)"><xpath expr="." position="inside"><script type="text/javascript" src="/listview_sticky_header_and_column/static/tests/tmp_tour.js"/></xpath></template></odoo>')
    m = m.replace("'data': [", "'data': [\n        'views/tmp_assets.xml',", 1)
elif "tmp_tour" not in m:
    m = m.replace("    'price'", "    'price'", 1)
    import re
    m = re.sub(r"('assets': \{)", r"\1\n        'web.assets_tests': ['listview_sticky_header_and_column/static/tests/tmp_tour.js'],", m, 1)
open("$M/__manifest__.py","w").write(m)
PY
export WRAP_PORT=82$v
export ODOO_BROWSER_BIN=/private/tmp/claude-501/-Users-hieu--claude/2c6103e7-e2d6-4a63-9270-126ab80a6cbe/scratchpad/cft/shell/chrome-headless-shell-mac-arm64/chrome-headless-shell
cd /Users/hieu/Documents/Odoo/$src
perl -e 'alarm 420; exec @ARGV' ./venv/bin/python ${WRAP:-odoo-bin} -c ../myproject/odoo_custom_addons${v}_conf/odoo.conf -d stick${v}t -i listview_sticky_header_and_column,base $EXTRA --test-tags /listview_sticky_header_and_column --stop-after-init --http-port=82$v > /tmp/stick$v.log 2>&1
echo exit=$?
grep -nE "tour succeeded|test successful|FAILED|failed at|Error:|TypeError|ERROR.*(Traceback|odoo\.modules)" /tmp/stick$v.log | cut -c1-260 | head -6
docker exec postgres179 dropdb -U odoo --if-exists stick${v}t
rm -rf $M/tests $M/static/tests $M/views/tmp_assets.xml
python3 - <<PY
import re
p="$M/__manifest__.py"; m=open(p).read()
m=re.sub(r"\n        'web.assets_tests': \['listview_sticky_header_and_column/static/tests/tmp_tour.js'\],","",m)
m=m.replace("\n        'views/tmp_assets.xml',","")
open(p,"w").write(m)
PY

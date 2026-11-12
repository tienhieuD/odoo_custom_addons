"""Build listview_sticky_test_lab for any Odoo version (12..20) from the 19-style generator output.

usage: svgenv/bin/python build_lab.py <version> <target addons dir>   (writes <target>/.lab/listview_sticky_test_lab)
"""
import os, re, shutil, subprocess, sys

V = int(sys.argv[1])
TARGET = sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
ODOO = {12: 'odoo-12.0.20211011', 13: 'odoo-13.0.20230607', 14: 'odoo-14.0.20231205', 15: 'odoo-15.0.20250115',
        16: 'odoo-16.0.20261021', 17: 'odoo-17.0.20240624', 18: 'odoo-18.0.20260412', 19: 'odoo-19.0.20260412',
        20: 'odoo-20.0.20261104'}[V]
OUT = os.path.join(TARGET, '.lab', 'listview_sticky_test_lab')
BASE = '/tmp/lab_base_%d' % V
shutil.rmtree(BASE, ignore_errors=True)
subprocess.check_call([sys.executable, os.path.join(HERE, 'gen_lab.py'), BASE], stdout=subprocess.DEVNULL)

# ------------------------------------------------------------------ widgets available in `web` of this version
names = set()
for root, _, files in os.walk(os.path.expanduser('~/Documents/Project/odoo_core/%s/odoo/addons/web/static/src') % ODOO):
    for f in files:
        if f.endswith('.js'):
            t = open(os.path.join(root, f), errors='ignore').read()
            names |= set(re.findall(r"""(?:field_registry|fieldRegistry|registry\.category\(["']fields["']\))\s*\.\s*add\(\s*["']([\w.]+)["']""", t))
            names |= set(re.findall(r"""\.add\(\s*["']([\w.]+)["']\s*,\s*\w+(?:Field|Widget)""", t))
            names |= set(re.findall(r"""\.add\(\s*["']([\w.]+)["']\s*,\s*(?:basic_fields|relational_fields|[\w]+)\.""", t))
names |= {'handle', 'statusbar', 'image', 'text'}
dropped = set()

def widget_filter(xml):
    def sub(m):
        w = m.group(1)
        if w in names:
            return m.group(0)
        dropped.add(w)
        return ''
    return re.sub(r' widget="([\w.]+)"', sub, xml)

os.makedirs(OUT + '/models', exist_ok=True)
os.makedirs(OUT + '/views', exist_ok=True)
os.makedirs(OUT + '/security', exist_ok=True)
os.makedirs(OUT + '/tests', exist_ok=True)
os.makedirs(OUT + '/static/tests/tours', exist_ok=True)
os.makedirs(OUT + '/tools', exist_ok=True)

LIST = 'tree' if V <= 17 else 'list'

# ------------------------------------------------------------------ views
views = open(BASE + '/views/lshc_test_views.xml').read()
views = widget_filter(views)
if V <= 17:
    views = views.replace('<list', '<tree').replace('</list>', '</tree>')
if V <= 16:
    views = views.replace(' column_invisible="1"', ' invisible="1"')
if V == 13:
    views = views.replace(' enable_counters="1"', '')   # counters arrived in 14
if V == 12:
    views = re.sub(r'\s*<searchpanel>.*?</searchpanel>', '', views, flags=re.S)
open(OUT + '/views/lshc_test_views.xml', 'w').write(views)

menus = open(os.path.expanduser('~/Documents/Project/odoo_appstore/odoo_custom_addons19/.lab/listview_sticky_test_lab/views/lshc_test_menus.xml')).read()
menus = menus.replace("'view_mode': 'list'", "'view_mode': '%s'" % LIST).replace('<field name="view_mode">list,form</field>', '<field name="view_mode">%s,form</field>' % LIST)
open(OUT + '/views/lshc_test_menus.xml', 'w').write(menus)

# ------------------------------------------------------------------ models
py = open(BASE + '/models/models.py').read()
if V <= 14:
    # Odoo <= 13 has no _table_query and 14 cannot join a _table_query comodel: SQL views created in init() (a view is not a table: no storage)
    py = py.replace('from odoo import api, fields, models\n', 'from odoo import api, fields, models, tools\n')
    py = py.replace('from odoo.tools import SQL\n', '')
    py = py.replace('''    @staticmethod
    def _fake_sql(query):
        # `%` is the SQL modulo operator here: escape it for SQL()
        return SQL(query.replace('%', '%%'))
''', '''    def _create_view(self, name, query):
        tools.drop_view_if_exists(self.env.cr, name)
        self.env.cr.execute("CREATE VIEW %s AS (%s)" % (name, query))
''')
    py = py.replace('    @property\n    def _table_query(self):\n        return self._fake_sql(', '    def init(self):\n        self._create_view(self._table, ')
    py = py.replace('"""\n\n    def _compute_tag_ids', '"""\n        )\n\n    def _compute_tag_ids') if False else py
elif V <= 17:
    py = py.replace('from odoo.tools import SQL\n', '')
    py = py.replace("        return SQL(query.replace('%', '%%'))", "        return query.replace('%', '%%')")
    py = py.replace("# `%` is the SQL modulo operator here: escape it for SQL()", "# `%` is the SQL modulo operator here: escape it for the cursor")
if V >= 20:
    # Odoo 20 renamed _table_query to _table_sql (an SQL fragment usable in FROM, so wrapped in parentheses)
    py = py.replace('    @property\n    def _table_query(self):', '    @property\n    def _table_sql(self):')
    py = py.replace("        return SQL(query.replace('%', '%%'))", "        return SQL('(%s)', SQL(query.replace('%', '%%')))")
py = py.replace('# `_auto = False` model whose `_table_query` is a SELECT', '# `_auto = False` model whose `_table_query` is a SELECT') 
if V <= 14:
    py = py.replace('# Generated: fake-data test bed. These models have NO database table and NO view: each one is an\n# `_auto = False` model whose `_table_query` is a SELECT over generate_series(), so rows are produced on the fly,\n# deterministically (same ids/values on every query). Everything is read-only.',
                    '# Generated: fake-data test bed. Odoo %d cannot use `_table_query` for this, so each model is an `_auto = False` model backed by a\n# SQL VIEW created in init() (no table, no stored rows): a SELECT over generate_series(), deterministic and read-only.' % V)
if V <= 17:
    # up to 17 a non-attachment Binary column holds the base64 *text* (18+ stores raw bytes)
    py = re.sub(r"decode\('([A-Za-z0-9+/=]+)', 'base64'\)", r"convert_to('\1', 'UTF8')", py)
open(OUT + '/models/models.py', 'w').write(py)
open(OUT + '/models/__init__.py', 'w').write('from . import models\n')
open(OUT + '/__init__.py', 'w').write('from . import models\n')

# ------------------------------------------------------------------ security
if V >= 20:
    open(OUT + '/security/ir.access.csv', 'w').write('''id,name,model_id,group_id/id,operation,domain
access_lshc_test_record,lshc.test.record,lshc.test.record,base.group_user,ru,
access_lshc_test_line,lshc.test.line,lshc.test.line,base.group_user,ru,
access_lshc_test_category,lshc.test.category,lshc.test.category,base.group_user,r,
access_lshc_test_tag,lshc.test.tag,lshc.test.tag,base.group_user,r,
''')
    sec = 'security/ir.access.csv'
else:
    open(OUT + '/security/ir.model.access.csv', 'w').write('''id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_lshc_test_record,lshc.test.record,model_lshc_test_record,base.group_user,1,1,0,0
access_lshc_test_line,lshc.test.line,model_lshc_test_line,base.group_user,1,1,0,0
access_lshc_test_category,lshc.test.category,model_lshc_test_category,base.group_user,1,0,0,0
access_lshc_test_tag,lshc.test.tag,model_lshc_test_tag,base.group_user,1,0,0,0
''')
    sec = 'security/ir.model.access.csv'

# ------------------------------------------------------------------ tours
EXT = open(HERE + '/lab_tours_body.js').read()
STEPS = open(HERE + '/lab_tours_steps.py').read()
ns = {}
exec(STEPS, ns)
TOURS = ns['TOURS']          # [(tour name, [(trigger, run_js)])]

def steps_js(steps, indent):
    pad = ' ' * indent
    return ',\n'.join('%s{ trigger: %s, run: %s }' % (pad, repr_js(t), r) for t, r in steps)

def repr_js(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

tour_files = {}
if V >= 17:
    out = ('/** @odoo-module **/\n' if V == 17 else '') + 'import { registry } from "@web/core/registry";\n\n' + EXT + '\n'
    for name, steps in TOURS:
        out += 'registry.category("web_tour.tours").add("%s", {\n    steps: () => [\n%s,\n    ],\n});\n\n' % (name, steps_js(steps, 8))
    tour_files['lab_tours.js'] = out
elif V >= 15:
    out = '/** @odoo-module **/\nimport tour from "web_tour.tour";\n\n' + EXT + '\n'
    for name, steps in TOURS:
        out += 'tour.register("%s", { test: true }, [\n%s,\n]);\n\n' % (name, steps_js(steps, 4))
    tour_files['lab_tours.js'] = out
else:
    out = "odoo.define('listview_sticky_test_lab.tours', function (require) {\n'use strict';\nvar tour = require('web_tour.tour');\n\n" + EXT + '\n'
    if V == 12:
        # Odoo 12 stores the column name with jQuery .data() only (no data-name attribute): expose it for the selectors
        out += '''setInterval(function () {
    $('th').each(function () {
        var n = $(this).data('name');
        if (n && !this.hasAttribute('data-name')) { this.setAttribute('data-name', n); }
    });
}, 100);

'''
    for name, steps in TOURS:
        out += 'tour.register("%s", { test: true }, [\n%s,\n]);\n\n' % (name, steps_js(steps, 4))
    out += '});\n'
    tour_files['lab_tours.js'] = out
for f, c in tour_files.items():
    open(OUT + '/static/tests/tours/' + f, 'w').write(c)

A = '/odoo/action-listview_sticky_test_lab.action_lshc_test_' if V >= 18 else '/web#action=listview_sticky_test_lab.action_lshc_test_'
if V == 12:
    tests = '''from odoo.tests import HttpCase, tagged

URL = '%s'
RUN = "odoo.__DEBUG__.services['web_tour.tour'].run('%%s')"
READY = "odoo.__DEBUG__.services['web_tour.tour'].tours.%%s.ready"


@tagged('post_install', '-at_install', 'lshc_lab')
class TestLabTours(HttpCase):
    """Drive the sticky module on the fake wide lists (pin, scroll, check the CSS really sticks)."""

    def _tour(self, action, name):
        self.browser_js(URL + action, RUN %% name, READY %% name, login='admin', timeout=180)

    def test_wide_list(self):
        self._tour('wide', 'lshc_lab_wide_list')

    def test_editable_list(self):
        self._tour('editable', 'lshc_lab_editable_list')

    def test_form_lists(self):
        self._tour('wide', 'lshc_lab_form_lists')
''' % A
else:
    tests = '''from odoo.tests import HttpCase, tagged

URL = '%s'


@tagged('post_install', '-at_install', 'lshc_lab')
class TestLabTours(HttpCase):
    """Drive the sticky module on the fake wide lists (pin, scroll, check the CSS really sticks)."""

    def test_wide_list(self):
        self.start_tour(URL + 'wide', 'lshc_lab_wide_list', login='admin')

    def test_editable_list(self):
        self.start_tour(URL + 'editable', 'lshc_lab_editable_list', login='admin')

    def test_form_lists(self):
        self.start_tour(URL + 'wide', 'lshc_lab_form_lists', login='admin')
''' % A
open(OUT + '/tests/test_lab_tours.py', 'w').write(tests)
open(OUT + '/tests/__init__.py', 'w').write('from . import test_lab_tours\n')

# ------------------------------------------------------------------ manifest
if V >= 15:
    assets = "    'assets': {\n        'web.assets_tests': ['listview_sticky_test_lab/static/tests/tours/*.js'],\n    },\n"
    data_extra = ''
else:
    assets = ''
    data_extra = "        'views/lshc_test_assets.xml',\n"
    bundle = 'web.assets_backend' if V == 12 else 'web.assets_tests'
    open(OUT + '/views/lshc_test_assets.xml', 'w').write('''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="lshc_test_assets" name="LSHC test tours" inherit_id="%s">
        <xpath expr="." position="inside">
            <script type="text/javascript" src="/listview_sticky_test_lab/static/tests/tours/lab_tours.js"/>
        </xpath>
    </template>
</odoo>
''' % bundle)
manifest = '''{
    'name': "List View Sticky - Test Lab",
    'summary': "Developer test bed: wide fake lists to try the sticky header / freeze column module.",
    'description': """
Developer-only test bed for listview_sticky_header_and_column.
Top-level app: List Sticky Test Lab.
Fake data is generated by SQL (no stored rows). Do not publish this module.
    """,
    'author': "DUO-TEK Software Vietnam",
    'license': 'LGPL-3',
    'category': 'Hidden/Tools',
    'version': '%d.0.1.0.0',
    'depends': ['base', 'web', 'listview_sticky_header_and_column'],
    'data': [
        '%s',
        'views/lshc_test_views.xml',
        'views/lshc_test_menus.xml',
%s    ],
%s    'installable': True,
    'application': True,
}
''' % (V, sec, data_extra, assets)
open(OUT + '/__manifest__.py', 'w').write(manifest)

readme = open(os.path.expanduser('~/Documents/Project/odoo_appstore/odoo_custom_addons19/.lab/listview_sticky_test_lab/README.md')).read()
if V <= 14:
    readme = readme.replace('* **No database objects**: the models are `_auto = False` and define `_table_query` (a SELECT over\n  `generate_series`), so no table, no view and no stored row is created.',
                            '* **No stored data**: on Odoo %d `_table_query` cannot be used here, so each `_auto = False` model is backed by a SQL VIEW\n  created in `init()` (a SELECT over `generate_series`): no table and no stored row.' % V)
if V == 12:
    readme += '* Odoo 12 has no search panel: the wide list has the normal search bar only.\n'
open(OUT + '/README.md', 'w').write(readme)
for f in ('gen_lab.py', 'models_part.py', 'build_lab.py', 'lab_tours_body.js', 'lab_tours_steps.py'):
    shutil.copy(os.path.join(HERE, f), OUT + '/tools/' + f)
print('built', V, OUT, 'dropped widgets:', sorted(dropped))

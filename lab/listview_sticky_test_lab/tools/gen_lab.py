"""Generate the listview_sticky_test_lab addon (models + views) so the field/column lists stay consistent."""
import os, sys, textwrap

OUT = sys.argv[1]
os.makedirs(OUT + '/models', exist_ok=True)
os.makedirs(OUT + '/views', exist_ok=True)
os.makedirs(OUT + '/security', exist_ok=True)

# (name, python field expr, string, list widget/attrs dict)  -- main record model, ~50 columns
R = [
 ('sequence',  "fields.Integer(default=10)", 'Seq', {'widget': 'handle'}),
 ('name',      "fields.Char(required=True, index=True)", 'Name', {}),
 ('code',      "fields.Char(index=True)", 'Code', {'widget': 'CopyClipboardChar'}),
 ('category_id', "fields.Many2one('lshc.test.category', string='Category')", 'Category', {}),
 ('state',     "fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('progress','In progress'),('done','Done'),('cancel','Cancelled')], default='draft')", 'Status', {'widget': 'badge'}),
 ('priority',  "fields.Selection([('0','Normal'),('1','Low'),('2','High'),('3','Very high')], default='0')", 'Priority', {'widget': 'priority'}),
 ('kanban_state', "fields.Selection([('normal','In progress'),('done','Ready'),('blocked','Blocked')], default='normal')", 'Kanban state', {'widget': 'state_selection'}),
 ('user_id',   "fields.Many2one('res.users', string='Responsible')", 'Responsible', {'widget': 'many2one_avatar_user'}),
 ('partner_id', "fields.Many2one('res.partner', string='Customer')", 'Customer', {}),
 ('country_id', "fields.Many2one('res.country', string='Country')", 'Country', {}),
 ('city',      "fields.Char()", 'City', {}),
 ('currency_id', "fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)", 'Currency', {'column_invisible': '1'}),
 ('amount',    "fields.Monetary()", 'Amount', {}),
 ('amount_tax', "fields.Monetary()", 'Tax', {}),
 ('amount_total', "fields.Monetary(compute='_compute_amount_total', store=True)", 'Total', {}),
 ('qty',       "fields.Integer()", 'Quantity', {}),
 ('price',     "fields.Float(digits=(16, 3))", 'Unit price', {}),
 ('discount',  "fields.Float(digits=(16, 2))", 'Discount', {'widget': 'percentage'}),
 ('progress',  "fields.Float()", 'Progress', {'widget': 'progressbar'}),
 ('rating_pie', "fields.Float()", 'Rating', {'widget': 'percentpie'}),
 ('duration',  "fields.Float()", 'Duration', {'widget': 'float_time'}),
 ('factor',    "fields.Float()", 'Factor', {'widget': 'float_factor', 'options': "{'factor': 0.5}"}),
 ('active_toggle', "fields.Boolean(default=True)", 'Enabled', {'widget': 'boolean_toggle'}),
 ('favorite',  "fields.Boolean()", 'Favorite', {'widget': 'boolean_favorite'}),
 ('is_vip',    "fields.Boolean()", 'VIP', {}),
 ('flag_icon', "fields.Boolean()", 'Verified', {'widget': 'boolean_icon', 'options': "{'icon': 'fa-check-circle'}"}),
 ('date_start', "fields.Date()", 'Start date', {}),
 ('date_end',  "fields.Date()", 'Deadline', {'widget': 'remaining_days'}),
 ('datetime_created', "fields.Datetime()", 'Created at', {}),
 ('datetime_due', "fields.Datetime()", 'Due at', {}),
 ('email',     "fields.Char()", 'Email', {'widget': 'email'}),
 ('phone',     "fields.Char()", 'Phone', {'widget': 'phone'}),
 ('website',   "fields.Char()", 'Website', {'widget': 'url'}),
 ('website_copy', "fields.Char()", 'Link (copy)', {'widget': 'CopyClipboardURL'}),
 ('color_hex', "fields.Char()", 'Colour', {'widget': 'color'}),
 ('color_index', "fields.Integer()", 'Colour index', {'widget': 'color_picker'}),
 ('tag_ids',   "fields.Many2many('lshc.test.tag', string='Tags')", 'Tags', {'widget': 'many2many_tags', 'options': "{'color_field': 'color'}"}),
 ('follower_ids', "fields.Many2many('res.users', 'lshc_test_record_follower_rel', 'record_id', 'user_id', string='Followers')", 'Followers', {'widget': 'many2many_tags_avatar'}),
 ('kind',      "fields.Selection([('a','Type A'),('b','Type B'),('c','Type C'),('d','Type D')], default='a')", 'Type', {'widget': 'selection_badge'}),
 ('description', "fields.Char()", 'Description', {}),
 ('ref_char',  "fields.Char()", 'Reference', {}),
 ('serial',    "fields.Char()", 'Serial no.', {}),
 ('weight',    "fields.Float(digits=(16, 2))", 'Weight (kg)', {}),
 ('volume',    "fields.Float(digits=(16, 2))", 'Volume (m3)', {}),
 ('height',    "fields.Integer()", 'Height', {}),
 ('width',     "fields.Integer()", 'Width', {}),
 ('stock',     "fields.Integer()", 'Stock', {}),
 ('score_a',   "fields.Float(digits=(16, 1))", 'Score A', {}),
 ('score_b',   "fields.Float(digits=(16, 1))", 'Score B', {}),
 ('score_c',   "fields.Integer()", 'Score C', {}),
 ('notes',     "fields.Text()", 'Notes', {'widget': 'text'}),
 ('image',     "fields.Image(max_width=64, max_height=64)", 'Image', {'widget': 'image', 'options': "{'size': [32, 32]}"}),
]

# line model: key fields + extra generic columns
L = [
 ('sequence', "fields.Integer(default=10)", 'Seq', {'widget': 'handle'}),
 ('name', "fields.Char(required=True)", 'Description', {}),
 ('product', "fields.Char()", 'Product', {}),
 ('qty', "fields.Float(default=1.0)", 'Qty', {}),
 ('price', "fields.Float(digits=(16, 2))", 'Unit price', {}),
 ('discount', "fields.Float()", 'Disc. %', {}),
 ('total', "fields.Monetary(compute='_compute_total', store=True)", 'Total', {}),
 ('currency_id', "fields.Many2one('res.currency', related='record_id.currency_id', store=True)", 'Currency', {'column_invisible': '1'}),
 ('state', "fields.Selection([('draft','Draft'),('ok','Validated'),('late','Late'),('cancel','Cancelled')], default='draft')", 'Status', {'widget': 'badge'}),
 ('partner_id', "fields.Many2one('res.partner', string='Partner')", 'Partner', {}),
 ('user_id', "fields.Many2one('res.users', string='Owner')", 'Owner', {'widget': 'many2one_avatar_user'}),
 ('date', "fields.Date()", 'Date', {}),
 ('deadline', "fields.Datetime()", 'Deadline', {}),
 ('progress', "fields.Float()", 'Progress', {'widget': 'progressbar'}),
 ('priority', "fields.Selection([('0','Normal'),('1','Low'),('2','High'),('3','Very high')], default='0')", 'Priority', {'widget': 'priority'}),
 ('flag', "fields.Boolean()", 'Flag', {'widget': 'boolean_toggle'}),
 ('email', "fields.Char()", 'Email', {'widget': 'email'}),
 ('phone', "fields.Char()", 'Phone', {'widget': 'phone'}),
 ('url', "fields.Char()", 'URL', {'widget': 'url'}),
 ('tag_ids', "fields.Many2many('lshc.test.tag', 'lshc_test_line_tag_rel', 'line_id', 'tag_id', string='Tags')", 'Tags', {'widget': 'many2many_tags', 'options': "{'color_field': 'color'}"}),
 ('color_index', "fields.Integer()", 'Colour', {'widget': 'color_picker'}),
 ('note', "fields.Char()", 'Note', {}),
]
for i in range(1, 17):
    if i % 4 == 0:
        L.append(('f%02d' % i, "fields.Char()", 'Text %d' % i, {}))
    elif i % 4 == 1:
        L.append(('f%02d' % i, "fields.Integer()", 'Int %d' % i, {}))
    elif i % 4 == 2:
        L.append(('f%02d' % i, "fields.Float(digits=(16, 2))", 'Float %d' % i, {}))
    else:
        L.append(('f%02d' % i, "fields.Date()", 'Date %d' % i, {}))

def attrs(opts, skip=()):
    s = ''
    for k, v in opts.items():
        if k in skip:
            continue
        s += ' %s="%s"' % (k, v)
    return s

def lfield(spec, extra=''):
    return '<field name="%s"%s%s/>' % (spec[0], attrs(spec[3]), extra)

def cols(specs, names, indent, optional=None):
    by = {s[0]: s for s in specs}
    return '\n'.join(' ' * indent + lfield(by[n]) for n in names)

# ---------------------------------------------------------------- python
def pyfields(specs):
    out = ''
    for n, expr, label, _ in specs:
        if ',' in expr and 'string=' not in expr and not expr.endswith('()') and n not in ('state',):
            pass
        # inject string
        if 'string=' in expr:
            out += '    %s = %s\n' % (n, expr)
        elif expr.endswith('()'):
            out += '    %s = %s\n' % (n, expr[:-1] + 'string=%r)' % label)
        else:
            out += '    %s = %s\n' % (n, expr[:-1] + ', string=%r)' % label)
    return out

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models_part.py')).read())

# ---------------------------------------------------------------- views
ALLR = [s[0] for s in R]
def list_view(vid, name, names, editable=None, specs=R, model='lshc.test.record', extra=''):
    ed = ' editable="%s"' % editable if editable else ''
    return '''    <record id="%s" model="ir.ui.view">
        <field name="name">%s</field>
        <field name="model">%s</field>
        <field name="arch" type="xml">
            <list string="%s"%s%s>
%s
            </list>
        </field>
    </record>
''' % (vid, name, model, name, ed, extra, cols(specs, names, 16))

# inline line lists (inside the form)
LN = [s[0] for s in L]
SMALL = ['sequence', 'name', 'qty', 'price', 'total', 'state', 'currency_id']
MEDIUM = ['sequence', 'name', 'product', 'qty', 'price', 'discount', 'total', 'currency_id', 'state', 'partner_id', 'user_id', 'date', 'deadline', 'progress', 'priority', 'flag', 'tag_ids']
LARGE = [n for n in LN if n not in ('f13', 'f14', 'f15', 'f16')]

def inline_list(names, indent, editable=None):
    ed = ' editable="%s"' % editable if editable else ''
    pad = ' ' * indent
    return '%s<list%s>\n%s\n%s</list>' % (pad, ed, cols(L, names, indent + 4), pad)

def o2m(fname, kind, names, indent, editable=None, nolabel=True):
    pad = ' ' * indent
    nl = ' nolabel="1"' if nolabel else ''
    return '%s<field name="%s"%s context="{\'default_kind\': \'%s\'}">\n%s\n%s</field>' % (
        pad, fname, nl, kind, inline_list(names, indent + 4, editable), pad)

form_main = ['name', 'code', 'category_id', 'user_id', 'partner_id', 'country_id', 'city', 'date_start', 'date_end', 'tag_ids', 'priority', 'kanban_state', 'kind']
form_money = ['currency_id', 'amount', 'amount_tax', 'amount_total', 'qty', 'price', 'discount', 'progress', 'rating_pie', 'duration']
form_more = ['email', 'phone', 'website', 'website_copy', 'color_hex', 'color_index', 'follower_ids', 'description', 'ref_char', 'serial',
             'weight', 'volume', 'height', 'width', 'stock', 'score_a', 'score_b', 'score_c', 'factor', 'active_toggle', 'favorite', 'is_vip', 'flag_icon',
             'datetime_created', 'datetime_due']
byR = {s[0]: s for s in R}
def ffields(names, indent):
    return '\n'.join(' ' * indent + '<field name="%s"%s/>' % (n, ' widget="%s"' % byR[n][3]['widget'] if 'widget' in byR[n][3] and n not in ('sequence',) and byR[n][3]['widget'] not in ('handle', 'image', 'text', 'badge', 'selection_badge') and n not in ('tag_ids',) else '') for n in names if n != 'currency_id' or True)

form = '''    <record id="lshc_test_record_view_form" model="ir.ui.view">
        <field name="name">lshc.test.record.form</field>
        <field name="model">lshc.test.record</field>
        <field name="arch" type="xml">
            <form string="Test record">
                <header>
                    <field name="state" widget="statusbar" options="{'clickable': '1'}"/>
                </header>
                <sheet>
                    <field name="image" widget="image" class="oe_avatar"/>
                    <div class="oe_title">
                        <h1><field name="name" placeholder="Name"/></h1>
                    </div>
                    <group>
                        <group string="Main">
%s
                        </group>
                        <group string="Amounts">
%s
                        </group>
                    </group>
                    <group string="Full width list - 7 columns (not in a tab)">
%s
                    </group>
                    <notebook>
                        <page string="Medium - editable" name="medium">
%s
                        </page>
                        <page string="Large - 38 columns" name="large">
%s
                        </page>
                        <page string="Half width lists" name="half">
                            <group>
                                <group string="Left half (7 columns)">
%s
                                </group>
                                <group string="Right half (17 columns, editable)">
%s
                                </group>
                            </group>
                        </page>
                        <page string="More fields" name="more">
                            <group>
                                <group>
%s
                                </group>
                                <group>
%s
                                </group>
                            </group>
                            <field name="notes" placeholder="Notes"/>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>
''' % (
    ffields(form_main, 28), ffields(form_money, 28),
    o2m('line_small_ids', 'small', SMALL, 24),
    o2m('line_medium_ids', 'medium', MEDIUM, 28, editable='bottom'),
    o2m('line_large_ids', 'large', LARGE, 28),
    o2m('line_left_ids', 'left', SMALL, 36),
    o2m('line_right_ids', 'right', MEDIUM, 36, editable='bottom'),
    ffields(form_more[:12], 36), ffields(form_more[12:], 36))

search = '''    <record id="lshc_test_record_view_search" model="ir.ui.view">
        <field name="name">lshc.test.record.search</field>
        <field name="model">lshc.test.record</field>
        <field name="arch" type="xml">
            <search string="Test records">
                <field name="name" string="Name / Code" filter_domain="['|', ('name', 'ilike', self), ('code', 'ilike', self)]"/>
                <field name="partner_id"/>
                <field name="user_id"/>
                <filter name="favorite" string="Favorites" domain="[('favorite', '=', True)]"/>
                <filter name="vip" string="VIP" domain="[('is_vip', '=', True)]"/>
                <filter name="late" string="Overdue" domain="[('date_end', '&lt;', context_today().strftime('%Y-%m-%d')), ('state', 'not in', ('done', 'cancel'))]"/>
                <separator/>
                <filter name="high" string="High priority" domain="[('priority', 'in', ('2', '3'))]"/>
                <group>
                    <filter name="group_category" string="Category" context="{'group_by': 'category_id'}"/>
                    <filter name="group_state" string="Status" context="{'group_by': 'state'}"/>
                    <filter name="group_user" string="Responsible" context="{'group_by': 'user_id'}"/>
                    <filter name="group_country" string="Country" context="{'group_by': 'country_id'}"/>
                </group>
                <searchpanel>
                    <field name="category_id" string="Category" icon="fa-folder" enable_counters="1"/>
                    <field name="state" string="Status" select="multi" icon="fa-flag" enable_counters="1"/>
                    <field name="priority" string="Priority" select="multi" icon="fa-star"/>
                </searchpanel>
            </search>
        </field>
    </record>
'''

views = '<?xml version="1.0" encoding="utf-8"?>\n<odoo>\n' + list_view('lshc_test_record_view_list', 'lshc.test.record.list', ALLR) \
    + list_view('lshc_test_record_view_list_editable', 'lshc.test.record.list.editable',
                [n for n in ALLR if n not in ('image', 'notes', 'follower_ids', 'rating_pie', 'color_hex', 'website_copy', 'datetime_due', 'score_a', 'score_b', 'score_c', 'serial', 'ref_char')],
                editable='top') \
    + form + search + '</odoo>\n'
open(OUT + '/views/lshc_test_views.xml', 'w').write(views)
print('columns main list:', len(ALLR), 'editable:', len([n for n in ALLR if n not in ('image', 'notes', 'follower_ids', 'rating_pie', 'color_hex', 'website_copy', 'datetime_due', 'score_a', 'score_b', 'score_c', 'serial', 'ref_char')]), 'large line:', len(LARGE))

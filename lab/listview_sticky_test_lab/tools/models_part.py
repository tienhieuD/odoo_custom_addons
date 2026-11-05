import base64, io, re
from PIL import Image, ImageDraw

def png(color):
    im = Image.new('RGB', (64, 64), color)
    ImageDraw.Draw(im).ellipse((12, 12, 52, 52), fill=(255, 255, 255))
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True)
    return base64.b64encode(b.getvalue()).decode()
PNGS = [png(c) for c in ((135, 90, 123), (14, 124, 102), (91, 141, 184), (224, 168, 31))]

def H(salt):
    return "abs(hashtext(g.id::text || '%s'))" % salt
def PICK(arr, salt):
    return "(ARRAY[%s])[1 + mod(%s, %d)]" % (', '.join("'%s'" % a for a in arr), H(salt), len(arr))
def REFPICK(col, salt):
    return "ref.%s[1 + mod(%s, GREATEST(array_length(ref.%s, 1), 1))]" % (col, H(salt), col)

FIRST = ['Anna', 'Minh', 'Linh', 'David', 'Sofia', 'Kenji', 'Lucas', 'Mai', 'Omar', 'Chloe', 'Hugo', 'Yuki']
LAST = ['Nguyen', 'Tran', 'Smith', 'Garcia', 'Tanaka', 'Martin', 'Silva', 'Kim', 'Rossi', 'Muller']
THING = ['Order', 'Contract', 'Project', 'Ticket', 'Shipment', 'Invoice', 'Quote', 'Campaign']
CITY = ['Hanoi', 'Saigon', 'Da Nang', 'Paris', 'Berlin', 'Tokyo', 'Austin', 'Lisbon', 'Oslo', 'Cairo']
NOTE = ['Call back next week', 'Waiting for approval', 'Needs a second review', 'Delivered on time', 'Customer asked for a discount', 'Check the packaging']
NREC = 240
RM = R + [('write_date', 'fields.Datetime()', 'Last update', {})]   # needed by the image widget (cache key)

RS = {
 'sequence': "g.id * 10",
 'name': "%s || ' ' || %s || ' #' || g.id" % (PICK(THING, 'n1'), PICK(LAST, 'n2')),
 'code': "'LAB-' || lpad(g.id::text, 5, '0')",
 'category_id': "1 + mod(%s, 8)" % H('cat'),
 'state': PICK(['draft', 'confirmed', 'progress', 'done', 'cancel'], 'st'),
 'priority': "(mod(%s, 4))::text" % H('pr'),
 'kanban_state': PICK(['normal', 'done', 'blocked'], 'ks'),
 'user_id': REFPICK('users', 'u'),
 'partner_id': REFPICK('partners', 'p'),
 'country_id': REFPICK('countries', 'c'),
 'city': PICK(CITY, 'city'),
 'currency_id': "ref.currency_id",
 'amount': "round((mod(%s, 9000000)) / 100.0, 2)" % H('am'),
 'amount_tax': "round((mod(%s, 900000)) / 100.0, 2)" % H('tx'),
 'amount_total': "round((mod(%s, 9000000)) / 100.0, 2) + round((mod(%s, 900000)) / 100.0, 2)" % (H('am'), H('tx')),
 'qty': "1 + mod(%s, 500)" % H('q'),
 'price': "round((mod(%s, 100000)) / 100.0, 3)" % H('pc'),
 'discount': "round((mod(%s, 30)) / 100.0, 2)" % H('di'),
 'progress': "(mod(%s, 101))::float" % H('pg'),
 'rating_pie': "(mod(%s, 101))::float" % H('rt'),
 'duration': "round((mod(%s, 1200)) / 100.0, 2)" % H('du'),
 'factor': "round((mod(%s, 2000)) / 100.0, 2)" % H('fa'),
 'active_toggle': "mod(%s, 5) <> 0" % H('ac'),
 'favorite': "mod(%s, 7) = 0" % H('fv'),
 'is_vip': "mod(%s, 6) = 0" % H('vp'),
 'flag_icon': "mod(%s, 3) = 0" % H('fl'),
 'date_start': "current_date - (mod(%s, 90))" % H('d1'),
 'date_end': "current_date + ((mod(%s, 120)) - 40)" % H('d2'),
 'datetime_created': "(now() at time zone 'utc')::timestamp - ((mod(%s, 90)) || ' days')::interval - ((mod(%s, 1440)) || ' minutes')::interval" % (H('t1'), H('t1m')),
 'datetime_due': "(now() at time zone 'utc')::timestamp + (((mod(%s, 90)) - 20) || ' days')::interval + ((mod(%s, 1440)) || ' minutes')::interval" % (H('t2'), H('t2m')),
 'email': "lower(%s || '.' || %s) || g.id || '@example.com'" % (PICK(FIRST, 'e1'), PICK(LAST, 'e2')),
 'phone': "'+84 9' || lpad((mod(%s, 100000000))::text, 8, '0')" % H('ph'),
 'website': "'https://example.com/lab/' || g.id",
 'website_copy': "'https://example.com/share/' || md5(g.id::text)",
 'color_hex': "'#' || substr(md5(g.id::text), 1, 6)",
 'color_index': "mod(%s, 12)" % H('ci'),
 'kind': PICK(['a', 'b', 'c', 'd'], 'kd'),
 'description': "%s || ' for ' || %s || ' - batch ' || (mod(%s, 90))" % (PICK(THING, 'ds1'), PICK(CITY, 'ds2'), H('ds3')),
 'ref_char': "'REF/' || to_char(current_date, 'YYYY') || '/' || lpad((mod(%s, 9999))::text, 4, '0')" % H('rf'),
 'serial': "upper(substr(md5('s' || g.id::text), 1, 10))",
 'weight': "round((mod(%s, 100000)) / 100.0, 2)" % H('wt'),
 'volume': "round((mod(%s, 5000)) / 100.0, 2)" % H('vo'),
 'height': "10 + mod(%s, 190)" % H('hg'),
 'width': "10 + mod(%s, 90)" % H('wd'),
 'stock': "mod(%s, 2000)" % H('sk'),
 'score_a': "round((mod(%s, 1000)) / 10.0, 1)" % H('sa'),
 'score_b': "round((mod(%s, 1000)) / 10.0, 1)" % H('sb'),
 'score_c': "mod(%s, 100)" % H('sc'),
 'notes': PICK(NOTE, 'no') + " || '. ' || " + PICK(NOTE, 'no2'),
 'write_date': "(now() at time zone 'utc')::date::timestamp",
 'image': "CASE mod(%s, 4) %s END" % (H('im'), ' '.join("WHEN %d THEN decode('%s', 'base64')" % (k, p) for k, p in enumerate(PNGS))),
}
LS = {
 'sequence': "g.n * 10",
 'name': PICK(THING, 'l1') + " || ' line ' || g.n",
 'product': PICK(['Desk', 'Chair', 'Lamp', 'Cable', 'Monitor', 'Keyboard', 'Router', 'Printer'], 'l2') + " || ' ' || (mod(%s, 900) + 100)" % H('l2n'),
 'total': "round((g.qty * g.price * (1 - g.discount / 100.0))::numeric, 2)",
 'currency_id': "ref.currency_id",
 'state': PICK(['draft', 'ok', 'late', 'cancel'], 'ls'),
 'partner_id': REFPICK('partners', 'lpa'),
 'user_id': REFPICK('users', 'lu'),
 'date': "current_date + ((mod(%s, 100)) - 30)" % H('lda'),
 'deadline': "(now() at time zone 'utc')::timestamp + (((mod(%s, 60)) - 20) || ' days')::interval" % H('ldl'),
 'progress': "(mod(%s, 101))::float" % H('lpg'),
 'priority': "(mod(%s, 4))::text" % H('lpr'),
 'flag': "mod(%s, 3) = 0" % H('lfl'),
 'email': "lower(%s) || g.n || '@example.com'" % PICK(FIRST, 'lem'),
 'phone': "'+33 6' || lpad((mod(%s, 100000000))::text, 8, '0')" % H('lph'),
 'url': "'https://example.com/line/' || g.id",
 'color_index': "mod(%s, 12)" % H('lci'),
 'note': PICK(NOTE, 'lno'),
}
for i in range(1, 17):
    n = 'f%02d' % i
    if i % 4 == 0:
        LS[n] = PICK(['alpha', 'beta', 'gamma', 'delta', 'omega'], 'x' + n) + " || '-' || (mod(%s, 99))" % H('y' + n)
    elif i % 4 == 1:
        LS[n] = "mod(%s, 10000)" % H('x' + n)
    elif i % 4 == 2:
        LS[n] = "round(((mod(%s, 100000)) / 100.0)::numeric, 2)" % H('x' + n)
    else:
        LS[n] = "current_date + ((mod(%s, 200)) - 100)" % H('x' + n)
# columns computed in the inner query of the line view (so `total` can use them)
INNER = {
 'qty': "round(((mod(abs(hashtext(g0.id::text || 'lq')), 2000)) / 100.0)::numeric, 2)",
 'price': "round(((mod(abs(hashtext(g0.id::text || 'lp')), 50000)) / 100.0)::numeric, 2)",
 'discount': "round(((mod(abs(hashtext(g0.id::text || 'ld')), 25)))::numeric, 1)",
}
SKIP_FIELD = ('record_id', 'kind')


def pyfield(n, expr, label):
    """Plain stored-column field definition (no defaults/computes: values come from the SQL)."""
    expr = re.sub(r"default=lambda self: self\.env\.company\.currency_id", '', expr)
    expr = re.sub(r"default='[^']*'", '', expr)
    expr = re.sub(r", compute='[^']*', store=True", '', expr)
    expr = expr.replace(", related='record_id.currency_id', store=True", '')
    expr = re.sub(r"default=(True|1\.0|10)", '', expr)
    expr = re.sub(r"\(\s*,\s*", '(', expr)
    expr = re.sub(r",\s*,", ',', expr)
    expr = re.sub(r",\s*\)", ')', expr)
    if 'fields.Image' in expr:
        expr = "fields.Binary(attachment=False)"
    if 'string=' not in expr:
        expr = expr[:-1] + ('' if expr.endswith('()') else ', ') + 'string=%r)' % label
    return '    %s = %s\n' % (n, expr)


def pyfields(specs, computed=()):
    out = ''
    for n, expr, label, _ in specs:
        if n in computed:
            continue
        out += pyfield(n, expr, label)
    return out


def sql_cols(specs, mapping, skip=()):
    return ',\n            '.join('%s AS %s' % (mapping[n], n) for n, *_ in specs if n not in skip)


REF_CTE = """WITH ref AS (
            SELECT ARRAY(SELECT id FROM res_users WHERE active ORDER BY id) AS users,
                   ARRAY(SELECT id FROM res_partner WHERE active ORDER BY id LIMIT 300) AS partners,
                   ARRAY(SELECT id FROM res_country ORDER BY id LIMIT 80) AS countries,
                   (SELECT currency_id FROM res_company ORDER BY id LIMIT 1) AS currency_id
        )"""

REC_COLS = [s for s in RM if s[0] not in ('tag_ids', 'follower_ids')]
rec_sql = REF_CTE + """
        SELECT g.id AS id,
            %s
        FROM generate_series(1, %d) AS g(id)
        CROSS JOIN ref""" % (sql_cols(REC_COLS, RS), NREC)

LINE_COLS = [s for s in L if s[0] not in ('tag_ids', 'qty', 'price', 'discount')]
line_sql = REF_CTE + """
        SELECT g.id AS id, g.record_id AS record_id, g.kind AS kind,
            g.qty AS qty, g.price AS price, g.discount AS discount,
            %s
        FROM (
            SELECT (r.id * 1000 + k.off + n.n) AS id, r.id AS record_id, k.kind AS kind, n.n AS n,
                   %s AS qty, %s AS price, %s AS discount
            FROM generate_series(1, %d) AS r(id)
            CROSS JOIN (VALUES ('small', 0, 4), ('medium', 100, 8), ('large', 200, 12), ('left', 300, 5), ('right', 400, 5)) AS k(kind, off, cnt)
            CROSS JOIN LATERAL generate_series(1, k.cnt) AS n(n)
        ) AS g
        CROSS JOIN ref""" % (
    sql_cols(LINE_COLS, LS),
    INNER['qty'].replace('g0.id', '(r.id * 1000 + k.off + n.n)'),
    INNER['price'].replace('g0.id', '(r.id * 1000 + k.off + n.n)'),
    INNER['discount'].replace('g0.id', '(r.id * 1000 + k.off + n.n)'), NREC)
line_sql = line_sql.replace('%%', '%')


def q(s):
    return '"""' + s.replace('%%', '%') + '"""'


rec_py = '''# -*- coding: utf-8 -*-
# Generated: fake-data test bed. These models have NO database table and NO view: each one is an
# `_auto = False` model whose `_table_query` is a SELECT over generate_series(), so rows are produced on the fly,
# deterministically (same ids/values on every query). Everything is read-only.
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import SQL

READ_ONLY = "Test-bed data is generated by SQL and is read-only: changes are not saved."


class LshcTestBase(models.AbstractModel):
    _name = 'lshc.test.base'
    _description = 'LSHC test base (generated, read-only)'

    @staticmethod
    def _fake_sql(query):
        # `%` is the SQL modulo operator here: escape it for SQL()
        return SQL(query.replace('%', '%%'))

    def write(self, vals):
        return True

    def unlink(self):
        return True

    @api.model_create_multi
    def create(self, vals_list):
        raise UserError(READ_ONLY)


class LshcTestCategory(models.Model):
    _name = 'lshc.test.category'
    _description = 'LSHC test category'
    _inherit = ['lshc.test.base']
    _auto = False
    _log_access = False
    _order = 'id'  # ordering by name would JOIN the comodel table, which does not exist for _table_query models

    name = fields.Char()

    @property
    def _table_query(self):
        return self._fake_sql("""
            SELECT g.id AS id,
                   (ARRAY['Hardware', 'Software', 'Services', 'Logistics', 'Marketing', 'Finance', 'Support', 'Research'])[g.id] AS name
            FROM generate_series(1, 8) AS g(id)""")


class LshcTestTag(models.Model):
    _name = 'lshc.test.tag'
    _description = 'LSHC test tag'
    _inherit = ['lshc.test.base']
    _auto = False
    _log_access = False
    _order = 'id'  # ordering by name would JOIN the comodel table, which does not exist for _table_query models

    name = fields.Char()
    color = fields.Integer()

    @property
    def _table_query(self):
        return self._fake_sql("""
            SELECT g.id AS id,
                   (ARRAY['urgent', 'vip', 'new', 'follow-up', 'b2b', 'b2c', 'export', 'promo', 'fragile', 'seasonal'])[g.id] AS name,
                   mod(g.id, 12) AS color
            FROM generate_series(1, 10) AS g(id)""")


class LshcTestRecord(models.Model):
    _name = 'lshc.test.record'
    _description = 'LSHC test record'
    _inherit = ['lshc.test.base']
    _auto = False
    _log_access = False
    _order = 'sequence, id'

''' + pyfields([s for s in RM if s[0] not in ('tag_ids', 'follower_ids')]) + '''    tag_ids = fields.Many2many('lshc.test.tag', string='Tags', compute='_compute_tag_ids')
    follower_ids = fields.Many2many('res.users', string='Followers', compute='_compute_follower_ids')
    line_ids = fields.One2many('lshc.test.line', 'record_id', string='All lines')
''' + ''.join("    line_%s_ids = fields.One2many('lshc.test.line', 'record_id', string='%s lines', domain=[('kind', '=', '%s')])\n" % (k, k.title(), k) for k in ('small', 'medium', 'large', 'left', 'right')) + '''
    @property
    def _table_query(self):
        return self._fake_sql(@@REC@@)

    def _compute_tag_ids(self):
        tags = self.env['lshc.test.tag']
        for rec in self:
            ids = [1 + ((rec.id + t * 3) % 10) for t in range(3) if (rec.id + t) % 3]
            rec.tag_ids = tags.browse(ids)

    def _compute_follower_ids(self):
        users = self.env['res.users'].search([], order='id', limit=3)
        for rec in self:
            rec.follower_ids = users[:1 + (rec.id % 3)]


class LshcTestLine(models.Model):
    _name = 'lshc.test.line'
    _description = 'LSHC test line'
    _inherit = ['lshc.test.base']
    _auto = False
    _log_access = False
    _order = 'sequence, id'

    record_id = fields.Many2one('lshc.test.record')
    kind = fields.Selection([('small', 'Small'), ('medium', 'Medium'), ('large', 'Large'), ('left', 'Left'), ('right', 'Right')])
'''.replace('@@REC@@', q(rec_sql)) + pyfields([s for s in L if s[0] != 'tag_ids']) + '''    tag_ids = fields.Many2many('lshc.test.tag', string='Tags', compute='_compute_tag_ids')

    @property
    def _table_query(self):
        return self._fake_sql(@@LINE@@)

    def _compute_tag_ids(self):
        tags = self.env['lshc.test.tag']
        for line in self:
            line.tag_ids = tags.browse([1 + ((line.id + 7) % 10)] if line.id % 4 else [])
'''.replace('@@LINE@@', q(line_sql))
open(OUT + '/models/models.py', 'w').write(rec_py)
open(OUT + '/models/__init__.py', 'w').write('from . import models\n')


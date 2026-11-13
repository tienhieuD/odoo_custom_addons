# -*- coding: utf-8 -*-
"""TG-36 (task 023): màu cố định theo ý nghĩa cho graph báo cáo và trục phần trăm.
Màu thật được đo trong tour `dwo_sla_graph_colors` (test_tg34); ở đây kiểm cấu hình."""
import re

from lxml import etree

from odoo.modules.module import get_module_path
from odoo.tests import TransactionCase, tagged

MODULE = 'dwo_sla_core'


def _palette(js):
    """{model: {field: {value}}} đọc từ SLA_GRAPH_COLORS trong file JS."""
    out, model, field = {}, None, None
    body = js.split('var SLA_GRAPH_COLORS', 1)[1].split('/**', 1)[0]
    for line in body.splitlines():
        m = re.match(r'^    "([\w.]+)": \{', line)
        if m:
            model = m.group(1)
            out[model] = {}
            continue
        f = re.match(r'^        (\w+): \{', line)
        if f:
            field = f.group(1)
            out[model][field] = set()
            continue
        v = re.match(r'^            "?(\w+)"?: "#[0-9a-f]{6}",', line)
        if v:
            out[model][field].add(v.group(1))
    return out


@tagged('post_install', '-at_install', 'dwo_sla_core', 'tg_36')
class TestGraphColors(TransactionCase):

    def test_palette_covers_every_selection_value(self):
        path = get_module_path(MODULE) + '/static/src/graph_colors/sla_graph_colors.js'
        with open(path) as f:
            palette = _palette(f.read())
        for model, fields_ in palette.items():
            for fname, values in fields_.items():
                keys = {k for k, _l in self.env[model]._fields[fname].selection}
                self.assertEqual(values, keys, "%s.%s" % (model, fname))
        self.assertEqual(set(palette['sla.task']), {'outcome', 'stage', 'usage_bucket'})

    def test_outcome_selection_order_is_stack_order(self):
        keys = [k for k, _l in self.env['sla.task']._fields['outcome'].selection]
        self.assertEqual(keys[:3], ['on_time', 'late', 'breached_open'])

    def test_rate_measure_is_percentage_in_graph_and_pivot(self):
        for xmlid in ('view_sla_report_trend_graph', 'view_sla_report_trend_pivot'):
            arch = self.env.ref('%s.%s' % (MODULE, xmlid)).arch
            node = etree.fromstring(arch).xpath("//field[@name='achieved_rate']")[0]
            self.assertEqual(node.get('widget'), 'percentage', xmlid)

    def test_asset_registered(self):
        manifest = get_module_path(MODULE) + '/__manifest__.py'
        with open(get_module_path(MODULE) + '/views/assets.xml') as f:
            self.assertIn('static/src/graph_colors/sla_graph_colors.js', f.read())

    def test_line_graphs_are_not_stacked(self):
        """Task 029: R2 and R9 lines plot one rate per definition/source, never cumulated."""
        for xmlid in ('view_sla_report_trend_graph', 'view_sla_report_heatmap_graph'):
            root = etree.fromstring(self.env.ref('%s.%s' % (MODULE, xmlid)).arch)
            self.assertEqual(root.get('type'), 'line', xmlid)
            self.assertEqual(root.get('stacked'), '0', xmlid)
        # the bar graphs of the outcome are meant to stack
        for xmlid in ('view_sla_report_distribution_graph', 'view_sla_report_performance_graph'):
            root = self.env.ref('%s.%s' % (MODULE, xmlid))
            self.assertNotEqual(etree.fromstring(root.arch).get('stacked'), '0', xmlid)

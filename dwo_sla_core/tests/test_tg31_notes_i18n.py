# -*- coding: utf-8 -*-
"""TG-31: tab Note của form definition/task, chuỗi lỗi thời, bản dịch ja_JP.

Refs: docs/plan-improvement-sla-01.md §3.4, §3.18.1; review §6.4
"""
import os

from lxml import etree

from odoo.tests import tagged

from .common import SlaCase
from .test_tg14_infra import MODULE_PATH

TAGS = ('post_install', '-at_install', 'dwo_sla_core')


class Tg31Case(SlaCase):

    def note(self, model):
        arch = self.env[model].fields_view_get(view_type='form')['arch']
        pages = etree.fromstring(arch).xpath("//page[@name='note']")
        self.assertEqual(len(pages), 1, model)
        return ' '.join(''.join(pages[0].itertext()).split())


@tagged(*TAGS, 'tg_31')
class TestNotePages(Tg31Case):

    def test_definition_note_has_nine_groups(self):
        arch = self.env['sla.definition'].fields_view_get(view_type='form')['arch']
        headings = etree.fromstring(arch).xpath("//page[@name='note']//h4")
        self.assertEqual(len(headings), 9)

    def test_definition_note_content(self):
        text = self.note('sla.definition')
        for expected in (
                "Match all records",            # [] không phải match-all
                "[('id', '!=', 0)]",
                "not kept in sync",             # bản sao calendar không tự đồng bộ
                "public holidays",
                "reload the page",              # chip cho model mới
                "Re-check Conditions",
                "equal to or longer than the Duration",   # due soon >= duration
                "Disable"):
            self.assertIn(expected, text)

    def test_task_note_has_four_groups_and_three_scenarios(self):
        arch = self.env['sla.task'].fields_view_get(view_type='form')['arch']
        page = etree.fromstring(arch).xpath("//page[@name='note']")[0]
        self.assertEqual(len(page.xpath(".//h4")), 4)
        self.assertEqual(len(page.xpath(".//ol/li")), 3)
        text = self.note('sla.task')
        for expected in ("Apply Current Settings", "Re-check Conditions", "Original Breach Time",
                         "from the moment you press the button", "creates a new one"):
            self.assertIn(expected, text)


@tagged(*TAGS, 'tg_31')
class TestNoStaleButtonNames(SlaCase):

    def test_no_old_button_names_in_user_strings(self):
        """Mọi chuỗi hiển thị không còn nhắc nút cũ "Recalculate"/"Re-evaluate"."""
        with open(os.path.join(MODULE_PATH, 'constants', 'message.py')) as handle:
            text = handle.read()
        self.assertNotRegex(text, r'\\"(Recalculate|Re-evaluate)\\"')
        for model in ('sla.definition', 'sla.task', 'sla.escalation'):
            for name, values in self.env[model].fields_get(attributes=['help']).items():
                help_text = values.get('help') or ''
                self.assertNotIn('Recalculate', help_text, '%s.%s' % (model, name))
                self.assertNotIn('Re-evaluate', help_text, '%s.%s' % (model, name))
        for xml in ('sla_definition_views.xml', 'sla_task_views.xml'):
            path = os.path.join(MODULE_PATH, 'views', xml)
            with open(path) as handle:
                text = handle.read()
            self.assertNotRegex(text, r'string="(Recalculate|Re-evaluate)"')
            self.assertNotIn('"Re-evaluate"', text)

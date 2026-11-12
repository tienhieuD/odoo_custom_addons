# -*- coding: utf-8 -*-
"""TG-21: field metadata mới (type, vendor_id, service_commitment, target) -- scope-add.

Chỉ kiểm lưu/đọc đúng giá trị và default; các field này không ảnh hưởng Engine
(xem 031_scope_additions_contract_sla_fields.md).
"""
from odoo.tests import tagged

from .common import SlaCase

TAGS = ('post_install', '-at_install', 'dwo_sla_core')


@tagged(*TAGS, 'tg_21')
class TestNewMetadataFields(SlaCase):

    def test_type_default_sla(self):
        d = self.make_definition()
        self.assertEqual(d.type, 'sla')

    def test_type_ola(self):
        d = self.make_definition(type='ola')
        self.assertEqual(d.type, 'ola')

    def test_vendor_id_set(self):
        vendor = self.env['res.partner'].create({'name': "Vendor Co"})
        d = self.make_definition(vendor_id=vendor.id)
        self.assertEqual(d.vendor_id, vendor)

    def test_vendor_id_default_empty(self):
        d = self.make_definition()
        self.assertFalse(d.vendor_id)

    def test_service_commitment_default_false(self):
        d = self.make_definition()
        self.assertFalse(d.service_commitment)

    def test_service_commitment_true(self):
        d = self.make_definition(service_commitment=True)
        self.assertTrue(d.service_commitment)

    def test_target_default_empty(self):
        d = self.make_definition()
        self.assertFalse(d.target)

    def test_target_response(self):
        d = self.make_definition(target='response')
        self.assertEqual(d.target, 'response')

    def test_target_resolution(self):
        d = self.make_definition(target='resolution')
        self.assertEqual(d.target, 'resolution')

    def test_metadata_fields_do_not_change_engine_behaviour(self):
        """type/vendor_id/service_commitment/target không ảnh hưởng việc gắn SLA."""
        d = self.make_definition(type='ola', service_commitment=True, target='response')
        p = self.make_partner('NEW')
        t = self.task_of(p, d)
        self.assertEqual(t.stage, 'in_progress')

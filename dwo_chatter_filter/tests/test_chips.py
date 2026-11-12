# -*- coding: utf-8 -*-
import glob
import importlib.util
import os
import random

from odoo.addons.mail.tests.common import MailCommon
from odoo.addons.dwo_chatter_filter.models.dwo_chatter_filter import (
    HEX_COLOR, MAX_LUMINANCE, _hue_of, _luminance, pick_color)
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged


def _lum(color):
    return _luminance(*(int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)))


@tagged("post_install", "-at_install", "dwo_chatter_filter")
class TestChatterFilterChips(MailCommon):
    @property
    def _thread_domain(self):
        return [("model", "=", "res.partner"), ("res_id", "=", self.record.id)]


    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Chip = cls.env["dwo.chatter.filter"]
        quiet = cls.env["res.partner"].with_context(mail_create_nolog=True, mail_notrack=True)
        cls.record = quiet.create({"name": "Chip record"})
        mt_comment = cls.env.ref("mail.mt_comment")
        base = {"model": "res.partner", "res_id": cls.record.id, "body": "<p>x</p>"}
        cls.quote_1 = cls.env["mail.message"].create(dict(base, body="<p>Quote Q-1</p>", message_type="comment",
                                                          subtype_id=mt_comment.id))
        cls.quote_2 = cls.env["mail.message"].create(dict(base, body="<p>Quote Q-2</p>", message_type="comment",
                                                          subtype_id=mt_comment.id))
        cls.other = cls.env["mail.message"].create(dict(base, body="<p>Hello</p>", message_type="comment",
                                                        subtype_id=mt_comment.id))
        cls.admin = cls.env.ref("base.user_admin")

    # ---- the chips that come with the module

    def test_the_module_comes_with_six_chips_in_the_old_order(self):
        chips = self.Chip.search([])
        self.assertEqual(chips.mapped("name"),
                         ["Discussions", "Emails", "Activities", "Notes", "Tracking", "Other"])
        self.assertEqual(chips.mapped("color"),
                         ["#71639e", "#17a2b8", "#6f42c1", "#ffac00", "#28a745", "#dc3545"])

    def test_the_upgrade_creates_the_six_chips_once(self):
        # the post-migrate script of this version: a database that had the fixed badges gets the six chips
        path = glob.glob(os.path.join(os.path.dirname(os.path.dirname(__file__)), "migrations", "*", "post-migrate.py"))[0]
        spec = importlib.util.spec_from_file_location("dwo_chatter_filter_post_migrate", path)
        script = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script)
        self.Chip.with_context(active_test=False).search([]).unlink()
        script.migrate(self.env.cr, "1.1.0")
        self.assertEqual(self.Chip.search([]).mapped("name"),
                         ["Discussions", "Emails", "Activities", "Notes", "Tracking", "Other"])
        # a chip deleted afterwards is only gone: the update never creates it again (forcecreate="0")
        self.Chip.search([("name", "=", "Other")]).unlink()
        self.assertEqual(len(self.Chip.search([])), 5)

    # ---- who can edit

    def test_an_employee_reads_but_cannot_write_create_or_delete(self):
        chip = self.env.ref("dwo_chatter_filter.dwo_filter_email").with_user(self.user_employee)
        self.assertEqual(chip.name, "Emails")
        with self.assertRaises(AccessError):
            chip.write({"name": "Mine"})
        with self.assertRaises(AccessError):
            self.Chip.with_user(self.user_employee).create({"name": "New"})
        with self.assertRaises(AccessError):
            chip.unlink()

    def test_an_administrator_creates_edits_archives_and_deletes(self):
        Chip = self.Chip.with_user(self.admin)
        chip = Chip.create({"name": "Quotes", "domain": "[('body', 'ilike', 'Quote')]"})
        chip.write({"name": "Offers"})
        self.assertEqual(chip.name, "Offers")
        chip.active = False
        self.assertFalse(chip.active)
        chip.unlink()
        self.assertFalse(chip.exists())

    # ---- the domain and the colour are checked

    def test_a_filter_that_does_not_work_is_refused(self):
        with self.assertRaises(ValidationError):
            self.Chip.create({"name": "Bad field", "domain": "[('no_such_field', '=', 1)]"})
        with self.assertRaises(ValidationError):
            self.Chip.create({"name": "Not a domain", "domain": "this is not python"})
        with self.assertRaises(ValidationError):
            self.Chip.create({"name": "Bad colour", "color": "red"})

    # ---- a chip filters the messages of a record

    def test_a_new_chip_counts_and_filters(self):
        chip = self.Chip.create({"name": "Quotes", "domain": "[('body', 'ilike', 'Quote')]"})
        Message = self.env["mail.message"].with_user(self.user_employee)
        result = Message.dwo_filter_chips("res.partner", self.record.id)
        by_name = {c["name"]: c for c in result["chips"]}
        self.assertEqual(by_name["Quotes"]["count"], 2)
        fetched = Message.message_fetch(self._thread_domain + [("dwo_filter_id", "=", chip.id)])
        self.assertEqual({m["id"] for m in fetched}, {self.quote_1.id, self.quote_2.id})

    def test_a_message_can_be_in_several_chips(self):
        self.Chip.create({"name": "Quote 1", "domain": "[('body', 'ilike', 'Q-1')]"})
        self.Chip.create({"name": "Quotes", "domain": "[('body', 'ilike', 'Quote')]"})
        result = self.env["mail.message"].with_user(self.user_employee).dwo_filter_chips("res.partner", self.record.id)
        by_name = {c["name"]: c["count"] for c in result["chips"]}
        self.assertEqual((by_name["Quote 1"], by_name["Quotes"]), (1, 2))

    def test_a_chip_that_breaks_later_has_no_number_and_the_others_still_work(self):
        chip = self.Chip.create({"name": "Quotes", "domain": "[('body', 'ilike', 'Quote')]"})
        # the field disappears (a module was removed): written in SQL, the constraint cannot see it
        self.env.cr.execute("UPDATE dwo_chatter_filter SET domain = %s WHERE id = %s",
                            ("[('gone_field', '=', 1)]", chip.id))
        self.Chip.invalidate_cache()
        result = self.env["mail.message"].with_user(self.user_employee).dwo_filter_chips("res.partner", self.record.id)
        by_name = {c["name"]: c["count"] for c in result["chips"]}
        self.assertIsNone(by_name["Quotes"])
        self.assertEqual(by_name["Emails"], 0)
        # fetching with that chip shows everything instead of failing
        fetched = self.env["mail.message"].with_user(self.user_employee).message_fetch(
            self._thread_domain + [("dwo_filter_id", "=", chip.id)])
        self.assertEqual(len(fetched), 3)

    def test_an_archived_chip_is_not_shown(self):
        self.env.ref("dwo_chatter_filter.dwo_filter_other").active = False
        names = [c["name"] for c in self.env["mail.message"].with_user(self.user_employee)
                 .dwo_filter_chips("res.partner", self.record.id)["chips"]]
        self.assertNotIn("Other", names)
        self.assertEqual(len(names), 5)

    def test_no_more_than_fifteen_chips_are_shown(self):
        for i in range(20):
            self.Chip.create({"name": "Chip %s" % i})
        result = self.env["mail.message"].with_user(self.user_employee).dwo_filter_chips("res.partner", self.record.id)
        self.assertEqual(len(result["chips"]), 15)

    # ---- the order

    def test_dragging_a_line_changes_the_order(self):
        chips = self.Chip.search([])
        order = chips.ids
        # before Odoo 19 the list writes the sequence of the lines it moved (no web_resequence yet)
        first, second = chips[0], chips[1]
        sequences = (first.sequence, second.sequence)
        first.with_user(self.admin).write({"sequence": sequences[1]})
        second.with_user(self.admin).write({"sequence": sequences[0]})
        names = [c["name"] for c in self.env["mail.message"].with_user(self.user_employee)
                 .dwo_filter_chips("res.partner", self.record.id)["chips"]]
        self.assertEqual(names[:2], ["Emails", "Discussions"])
        self.assertEqual(self.Chip.search([]).ids, [order[1], order[0]] + order[2:])

    def test_a_new_chip_goes_last(self):
        chip = self.Chip.create({"name": "Last"})
        self.assertEqual(self.Chip.search([]).ids[-1], chip.id)

    # ---- the colour of a new chip

    def test_the_default_colour_is_new_and_readable_on_white(self):
        used = list(self.Chip.search([]).mapped("color"))
        for _ in range(20):
            color = self.Chip.default_get(["color"])["color"]
            self.assertRegex(color, HEX_COLOR)
            self.assertLessEqual(_lum(color), MAX_LUMINANCE + 0.002)   # contrast with white >= 4.5
            # not the hue of a chip that exists, by at least 12 degrees on the colour circle
            for other in used:
                gap = abs(_hue_of(color) - _hue_of(other))
                self.assertGreater(min(gap, 1 - gap), 12 / 360, "%s too close to %s" % (color, other))

    def test_colours_picked_one_after_the_other_stay_apart(self):
        rng = random.Random(7)
        used = []
        for _ in range(8):
            used.append(pick_color(used, rng))
        hues = sorted(_hue_of(c) for c in used)
        gaps = [(hues[(i + 1) % 8] - hues[i]) % 1 for i in range(8)]
        self.assertGreater(min(gaps), 0.04)
        for color in used:
            self.assertLessEqual(_lum(color), MAX_LUMINANCE + 0.002)

# -*- coding: utf-8 -*-
import copy

from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests.common import TransactionCase

from .test_spec import page as sample_page, widget


class DashboardCase(TransactionCase):

    def setUp(self):
        super().setUp()
        Users = self.env["res.users"]
        group = self.env.ref("base.group_user")
        self.alice = Users.create({"name": "Alice", "login": "dash_alice", "group_ids": [(6, 0, [group.id])]})
        self.bob = Users.create({"name": "Bob", "login": "dash_bob", "group_ids": [(6, 0, [group.id])]})
        self.Dashboard = self.env["dwo.dashboard"]
        self.Page = self.env["dwo.dashboard.page"]

    def as_(self, user, model="dwo.dashboard"):
        return self.env(user=user)[model]


class TestDashboardModels(DashboardCase):

    def test_first_use_creates_one_dashboard_with_a_home_page(self):
        first = self.as_(self.alice).get_my_dashboard()
        self.assertEqual([p["name"] for p in first["pages"]], ["Home"])
        again = self.as_(self.alice).get_my_dashboard()
        self.assertEqual(first["id"], again["id"])  # idempotent
        self.assertEqual(self.Dashboard.search_count([("user_id", "=", self.alice.id)]), 1)

    def test_a_new_page_goes_to_the_end(self):
        mine = self.as_(self.alice).get_my_dashboard()
        Page = self.as_(self.alice, "dwo.dashboard.page")
        Page.reorder([mine["pages"][0]["id"]])
        second = Page.create({"dashboard_id": mine["id"], "name": "Second"})
        third = Page.create({"dashboard_id": mine["id"], "name": "Third"})
        names = [p["name"] for p in self.as_(self.alice).get_my_dashboard()["pages"]]
        self.assertEqual(names, ["Home", "Second", "Third"])
        self.assertLess(second.sequence, third.sequence)

    def test_a_user_has_one_dashboard(self):
        self.Dashboard.create({"user_id": self.alice.id})
        with self.assertRaises(Exception):
            self.Dashboard.create({"user_id": self.alice.id})

    def test_pages_are_private(self):
        mine = self.as_(self.alice).get_my_dashboard()
        theirs = self.as_(self.bob).get_my_dashboard()
        self.assertNotEqual(mine["id"], theirs["id"])
        alice_page = mine["pages"][0]["id"]
        # Bob cannot read, write, delete or find Alice's page
        PageBob = self.as_(self.bob, "dwo.dashboard.page")
        self.assertEqual(PageBob.search([("id", "=", alice_page)]), PageBob.browse())
        with self.assertRaises(AccessError):
            PageBob.get_page(alice_page)
        with self.assertRaises(AccessError):
            PageBob.browse(alice_page).write({"name": "mine now"})
        with self.assertRaises(AccessError):
            PageBob.browse(alice_page).unlink()
        with self.assertRaises(AccessError):
            self.as_(self.bob).browse(mine["id"]).write({"name": "x"})

    def test_nobody_creates_a_dashboard_or_page_for_somebody_else(self):
        with self.assertRaises(AccessError):  # Bob has none yet: only the record rule can refuse
            self.as_(self.alice).create({"user_id": self.bob.id})
        bob_dashboard = self.as_(self.bob).get_my_dashboard()["id"]
        with self.assertRaises(AccessError):
            self.as_(self.alice, "dwo.dashboard.page").create({"dashboard_id": bob_dashboard, "name": "intruder"})

    def test_the_owner_cannot_hand_over_a_dashboard_or_move_a_page(self):
        mine = self.as_(self.alice).get_my_dashboard()
        with self.assertRaises(AccessError):
            self.as_(self.alice).browse(mine["id"]).write({"user_id": self.bob.id})
        other = self.as_(self.bob).get_my_dashboard()["id"]
        with self.assertRaises(AccessError):
            self.as_(self.alice, "dwo.dashboard.page").browse(mine["pages"][0]["id"]).write({"dashboard_id": other})

    def test_administrators_do_not_read_private_dashboards_either(self):
        admin = self.env.ref("base.user_admin")
        mine = self.as_(self.alice).get_my_dashboard()
        self.assertEqual(self.as_(admin, "dwo.dashboard.page").search([("id", "=", mine["pages"][0]["id"])]).ids, [])

    def test_a_portal_user_has_no_access(self):
        portal = self.env["res.users"].create({"name": "Pat", "login": "dash_pat2",
                                               "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])]})
        with self.assertRaises(AccessError):
            self.as_(portal).get_my_dashboard()


class TestPages(DashboardCase):

    def setUp(self):
        super().setUp()
        self.Mine = self.as_(self.alice, "dwo.dashboard.page")
        self.dashboard = self.as_(self.alice).get_my_dashboard()
        self.home = self.Mine.browse(self.dashboard["pages"][0]["id"])

    def test_a_valid_spec_is_saved_and_the_revision_grows(self):
        spec = sample_page("attachments_usage")
        result = self.home.save_spec(spec, 1)
        self.assertEqual(result, {"revision": 2})
        self.assertEqual(self.Mine.get_page(self.home.id)["spec"], spec)

    def test_an_invalid_spec_is_refused_with_the_pointer_of_the_error(self):
        spec = sample_page("attachments_usage")
        widget(spec, "files")["dataset"] = "orm:no.such.model"
        with self.assertRaisesRegex(ValidationError, "/widgets/0/dataset"):
            self.home.save_spec(spec, 1)
        self.assertEqual(self.home.revision, 1)  # refused before anything was written

    def test_the_spec_is_validated_as_the_writer_not_as_sudo(self):
        spec = sample_page("attachments_usage")
        widget(spec, "files")["dataset"] = "orm:ir.cron"  # an internal user cannot read it
        with self.assertRaisesRegex(ValidationError, "not available to you"):
            self.home.save_spec(spec, 1)
        self.assertEqual(self.home.revision, 1)
        with self.assertRaisesRegex(ValidationError, "not available to you"):  # create, too
            self.Mine.create({"dashboard_id": self.dashboard["id"], "name": "x", "spec": spec})
        self.home.sudo().write({"spec": spec})  # the backstop constraint (superuser) lets it pass: the model exists

    def test_a_plain_write_of_the_spec_also_counts_a_revision_and_is_validated(self):
        self.home.write({"spec": sample_page("attachments_usage")})
        self.assertEqual(self.home.revision, 2)
        bad = copy.deepcopy(sample_page("attachments_usage"))
        bad["widgets"][0]["x"] = 99
        with self.assertRaises(ValidationError):
            self.home.write({"spec": bad})

    def test_a_save_from_a_stale_tab_does_not_overwrite(self):
        self.home.save_spec(sample_page("attachments_usage"), 1)
        with self.assertRaisesRegex(UserError, "changed somewhere else"):
            self.home.save_spec({"schema": "dwo-dashboard/1", "widgets": []}, 1)
        self.assertEqual(len(self.home.spec["widgets"]), 4)

    def test_a_huge_spec_is_refused(self):
        spec = {"schema": "dwo-dashboard/1", "widgets": [], "description": "x" * 600}
        with self.assertRaises(ValidationError):
            self.home.save_spec(spec, 1)  # the description is longer than allowed: shape error, not size
        from ..models import dwo_dashboard as module
        with self.assertRaisesRegex(ValidationError, "too large"):
            with __import__("unittest.mock").mock.patch.object(module, "MAX_SPEC_BYTES", 10):
                self.home.save_spec(sample_page("attachments_usage"), 1)

    def test_duplicate_page(self):
        self.home.save_spec(sample_page("attachments_usage"), 1)
        summary = self.home.duplicate_page()
        copy_ = self.Mine.browse(summary["id"])
        self.assertEqual(copy_.name, "Home (copy)")
        self.assertEqual(copy_.spec, self.home.spec)
        self.assertEqual(copy_.dashboard_id, self.home.dashboard_id)
        copy_.spec["widgets"].clear()  # independent copies

    def test_at_most_thirty_pages(self):
        for i in range(29):
            self.Mine.create({"dashboard_id": self.dashboard["id"], "name": "P%d" % i})
        with self.assertRaisesRegex(ValidationError, "at most 30"):
            self.Mine.create({"dashboard_id": self.dashboard["id"], "name": "one too many"})

    def test_a_category_is_a_heading_not_a_page(self):
        divider = self.Mine.create({"dashboard_id": self.dashboard["id"], "name": "Team", "kind": "divider"})
        for call in (lambda: self.Mine.get_page(divider.id), lambda: divider.duplicate_page(),
                     lambda: divider.save_spec(sample_page("attachments_usage"), 1),
                     lambda: divider.share_with([self.bob.id], [], "view")):
            with self.assertRaises(UserError):
                call()
        # it does not count as a page, nor does it appear for other people
        for i in range(29):
            self.Mine.create({"dashboard_id": self.dashboard["id"], "name": "P%d" % i})
        self.assertEqual(len(self.as_(self.alice).get_my_dashboard()["pages"]), 1 + 29 + 1)
        self.assertEqual(self.as_(self.bob).get_my_dashboard()["shared"], [])

    def test_at_most_thirty_categories(self):
        for i in range(30):
            self.Mine.create({"dashboard_id": self.dashboard["id"], "name": "D%d" % i, "kind": "divider"})
        with self.assertRaisesRegex(ValidationError, "at most 30 categories"):
            self.Mine.create({"dashboard_id": self.dashboard["id"], "name": "one too many", "kind": "divider"})

    def test_favorites_and_folding_are_the_owners(self):
        divider = self.Mine.create({"dashboard_id": self.dashboard["id"], "name": "Team", "kind": "divider"})
        second = self.Mine.create({"dashboard_id": self.dashboard["id"], "name": "Second"})
        (self.home | second).write({"favorite": True})
        self.Mine.reorder_favorites([second.id, self.home.id])
        self.assertEqual([second.fav_sequence, self.home.fav_sequence], [10, 20])
        divider.write({"collapsed": True})
        self.assertEqual(self.home.revision, 1)  # a fold or a star is not a new revision of the page
        self.Mine.reorder_favorites([self.home.id])
        # somebody else cannot star or fold what is not theirs, nor order it
        self.home.share_with([self.bob.id], [], "edit")
        as_bob = self.as_(self.bob, "dwo.dashboard.page").browse(self.home.id)
        with self.assertRaises(AccessError):
            as_bob.write({"favorite": False})
        with self.assertRaises(AccessError):
            self.as_(self.bob, "dwo.dashboard.page").reorder_favorites([self.home.id])

    def test_reorder_only_my_pages(self):
        second = self.Mine.create({"dashboard_id": self.dashboard["id"], "name": "Second"})
        self.Mine.reorder([second.id, self.home.id])
        self.assertEqual([p["name"] for p in self.as_(self.alice).get_my_dashboard()["pages"]], ["Second", "Home"])
        bob_page = self.as_(self.bob).get_my_dashboard()["pages"][0]["id"]
        with self.assertRaises(AccessError):
            self.Mine.reorder([bob_page])

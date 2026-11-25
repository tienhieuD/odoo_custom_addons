# -*- coding: utf-8 -*-
from psycopg2 import IntegrityError

from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from .test_engine import kpi


class SharingCase(TransactionCase):

    def setUp(self):
        super().setUp()
        Users = self.env["res.users"]
        internal = self.env.ref("base.group_user")
        mk = lambda login, groups=(): Users.create({"name": login.title(), "login": login,
                                                    "group_ids": [(6, 0, [internal.id] + [g.id for g in groups])]})
        self.team = self.env["res.groups"].create({"name": "Dash team"})
        self.owner, self.viewer, self.editor = mk("sh_owner"), mk("sh_viewer"), mk("sh_editor")
        self.member, self.ex_member, self.stranger = mk("sh_member", [self.team]), mk("sh_ex", [self.team]), mk("sh_stranger")
        self.portal = Users.create({"name": "Pat", "login": "sh_portal", "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])]})
        self.admin = self.env.ref("base.user_admin")
        mine = self.as_(self.owner).get_my_dashboard()
        self.page_id = mine["pages"][0]["id"]
        self.page = self.as_(self.owner, "dwo.dashboard.page").browse(self.page_id)
        self.page.write({"spec": {"schema": "dwo-dashboard/1", "grid": {"cols": 12},
                                  "widgets": [dict(kpi("k"), x=0, y=0, w=3, h=2)]}})
        self.page.share_with([self.viewer.id], [], "view")
        self.page.share_with([self.editor.id], [], "edit")
        self.page.share_with([], [self.team.id], "view")

    def as_(self, user, model="dwo.dashboard"):
        return self.env(user=user)[model]

    def P(self, user):
        return self.as_(user, "dwo.dashboard.page").browse(self.page_id)


class TestSharingAccess(SharingCase):

    def test_who_can_read(self):
        for user in (self.owner, self.viewer, self.editor, self.member, self.ex_member):
            self.assertEqual(self.as_(user, "dwo.dashboard.page").get_page(self.page_id)["id"], self.page_id, user.login)
        for user in (self.stranger, self.admin):
            with self.assertRaises(AccessError, msg=user.login):
                self.as_(user, "dwo.dashboard.page").get_page(self.page_id)
        with self.assertRaises(AccessError):
            self.as_(self.portal, "dwo.dashboard.page").get_page(self.page_id)

    def test_levels(self):
        lv = lambda u: self.as_(u, "dwo.dashboard.page").get_page(self.page_id)["level"]
        self.assertEqual([lv(u) for u in (self.owner, self.viewer, self.editor, self.member)],
                         ["owner", "view", "edit", "view"])

    def test_a_group_member_who_leaves_the_group_loses_the_page(self):
        self.ex_member.write({"group_ids": [(3, self.team.id)]})
        with self.assertRaises(AccessError):
            self.as_(self.ex_member, "dwo.dashboard.page").get_page(self.page_id)

    def test_revoking_removes_access_at_once(self):
        share = self.page.share_ids.filtered(lambda s: s.user_id == self.viewer)
        self.page.revoke_share(share.id)
        with self.assertRaises(AccessError):
            self.as_(self.viewer, "dwo.dashboard.page").get_page(self.page_id)

    def test_a_viewer_cannot_change_anything(self):
        with self.assertRaises(AccessError):
            self.P(self.viewer).save_spec({"schema": "dwo-dashboard/1", "widgets": []}, self.P(self.owner).revision)
        for vals in ({"name": "x"}, {"sequence": 99}):
            with self.assertRaises(AccessError):
                self.P(self.viewer).write(vals)
        with self.assertRaises(AccessError):
            self.P(self.viewer).unlink()

    def test_an_editor_changes_the_content_only(self):
        page = self.P(self.editor)
        page.save_spec({"schema": "dwo-dashboard/1", "grid": {"cols": 12}, "widgets": []}, page.revision)
        self.assertEqual(self.page.spec["widgets"], [])
        for vals in ({"name": "mine"}, {"sequence": 99}, {"dashboard_id": self.as_(self.editor).get_my_dashboard()["id"]}):
            with self.assertRaises(AccessError):
                page.write(vals)
        with self.assertRaises(AccessError):
            page.unlink()

    def test_reorder_is_for_the_owner(self):
        with self.assertRaises(AccessError):
            self.as_(self.editor, "dwo.dashboard.page").reorder([self.page_id])
        self.assertTrue(self.as_(self.owner, "dwo.dashboard.page").reorder([self.page_id]))

    def test_only_the_owner_manages_shares(self):
        for user in (self.viewer, self.editor, self.member, self.stranger):
            page = self.P(user)
            with self.assertRaises(AccessError, msg=user.login):
                page.share_with([self.stranger.id], [], "edit")
            with self.assertRaises(AccessError, msg=user.login):
                page.get_shares()
            with self.assertRaises(AccessError, msg=user.login):
                page.revoke_share(self.page.share_ids[0].id)
        Share = self.as_(self.viewer, "dwo.dashboard.share")
        with self.assertRaises(AccessError):  # a viewer cannot grant themselves more
            Share.create({"page_id": self.page_id, "user_id": self.stranger.id, "level": "edit"})
        mine = Share.search([("user_id", "=", self.viewer.id)])
        self.assertEqual(len(mine), 1)  # the recipient sees their own share only
        with self.assertRaises(AccessError):
            mine.write({"level": "edit"})
        with self.assertRaises(AccessError):
            mine.unlink()

    def test_a_share_cannot_be_moved(self):
        other = self.as_(self.owner, "dwo.dashboard.page").create({
            "dashboard_id": self.as_(self.owner).get_my_dashboard()["id"], "name": "Other"})
        share = self.as_(self.owner, "dwo.dashboard.share").search([("page_id", "=", self.page_id), ("user_id", "=", self.viewer.id)])
        for vals in ({"page_id": other.id}, {"user_id": self.stranger.id}, {"group_id": self.team.id}):
            with self.assertRaises(AccessError):
                share.write(vals)
        share.write({"level": "edit"})
        self.assertEqual(self.P(self.viewer).get_page(self.page_id)["level"], "edit")

    def test_who_can_be_a_recipient(self):
        Share = self.as_(self.owner, "dwo.dashboard.share")
        with self.assertRaises(ValidationError):
            Share.create({"page_id": self.page_id, "user_id": self.portal.id})
        with self.assertRaises(ValidationError):
            Share.create({"page_id": self.page_id, "user_id": self.owner.id})
        with self.assertRaises(ValidationError):
            Share.create({"page_id": self.page_id, "group_id": self.env.ref("base.group_portal").id})
        with self.assertRaises(ValidationError):
            Share.create({"page_id": self.page_id, "group_id": self.env.ref("base.group_public").id})
        with self.assertRaises(UserError):
            self.page.share_with([self.stranger.id], [], "owner")
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError), self.env.cr.savepoint():
            Share.create({"page_id": self.page_id, "user_id": self.stranger.id, "group_id": self.team.id})

    def test_share_twice_changes_the_level(self):
        self.page.share_with([self.viewer.id], [], "edit")
        self.assertEqual(self.P(self.viewer).get_page(self.page_id)["level"], "edit")
        self.assertEqual(len(self.page.share_ids.filtered(lambda s: s.user_id == self.viewer)), 1)

    def test_listing_and_search(self):
        mine = self.as_(self.viewer).get_my_dashboard()
        self.assertEqual([p["id"] for p in mine["shared"]], [self.page_id])
        self.assertEqual(mine["shared"][0]["owner"], "Sh_Owner")
        self.assertNotIn(self.page_id, [p["id"] for p in mine["pages"]])
        self.assertEqual(self.as_(self.stranger).get_my_dashboard()["shared"], [])
        found = self.as_(self.owner, "dwo.dashboard.page").search_recipients("sh_v")
        self.assertEqual([u["name"] for u in found["users"]], ["Sh_Viewer"])
        names = [u["name"] for u in self.as_(self.owner, "dwo.dashboard.page").search_recipients("")["users"]]
        self.assertNotIn("Pat", names)

    def test_a_copy_goes_to_my_dashboard(self):
        copy_ = self.P(self.viewer).duplicate_page()
        mine = self.as_(self.viewer).get_my_dashboard()
        self.assertIn(copy_["id"], [p["id"] for p in mine["pages"]])
        self.assertEqual(copy_["level"], "owner")
        self.assertEqual(self.as_(self.owner).get_my_dashboard()["pages"][0]["id"], self.page_id)
        self.assertEqual(len(self.as_(self.owner).get_my_dashboard()["pages"]), 1)  # nothing landed in the owner's dashboard

    def test_widgets_run_as_the_viewer(self):
        Engine = lambda u: self.as_(u, "dwo.dashboard.engine")
        self.assertTrue(Engine(self.viewer).run_widget(self.page_id, "k")["ok"])
        denied = Engine(self.stranger).run_widget(self.page_id, "k")
        self.assertEqual((denied["ok"], denied["error"]["code"]), (False, "access"))

    def test_the_log(self):
        log = self.as_(self.owner, "dwo.dashboard.page").share_log()
        self.assertEqual({(r["action"], r["target"], r["level"]) for r in log},
                         {("grant", "Sh_Viewer", "view"), ("grant", "Sh_Editor", "edit"), ("grant", "Dash team", "view")})
        self.page.revoke_share(self.page.share_ids[0].id)
        self.assertEqual(self.as_(self.owner, "dwo.dashboard.page").share_log()[0]["action"], "revoke")
        self.assertEqual(self.as_(self.viewer, "dwo.dashboard.page").share_log(), [])
        other = self.as_(self.owner, "dwo.dashboard.page").create({
            "dashboard_id": self.as_(self.owner).get_my_dashboard()["id"], "name": "Other"})
        other.share_with([self.viewer.id], [], "view")
        mine = self.as_(self.owner, "dwo.dashboard.page")
        self.assertEqual({r["page_name"] for r in mine.share_log(self.page_id)}, {self.page.name})
        self.assertEqual({r["page_name"] for r in mine.share_log(other.id)}, {"Other"})  # nobody reads somebody else's log

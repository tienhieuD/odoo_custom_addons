from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    dwo_protect_limits_info = fields.Html(compute="_compute_dwo_protect_limits_info")
    dwo_protect_job_count = fields.Integer(compute="_compute_dwo_protect_job_count")

    # @api.depends_context khong co o ban nay (chi tu 13 tro di) -- bo qua, field nay khong
    # phu thuoc du lieu luu tru nen khong can khai bao depends, chi tinh lai moi lan form
    # Settings duoc mo (luon la ban ghi NewId moi).
    def _compute_dwo_protect_limits_info(self):
        limits = self.env["dwo.protect.job"].get_runtime_limits()
        for record in self:
            if limits["limits_enforced"]:
                enforced = (
                    "<span style='color:#1a7e37'>enforced</span> (server running with "
                    "%d worker process(es))" % limits["workers"]
                )
            else:
                enforced = (
                    "<span style='color:#b55a00'>NOT strictly enforced</span> "
                    "(server running with 0 worker processes — single-process mode)"
                )
            record.dwo_protect_limits_info = (
                "<div style='font-size:0.95em;color:#1F2430;line-height:1.5'>"
                "<p>Protecting a module runs within the same request you trigger it from. "
                "These are the server's current limits for that request — "
                "%s. If protecting a large zip runs longer than a limit below, the request "
                "may be killed and the job will end up in an <b>Error</b> state (try a "
                "smaller zip, or fewer modules per upload).</p>"
                "<ul style='margin-bottom:0'>"
                "<li>CPU time per request: <b>%ss</b></li>"
                "<li>Real time per request: <b>%ss</b></li>"
                "<li>Soft memory limit: <b>%s MB</b></li>"
                "<li>Hard memory limit: <b>%s MB</b></li>"
                "</ul></div>"
            ) % (
                enforced,
                limits["limit_time_cpu"],
                limits["limit_time_real"],
                round((limits["limit_memory_soft"] or 0) / (1024 * 1024)),
                round((limits["limit_memory_hard"] or 0) / (1024 * 1024)),
            )

    def _compute_dwo_protect_job_count(self):
        count = self.env["dwo.protect.job"].search_count([])
        for record in self:
            record.dwo_protect_job_count = count

    def action_dwo_protect_open_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "dwo.protect.source.wizard",
            "view_mode": "form",
            "target": "new",
        }

    def action_dwo_protect_open_jobs(self):
        # _for_xml_id (ir.actions.actions) khong co o ban nay (chi tu 14 tro di) -- tra thang
        # dict act_window, giong het action_dwo_protect_job trong views/dwo_protect_job_views.xml.
        return {
            "type": "ir.actions.act_window",
            "name": "Source Code Protector",
            "res_model": "dwo.protect.job",
            "view_mode": "tree,form",
        }

/* @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { session } from "@web/session";
import { useService } from "@web/core/utils/hooks";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";

const LIMIT = 80;

/**
 * Template menu of the email form. It follows the template menu of the core composer
 * (mail_composer_template_selector): the templates of the user first, then the shared
 * ones, "Search More...", "Save as Template" and "Manage Templates".
 */
export class DwoTemplateDropdown extends Component {
    static template = "dwo_mail_compose.TemplateDropdown";
    static components = { Dropdown, DropdownItem };
    static props = {
        model: String,
        onPick: Function,
        onSave: Function,
    };

    setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        this.dialog = useService("dialog");
        this.limit = LIMIT;
        this.state = useState({ templates: [] });
        onWillStart(() => this.fetchTemplates());
    }

    async fetchTemplates() {
        const fields = ["display_name"];
        const templates = await this.orm.searchRead(
            "mail.template",
            [["model", "=", this.props.model], ["user_id", "=", session.uid]],
            fields,
            { limit: LIMIT }
        );
        if (templates.length < LIMIT) {
            templates.push(
                ...(await this.orm.searchRead(
                    "mail.template",
                    [["model", "=", this.props.model], ["user_id", "=", false]],
                    fields,
                    { limit: LIMIT - templates.length }
                ))
            );
        }
        this.state.templates = templates;
    }

    searchMore() {
        this.dialog.add(SelectCreateDialog, {
            resModel: "mail.template",
            title: _t("Select a Template"),
            multiSelect: false,
            noCreate: true,
            domain: [["model", "=", this.props.model]],
            onSelected: async (templateIds) => {
                const [template] = await this.orm.read("mail.template", [templateIds[0]], ["display_name"]);
                this.props.onPick(template);
            },
        });
    }

    async manage() {
        const action = await this.action.loadAction("mail.action_email_template_tree_all");
        action.context = {
            search_default_my_templates: 1,
            search_default_model: this.props.model,
            default_model: this.props.model,
            default_user_id: session.uid,
        };
        this.action.doAction(action);
    }
}

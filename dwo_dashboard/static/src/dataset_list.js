/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";

/** The list of datasets: a "Create with AI" button next to New (managers only; the wizard checks it again). */
export class DatasetListController extends ListController {
    

    setup() {
        super.setup();
        this.actionService = useService("action");
    }

    createWithAi() {
        this.actionService.doAction("dwo_dashboard.action_dwo_ai_dataset");
    }
}

registry.category("views").add("dwo_dataset_list", { ...listView, Controller: DatasetListController, buttonTemplate: "dwo_dashboard.DatasetListButtons" });

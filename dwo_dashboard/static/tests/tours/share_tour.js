/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
import { registry } from "@web/core/registry";

// The owner shares the page with Vera (view); Vera then opens it from "Shared with me", read only.
registry.category("web_tour.tours").add("dwo_share_owner", {
    steps: () => [
        { trigger: ".dwo-dashboard .dwo-page-item.active .dwo-page-name:contains(Home)" },
        { trigger: ".dwo-share", run: "click" },
        { trigger: ".dwo-share-search", run: "edit Vera" },
        { trigger: ".dwo-share-found .list-group-item:contains(Vera)", run: "click" },
        { trigger: ".dwo-share-list:contains(Vera)" },
        { trigger: ".modal-footer .btn-primary", run: "click" },
    ],
});

registry.category("web_tour.tours").add("dwo_share_viewer", {
    steps: () => [
        { trigger: ".dwo-shared-item .dwo-page-name:contains(Home)", run: "click" },
        { trigger: ".dwo-shared-badge:contains(view only)" },
        { trigger: ".dwo-copy" },
        { trigger: ".dwo-dashboard:not(:has(.dwo-edit)):not(:has(.dwo-add-widget)):not(:has(.dwo-share))" },
    ],
});

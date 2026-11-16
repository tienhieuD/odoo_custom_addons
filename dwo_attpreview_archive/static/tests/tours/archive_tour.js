/** @odoo-module **/
// Copyright 2026 DuoTEK. Licensed under the Odoo Proprietary License v1.0 (OPL-1).
// Odoo 17: tours are added through dwoAddTour (see dwo_attpreview_core/static/tests/tours/tour_compat.js), and the
// 17 tour runner types with run: "text ..." (18/19: "edit ...")
import { dwoAddTour } from "@dwo_attpreview_core/../tests/tours/tour_compat";
// Odoo 18/17: file cards in the chatter are .o-mail-AttachmentCard (19: .o-mail-AttachmentContainer)

function key(el, name) {
    el.dispatchEvent(new KeyboardEvent("keydown", { key: name, code: name, bubbles: true }));
    el.dispatchEvent(new KeyboardEvent("keyup", { key: name, code: name, bubbles: true }));
}

// A zip of 20 002 files: the tree draws only the visible rows, the keyboard reaches the last one, the name filter
// finds a file deep in a folder, and files inside open in their own dialog (a picture, a zip in the zip).
dwoAddTour("dwo_attpreview_archive_tour", {
    steps: () => [
        { trigger: ".o-mail-AttachmentList .o-mail-AttachmentCard", run: "click" },
        { content: "Summary of the archive", trigger: ".modal .o_dwo_arc_stats:contains('20002 files')" },
        { content: "The single top folder is open", trigger: ".modal .o_dwo_tree_row:contains('logo.png')" },
        { content: "Open the folder of 20 000 files", trigger: ".modal .o_dwo_tree_row.o_dwo_tree_folder:contains('docs')", run: "click" },
        {
            content: "Only the visible rows are in the page",
            trigger: ".modal .o_dwo_tree_row:contains('page00000.txt')",
            run() {
                const rows = document.querySelectorAll(".modal .o_dwo_tree_row").length;
                if (rows > 120) {
                    throw new Error(`too many rows in the page: ${rows}`);
                }
            },
        },
        {
            content: "End goes to the last row (the list scrolls to it)",
            trigger: ".modal .o_dwo_tree_row.o_dwo_tree_focused:contains('docs')",
            run() {
                key(this.anchor, "End");
            },
        },
        { content: "Last row focused and drawn", trigger: ".modal .o_dwo_tree_row.o_dwo_tree_focused:contains('logo.png')" },
        { content: "Filter by name", trigger: ".modal .o_dwo_arc_filter", run: "text page01999" },
        { trigger: ".modal .o_dwo_arc_matches:contains('1 found')" },
        { trigger: ".modal .o_dwo_tree_row:contains('page01999.txt')" },
        { content: "Filter on the zip inside", trigger: ".modal .o_dwo_arc_filter", run: "text inner" },
        { trigger: ".modal .o_dwo_tree_row:not(.o_dwo_tree_folder):contains('inner.zip')", run: "click" },
        { content: "The zip in the zip opens in its own dialog", trigger: ".modal:last .o_dwo_arc_stats:contains('1 files')" },
        { trigger: ".modal:last .o_dwo_tree_row:contains('readme.txt')" },
        { trigger: ".modal:last .o_dwo_ap_close", run: "click" },
        { content: "Back to the first archive", trigger: ".modal .o_dwo_arc_stats:contains('20002 files')" },
        { trigger: ".modal .o_dwo_arc_filter", run: "text logo" },
        { trigger: ".modal .o_dwo_tree_row:not(.o_dwo_tree_folder):contains('logo.png')", run: "click" },
        { content: "A picture inside opens natively", trigger: ".modal:last .o_dwo_ap_content img" },
        { trigger: ".modal:last .o_dwo_ap_close", run: "click" },
        { trigger: ".modal .o_dwo_ap_close", run: "click" },
    ],
});

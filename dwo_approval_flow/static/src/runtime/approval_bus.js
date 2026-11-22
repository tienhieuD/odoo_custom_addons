/** @odoo-module **/
import { reactive } from "@odoo/owl";

/** Bumped after each press so the buttons and the panel of a form reload together. */
export const approvalBus = reactive({ rev: 0 });

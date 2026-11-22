import { proxy } from "@odoo/owl";

/** Bumped after each press so the buttons and the panel of a form reload together. */
export const approvalBus = proxy({ rev: 0 });

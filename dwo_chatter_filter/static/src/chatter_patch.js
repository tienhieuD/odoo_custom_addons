/* @odoo-module */

import { Chatter } from "@mail/core/web/chatter";
import { patch } from "@web/core/utils/patch";

import { DwoMessageFilter } from "./filter/dwo_message_filter";

patch(Chatter, {
    components: { ...Chatter.components, DwoMessageFilter },
});

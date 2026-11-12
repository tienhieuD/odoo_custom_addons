/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { formatFloatTime } from "@web/views/fields/formatters";
import { parseFloatTime } from "@web/views/fields/parsers";
import { useInputField } from "@web/views/fields/input_field_hook";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useNumpadDecimal } from "@web/views/fields/numpad_decimal_hook";

import { Component } from "@odoo/owl";

/**
 * `float_time` (HH:MM) with a short unit label after the value, e.g.
 * "04:30 h". Plain float_time reads as a duration already, but on a
 * generic SLA engine mixing hours-based durations with percentages and
 * plain counts on the same screen, a bare "4.50" or "04:30" leaves the
 * unit to be inferred from the field label alone -- this spells it out
 * next to the number itself.
 */
export class FloatTimeUnitField extends Component {
    static template = "dwo_sla_core.FloatTimeUnitField";
    static props = {
        ...standardFieldProps,
        unit: { type: String, optional: true },
    };
    static defaultProps = {
        unit: _t("h"),
    };

    setup() {
        this.inputFloatTimeRef = useInputField({
            getValue: () => this.formattedValue,
            refName: "numpadDecimal",
            parse: (v) => parseFloatTime(v),
        });
        useNumpadDecimal();
    }

    get formattedValue() {
        return formatFloatTime(this.props.record.data[this.props.name]);
    }
}

export const floatTimeUnitField = {
    component: FloatTimeUnitField,
    displayName: _t("Time with unit"),
    supportedOptions: [
        {
            label: _t("Unit label"),
            name: "unit",
            type: "string",
        },
    ],
    supportedTypes: ["float"],
    isEmpty: () => false,
    extractProps: ({ options }) => ({
        unit: options.unit,
    }),
};

registry.category("fields").add("float_time_unit", floatTimeUnitField);

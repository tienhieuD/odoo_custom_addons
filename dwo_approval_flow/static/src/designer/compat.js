/** @odoo-module **/
// Odoo 15: Owl 1.4 inside the legacy web client. No orm/dialog/notification services of Owl 2: thin helpers.
const { Component } = owl;
const { useExternalListener } = owl.hooks;

/** ``{call(model, method, args, kwargs)}`` on top of the legacy rpc service. */
export function makeOrm(env) {
    return {
        call: (model, method, args = [], kwargs = {}) => env.services.rpc({ model, method, args, kwargs }),
    };
}

/** A notification of the legacy service. */
export function notify(env, message, type = "info") {
    env.services.notification.notify({ message, type });
}

/** Open an action returned by the server. */
export function doAction(env, action) {
    env.bus.trigger("do-action", { action });
}

/** The modal of the designer: ``<DwoModal title size close>`` with a default slot and a ``footer`` slot. */
export class DwoModal extends Component {
    setup() {
        useExternalListener(window, "keydown", (ev) => {
            if (ev.key === "Escape") {
                this.props.close();
            }
        });
    }

    get dialogClass() {
        return this.props.size === "lg" ? "modal-dialog modal-lg" : "modal-dialog";
    }
}
DwoModal.template = "dwo_approval_flow.Modal";

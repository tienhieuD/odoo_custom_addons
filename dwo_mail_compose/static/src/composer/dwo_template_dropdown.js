odoo.define('dwo_mail_compose/static/src/composer/dwo_template_dropdown.js', function (require) {
'use strict';

const session = require('web.session');
const { orm } = require('dwo_mail_compose/static/src/composer/dwo_utils.js');

const { Component } = owl;
const { useExternalListener, useState } = owl.hooks;

const LIMIT = 80;

/**
 * Template menu of the email form. It follows the template menu of the core composer: the templates
 * of the user first, then the shared ones, "Save as Template" and "Manage Templates".
 * Odoo 15 has no dropdown component and no "Search More..." dialog: the menu is a Bootstrap menu and it
 * lists up to 80 templates.
 */
class DwoTemplateDropdown extends Component {
    setup() {
        super.setup();
        this.state = useState({ open: false, templates: [] });
        this.unmounted = false;
        useExternalListener(document, 'click', (ev) => {
            if (this.state.open && !(this.el && this.el.contains(ev.target))) {
                this.state.open = false;
            }
        });
    }

    async willStart() {
        await this.fetchTemplates();
    }

    willUnmount() {
        this.unmounted = true;
    }

    async fetchTemplates() {
        const fields = ['display_name'];
        const templates = await orm(this.env, 'mail.template', 'search_read', [], {
            domain: [['model', '=', this.props.model], ['user_id', '=', session.uid]],
            fields,
            limit: LIMIT,
        });
        if (templates.length < LIMIT) {
            templates.push(
                ...(await orm(this.env, 'mail.template', 'search_read', [], {
                    domain: [['model', '=', this.props.model], ['user_id', '=', false]],
                    fields,
                    limit: LIMIT - templates.length,
                }))
            );
        }
        this.state.templates = templates;
    }

    toggle() {
        this.state.open = !this.state.open;
    }

    onClickTemplate(ev) {
        const id = Number(ev.currentTarget.dataset.id);
        this.state.open = false;
        this.props.onPick(this.state.templates.find((t) => t.id === id));
    }

    onClickSave() {
        this.state.open = false;
        this.props.onSave();
    }

    manage(ev) {
        ev.preventDefault();
        this.state.open = false;
        this.env.bus.trigger('do-action', {
            action: 'mail.action_email_template_tree_all',
            options: {
                additional_context: {
                    search_default_my_templates: 1,
                    search_default_model: this.props.model,
                    default_model: this.props.model,
                    default_user_id: session.uid,
                },
            },
        });
    }
}

Object.assign(DwoTemplateDropdown, {
    template: 'dwo_mail_compose.TemplateDropdown',
});

return { DwoTemplateDropdown };

});

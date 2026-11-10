odoo.define('dwo_mail_compose/static/src/composer/dwo_address_input.js', function (require) {
'use strict';

const { orm } = require('dwo_mail_compose/static/src/composer/dwo_utils.js');

const { Component } = owl;
const { useRef, useState } = owl.hooks;

const EMAIL_RE = /^[^\s@<>,;]+@[^\s@<>,;]+\.[^\s@<>,;]+$/;

/**
 * Parse "Name <a@b.com>", "a@b.com" or a list separated by , ; or new lines.
 * @returns {{email: string, name: string}[]}
 */
function parseAddresses(text) {
    const result = [];
    for (const raw of (text || '').split(/[,;\n]+/)) {
        const part = raw.trim();
        if (!part) {
            continue;
        }
        const match = part.match(/^(.*?)\s*<([^>]+)>$/);
        const email = (match ? match[2] : part).trim().toLowerCase();
        const name = match ? match[1].replace(/^["']|["']$/g, '').trim() : '';
        result.push({ email, name, valid: EMAIL_RE.test(email) });
    }
    return result;
}

/**
 * Email field made of badges. Typing suggests users, partners and the
 * addresses already used; any valid address can be typed. An address is shown
 * once per field; the same address may be in To, Cc and Bcc.
 */
class DwoAddressInput extends Component {

    setup() {
        super.setup();
        this.inputRef = useRef('input');
        this.editRef = useRef('edit');
        // editing: the chip being edited ({ email, text, invalid }), null when none
        this.state = useState({ text: '', suggestions: [], active: -1, invalid: false, editing: null });
        this.timer = null;
        this.requestId = 0;
        this.editFocused = null;
        this.unmounted = false;
    }

    /** The edit box takes the focus as soon as it is shown. */
    patched() {
        const email = this.state.editing && this.state.editing.email;
        if (email && this.editFocused !== email && this.editRef.el) {
            this.editFocused = email;
            this.editRef.el.focus();
            this.editRef.el.select();
        } else if (!email) {
            this.editFocused = null;
        }
    }

    willUnmount() {
        this.unmounted = true;
        clearTimeout(this.timer);
    }

    // --- edit a chip in place ------------------------------------------------

    startEdit(address) {
        this.commitText({ silent: true });
        this.state.suggestions = [];
        this.state.editing = { email: address.email, text: address.email, invalid: false };
    }

    onEditInput(ev) {
        this.state.editing.text = ev.target.value;
        this.state.editing.invalid = false;
    }

    onEditKeydown(ev) {
        if (ev.key === 'Enter' || ev.key === 'Tab' || ev.key === ',') {
            ev.preventDefault();
            this.commitEdit();
        } else if (ev.key === 'Escape') {
            ev.preventDefault();
            ev.stopPropagation();
            this.state.editing = null;
        }
    }

    onEditBlur() {
        // a text that is not an address is dropped: the chip keeps its old address
        if (this.state.editing) {
            this.commitEdit({ silent: true });
        }
    }

    /**
     * Replace the address of the chip by what was typed, at the same place. An address already
     * in the field is not added twice (the chip is removed); an empty text removes the chip.
     */
    commitEdit({ silent = false } = {}) {
        const editing = this.state.editing;
        if (!editing) {
            return;
        }
        const text = editing.text.trim();
        const old = this.props.value.find((a) => a.email === editing.email);
        if (!text) {
            this.state.editing = null;
            if (old) {
                this.remove(old);
            }
            return;
        }
        const [parsed] = parseAddresses(text);
        if (!parsed || !parsed.valid) {
            if (silent) {
                this.state.editing = null;
            } else {
                editing.invalid = true;
            }
            return;
        }
        this.state.editing = null;
        if (!old || parsed.email === old.email) {
            return;
        }
        const exists = this.props.value.some((a) => a.email === parsed.email);
        const value = [];
        for (const address of this.props.value) {
            if (address === old) {
                if (!exists) {
                    value.push({ email: parsed.email, name: parsed.name, isNew: true });
                }
            } else {
                value.push(address);
            }
        }
        this.props.onChange(value);
    }

    /** Only the addresses of this field: the same address may also be in To, Cc and Bcc. */
    get used() {
        return new Set(this.props.value.map((a) => a.email));
    }

    onInput(ev) {
        this.state.text = ev.target.value;
        this.state.invalid = false;
        if (/[,;]\s*$/.test(this.state.text)) {
            this.commitText();
            return;
        }
        clearTimeout(this.timer);
        this.timer = setTimeout(() => this.fetchSuggestions(), 150);
    }

    async fetchSuggestions() {
        const requestId = ++this.requestId;
        const suggestions = await orm(this.env, 'dwo.mail.composer', 'suggest', [], {
            query: this.state.text.trim(),
            exclude: [...this.used],
        });
        if (!this.unmounted && requestId === this.requestId) {
            this.state.suggestions = suggestions;
            this.state.active = -1;
        }
    }

    onFocus() {
        this.fetchSuggestions();
    }

    /**
     * The input keeps the focus after a suggestion is picked, so a second click on it fires no
     * focus event: open the suggestions on click too.
     */
    onClick() {
        this.fetchSuggestions();
    }

    /** A click anywhere on the field (badges area, padding) puts the cursor in the input. */
    onBoxClick(ev) {
        if (ev.target === ev.currentTarget) {
            if (this.inputRef.el) {
                this.inputRef.el.focus();
            }
            this.fetchSuggestions();
        }
    }

    onBlur() {
        // let a click on a suggestion happen first
        setTimeout(() => {
            if (this.unmounted) {
                return;
            }
            this.commitText({ silent: true });
            this.state.suggestions = [];
        }, 120);
    }

    onKeydown(ev) {
        const { suggestions, active } = this.state;
        if (ev.key === 'ArrowDown' && suggestions.length) {
            ev.preventDefault();
            this.state.active = Math.min(active + 1, suggestions.length - 1);
        } else if (ev.key === 'ArrowUp' && suggestions.length) {
            ev.preventDefault();
            this.state.active = Math.max(active - 1, 0);
        } else if (ev.key === 'Enter' || (ev.key === 'Tab' && this.state.text.trim())) {
            if (active > -1 && suggestions[active]) {
                ev.preventDefault();
                this.pick(suggestions[active]);
            } else if (this.state.text.trim()) {
                ev.preventDefault();
                this.commitText();
            }
        } else if (ev.key === 'Escape') {
            this.state.suggestions = [];
        } else if (ev.key === 'Backspace' && !this.state.text && this.props.value.length) {
            this.props.onChange(this.props.value.slice(0, -1));
        }
    }

    onPaste(ev) {
        const text = (ev.clipboardData && ev.clipboardData.getData('text')) || '';
        if (/[,;\n]/.test(text)) {
            ev.preventDefault();
            this.state.text += text;
            this.commitText();
        }
    }

    /** Forget the suggestions asked for but not shown yet: they are about text that is gone. */
    cancelPendingSuggestions() {
        clearTimeout(this.timer);
        this.requestId++;
    }

    onMousedownSuggestion(ev) {
        // the click must not take the focus out of the input
        ev.preventDefault();
        this.pick(this.state.suggestions[Number(ev.currentTarget.dataset.index)]);
    }

    pick(suggestion) {
        this.cancelPendingSuggestions();
        this.add([{ email: suggestion.email, name: suggestion.name }]);
        this.state.text = '';
        this.state.suggestions = [];
        if (this.inputRef.el) {
            this.inputRef.el.focus();
        }
    }

    commitText({ silent = false } = {}) {
        const parsed = parseAddresses(this.state.text);
        if (!parsed.length) {
            return;
        }
        const valid = parsed.filter((a) => a.valid);
        const invalid = parsed.filter((a) => !a.valid);
        this.cancelPendingSuggestions();
        this.state.suggestions = [];
        this.add(valid.map(({ email, name }) => ({ email, name, isNew: true })));
        if (invalid.length) {
            // keep what could not be read so the user can fix it
            this.state.text = invalid.map((a) => a.email).join(', ');
            this.state.invalid = !silent;
        } else {
            this.state.text = '';
            this.state.invalid = false;
        }
    }

    add(items) {
        const used = this.used;
        const fresh = [];
        for (const item of items) {
            if (!used.has(item.email)) {
                used.add(item.email);
                fresh.push(item);
            }
        }
        if (fresh.length) {
            this.props.onChange([...this.props.value, ...fresh]);
        }
    }

    onClickRemove(ev) {
        ev.stopPropagation();
        this.remove({ email: ev.currentTarget.dataset.email });
    }

    onClickChip(ev) {
        ev.stopPropagation();
        const email = ev.currentTarget.dataset.email;
        this.startEdit(this.props.value.find((a) => a.email === email));
    }

    remove(address) {
        this.props.onChange(this.props.value.filter((a) => a.email !== address.email));
    }
}

Object.assign(DwoAddressInput, {
    template: 'dwo_mail_compose.AddressInput',
});

return { parseAddresses, DwoAddressInput };

});

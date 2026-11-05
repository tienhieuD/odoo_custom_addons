import hashlib
import json
import logging

from odoo import api, fields, models, tools

_logger = logging.getLogger(__name__)


class DwoModelConcurrency(models.Model):
    _name = 'dwo.model.concurrency'
    _description = 'Concurrency Model Configuration'
    _rec_name = 'model'

    model_id = fields.Many2one('ir.model', string='Model', index=True, ondelete='cascade')
    model = fields.Char('Technical Model Name', related='model_id.model', readonly=True, store=True, index=True)
    field_ids = fields.Many2many(
        'ir.model.fields', relation='dwo_model_concurrency_field_rel',
        column1='concurrency_model_id', column2='field_id', string='Fields')
    field_domain = fields.Char(compute='_compute_field_domain')
    active = fields.Boolean(string='Active', default=True, index=True)

    @api.depends('model_id')
    def _compute_field_domain(self):
        for rec in self:
            rec.field_domain = json.dumps([
                ('model', '=', rec.model_id.model),
                ('store', '=', True),
                ('readonly', '=', False),
            ])

    # ------------------------------------------------------------------
    # configuration cache: write() runs for every model, so the lookup of
    # the watched fields must not hit the database each time
    # ------------------------------------------------------------------
    @api.model
    @tools.ormcache('model_name')
    def _get_watched_field_names(self, model_name):
        configs = self.sudo().with_context(active_test=True).search([('model', '=', model_name)])
        return tuple(sorted(set(configs.field_ids.mapped('name'))))

    def _clear_watched_cache(self):
        self.env.registry.clear_caches()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self._clear_watched_cache()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._clear_watched_cache()
        return res

    def unlink(self):
        res = super().unlink()
        self._clear_watched_cache()
        return res

    # ------------------------------------------------------------------
    # soft conflict detection (never raises, never blocks a write)
    # ------------------------------------------------------------------
    @api.model
    def get_watched_fields(self, model_name):
        """Names of the fields watched on a model, for the web client."""
        return list(self._get_watched_field_names(model_name))

    @api.model
    def _normalize_value(self, record, field_name):
        """Return ``(comparable, display)`` of a field. ``comparable`` is JSON friendly and stable,
        ``display`` is a short text for humans."""
        field = record._fields[field_name]
        value = record[field_name]
        ftype = field.type
        if ftype == 'many2one':
            return (value.id or False), (value.display_name or '')
        if ftype in ('one2many', 'many2many'):
            ids = sorted(value.ids)
            return ids, ', '.join(value.mapped('display_name'))
        if ftype == 'binary':
            raw = value or b''
            if isinstance(raw, str):
                raw = raw.encode()
            digest = hashlib.sha1(raw).hexdigest() if raw else False
            return digest, ''
        if ftype == 'float':
            digits = field.get_digits(record.env) if hasattr(field, 'get_digits') else None
            value = round(value or 0.0, digits[1]) if digits else (value or 0.0)
            return value, str(value)
        if ftype == 'monetary':
            value = value or 0.0
            return round(value, 6), str(value)
        if ftype in ('date', 'datetime'):
            text = fields.Date.to_string(value) if ftype == 'date' else fields.Datetime.to_string(value)
            return (text or False), (text or '')
        if ftype == 'selection':
            label = dict(field._description_selection(record.env)).get(value, value)
            return (value or False), (label or '')
        if ftype == 'boolean':
            return bool(value), 'Yes' if value else 'No'
        return (value if value not in (None, '') else False), ('' if value in (None, False) else str(value))

    @api.model
    def dwo_snapshot(self, model_name, res_id):
        """Normalized values of the watched fields, taken when the form is loaded."""
        names = self._get_watched_field_names(model_name)
        if not names or not res_id or model_name not in self.env:
            return {}
        record = self.env[model_name].browse(res_id).exists()
        if not record:
            return {}
        values = {}
        for name in names:
            try:
                values[name] = self._normalize_value(record, name)[0]
            except Exception:  # noqa: BLE001 - a field the user cannot read is simply not compared
                continue
        return values

    @api.model
    def dwo_check_conflict(self, model_name, res_id, snapshot, dirty_fields):
        """Compare the fields the user is about to save with the values loaded at form open.

        Only the fields that are watched, edited by the user *and* changed on the server since the
        form was loaded are reported. Returns a list of dicts; an empty list means "no conflict".
        This method only reads: it never raises because of a conflict.
        """
        watched = set(self._get_watched_field_names(model_name))
        candidates = [name for name in (dirty_fields or []) if name in watched and name in (snapshot or {})]
        if not candidates or not res_id or model_name not in self.env:
            return []
        record = self.env[model_name].browse(res_id).exists()
        if not record:
            return []
        conflicts = []
        for name in candidates:
            try:
                current, display = self._normalize_value(record, name)
            except Exception:  # noqa: BLE001
                continue
            if current != snapshot[name]:
                conflicts.append({
                    'name': name,
                    'label': record._fields[name]._description_string(self.env),
                    'type': record._fields[name].type,
                    'server': display,
                })
        if conflicts:
            writer = record.sudo().write_uid
            for conflict in conflicts:
                conflict['write_uid_name'] = writer.name or ''
        return conflicts

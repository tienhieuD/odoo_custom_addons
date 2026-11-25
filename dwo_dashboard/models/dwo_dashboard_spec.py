# -*- coding: utf-8 -*-
import json

from odoo import _, api, models
from odoo.exceptions import AccessError

from ..spec import (Registry, core_dataset_types, core_visual_types, validate_dataset_semantics,
                    validate_dataset_structure, validate_semantics, validate_structure)
from ..spec.schema_gen import build_dataset_schema, build_schema


def _parse(value):
    """(parsed value, error list): accepts a dict or a JSON text; never raises."""
    if isinstance(value, (str, bytes)):
        try:
            return json.loads(value), []
        except ValueError as exc:
            return None, [{"path": "", "code": "json", "message": "not valid JSON: %s" % exc}]
    return value, []


class DwoDashboardSpec(models.AbstractModel):
    """Entry points of the dashboard specification: validators, schemas, and the hooks plugins extend.

    A plugin (a visual type such as ``scatter``, a dataset type such as ``csv``) is an addon that does
    ``_inherit = "dwo.dashboard.spec"`` and extends ``_dwo_visual_types`` / ``_dwo_dataset_types`` with ``super()``,
    so it only exists in the databases where it is installed. Strict on save, tolerant on render: a page whose
    widget type is no longer installed fails ``validate`` (cannot be saved), but a stored page must still open, with
    a placeholder in that widget."""
    _name = "dwo.dashboard.spec"
    _description = "Dashboard specification"

    # ---------------------------------------------------------------------------------------------- plugin hooks
    @api.model
    def _dwo_visual_types(self):
        """{name: visual type definition} (see spec/registry.py)."""
        return core_visual_types()

    @api.model
    def _dwo_dataset_types(self):
        """{name: dataset type definition} (see spec/registry.py)."""
        return core_dataset_types()

    @api.model
    def _dwo_resolve_dataset(self, ref):
        """The definition (dwo-dataset/1) of a dataset reference, or None. Stored definitions arrive in a later
        phase; tests and plugins can override it."""
        return None

    @api.model
    def _dwo_dataset_checkers(self):
        """{dataset type: callable(ref, widget_path, widget, definition) -> [errors]}: the semantic check of the dataset
        types a plugin adds. A plugin type without a checker is refused by ``validate``."""
        return {}

    @api.model
    def _dwo_registry(self):
        return Registry(self._dwo_visual_types(), self._dwo_dataset_types())

    # ------------------------------------------------------------------------------------------------ public API
    # Public methods are callable over RPC by any logged-in user: they never take ``check_access``. The author's own
    # access is always checked (the private variants below let tests and the server skip it).
    @api.model
    def validate(self, spec):
        """Validate a page (dict or JSON text). Returns {"valid": bool, "errors": [{path, code, message}]}; paths are
        JSON Pointers. Never raises because of the content of the spec."""
        return self._validate(spec, True)

    @api.model
    def validate_dataset(self, defn):
        """Validate a dataset definition (dict or JSON text). System administrators only: they write datasets."""
        if not self.env.is_system():
            raise AccessError(_("Only system administrators can validate dataset definitions."))
        return self._validate_dataset(defn, True)

    @api.model
    def _validate(self, spec, check_access):
        spec, errors = _parse(spec)
        if not errors:
            registry = self._dwo_registry()
            errors = validate_structure(spec, registry)
            if not errors:
                errors = validate_semantics(self.env, spec, registry, self._dwo_resolve_dataset, check_access,
                                            self._dwo_dataset_checkers())
        return {"valid": not errors, "errors": errors}

    @api.model
    def _validate_dataset(self, defn, check_access):
        defn, errors = _parse(defn)
        if not errors:
            registry = self._dwo_registry()
            errors = validate_dataset_structure(defn, registry)
            if not errors:
                errors = validate_dataset_semantics(self.env, defn, registry, check_access)
        return {"valid": not errors, "errors": errors}

    @api.model
    def get_schema(self):
        """JSON Schema of a page, including the plugins installed in this database."""
        return build_schema(self._dwo_registry())

    @api.model
    def get_dataset_schema(self):
        return build_dataset_schema(self._dwo_registry())

    @api.model
    def get_registry(self):
        """The installed visual and dataset types (for the UI and for AI tools)."""
        registry = self._dwo_registry()
        return {"visuals": registry.visuals, "datasets": registry.datasets}

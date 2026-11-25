# -*- coding: utf-8 -*-
"""The dashboard specification: registry of visual and dataset types, structural and semantic validation, schemas."""
from .constants import DATASET_SCHEMA_ID, SCHEMA_ID  # noqa: F401
from .dataset import validate_dataset_structure  # noqa: F401
from .registry import Registry, core_dataset_types, core_visual_types  # noqa: F401
from .structure import validate_structure  # noqa: F401
try:
    from .semantic import validate_dataset_semantics, validate_semantics  # noqa: F401
except ModuleNotFoundError as exc:  # no Odoo here (schema tools): the pure parts above stay usable
    if not (exc.name or "").startswith("odoo"):
        raise

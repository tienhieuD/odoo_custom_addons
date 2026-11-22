# -*- coding: utf-8 -*-
"""Protect the own-states field (``x_dwo_approval_state_id``) against direct writes.

The patch is put on the final class of the registry (outside every ``_inherit``) for the models
that have a flow with own states. It is idempotent and rebuilt when the registry loads.
The bypass flag lives in the server process (a thread local), never in the context, so a client
cannot forge it.
"""
import functools
import logging
import threading

_logger = logging.getLogger(__name__)
_local = threading.local()


class bypass:
    """``with bypass():`` the guards let calls through (used while an arrow runs its main step)."""

    def __enter__(self):
        _local.depth = getattr(_local, "depth", 0) + 1

    def __exit__(self, *exc):
        _local.depth -= 1


def is_bypassed():
    return getattr(_local, "depth", 0) > 0


def make_wrapper(name, original):
    @functools.wraps(original)
    def wrapper(self, vals, *args, **kwargs):
        if not is_bypassed() and not self.env.su and "x_dwo_approval_state_id" in vals:
            self.env["dwo.approval.flow"]._guard_write_refused()
        return original(self, vals, *args, **kwargs)
    wrapper._dwo_guard = True
    wrapper._dwo_orig = original
    return wrapper


def patch(cls, name):
    current = getattr(cls, name, None)
    if not callable(current) or getattr(current, "_dwo_guard", False):
        return False
    wrapper = make_wrapper(name, current)
    wrapper._dwo_own = name in vars(cls)
    setattr(cls, name, wrapper)
    return True


def unpatch(cls, name):
    current = vars(cls).get(name)
    if not getattr(current, "_dwo_guard", False):
        return
    if current._dwo_own:
        setattr(cls, name, current._dwo_orig)
    else:
        delattr(cls, name)


def sync(registry, wanted):
    """Make the patched pairs equal to ``wanted`` (a set of ``(model, method)``)."""
    for model_name in list(registry):
        cls = registry[model_name]
        for attr, value in list(vars(cls).items()):
            if getattr(value, "_dwo_guard", False) and (model_name, attr) not in wanted:
                unpatch(cls, attr)
    for model_name, name in wanted:
        if model_name in registry:
            patch(registry[model_name], name)

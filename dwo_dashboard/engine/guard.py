# -*- coding: utf-8 -*-
"""Run a query so that a slow or failing widget cannot take the request (or its neighbours) down."""
import contextlib

DEFAULT_TIMEOUT = 60
DEFAULT_MAX_ROWS = 5000


def _param(env, key, default, low, high):
    try:
        value = int(env["ir.config_parameter"].sudo().get_param(key, default))
    except (TypeError, ValueError):
        value = default
    return max(low, min(high, value))


def timeout_seconds(env):
    return _param(env, "dwo_dashboard.query_timeout", DEFAULT_TIMEOUT, 1, 600)


def max_rows(env):
    return _param(env, "dwo_dashboard.max_rows", DEFAULT_MAX_ROWS, 100, 50000)


@contextlib.contextmanager
def guarded(env, seconds=None):
    """Savepoint + ``statement_timeout``. A query cancelled by PostgreSQL aborts the transaction; the savepoint is rolled
    back (and with it the timeout setting), the transaction stays usable and the caller sees ``QueryCanceled``."""
    cr = env.cr
    cr.execute("SHOW statement_timeout")
    previous = cr.fetchone()[0]
    with cr.savepoint():
        cr.execute("SET LOCAL statement_timeout = %s", ["%ds" % (seconds or timeout_seconds(env))])
        yield
        cr.execute("SET LOCAL statement_timeout = %s", [previous])

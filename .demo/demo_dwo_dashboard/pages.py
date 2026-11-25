# -*- coding: utf-8 -*-
"""The dashboard pages given to the demo users (spec dwo-dashboard/1)."""

OPEN = ["state", "in", ["sale", "done"]]


def _kpi(wid, title, x, wells, **extra):
    return dict({"id": wid, "type": "kpi", "title": title, "x": x, "y": 0, "w": 3, "h": 3, "dataset": "orm:sale.order",
                 "where": [OPEN], "wells": {"value": wells}}, **extra)


def sales_page():
    compare = {"field": "date_order", "period": "this_month", "against": "previous_period"}
    trend = {"field": "date_order", "interval": "month", "points": 12}
    return {
        "schema": "dwo-dashboard/1", "title": "Sales", "grid": {"cols": 12},
        "filters": [
            {"id": "period", "type": "date", "label": "Order date", "default": "last_90_days",
             "bind": [{"dataset": "orm:sale.order", "field": "date_order"},
                      {"dataset": "orm:sale.order.line", "field": "create_date"}]},
            {"id": "seller", "type": "relation", "model": "res.users", "label": "Salesperson",
             "bind": [{"dataset": "orm:sale.order", "field": "user_id"},
                      {"dataset": "orm:sale.order.line", "field": "salesman_id"}]},
        ],
        "widgets": [
            _kpi("revenue", "Revenue", 0, {"field": "amount_total", "agg": "sum"}, compare=compare, trend=trend,
                 options={"format": "currency", "decimals": 0}),
            _kpi("orders", "Orders", 3, {"agg": "count"}, compare=compare, trend=trend),
            _kpi("average", "Average order", 6, {"field": "amount_total", "agg": "avg"}, compare=compare, trend=trend,
                 options={"format": "currency", "decimals": 0}),
            {"id": "quotes", "type": "kpi", "title": "Open quotations", "x": 9, "y": 0, "w": 3, "h": 3,
             "dataset": "orm:sale.order", "where": [["state", "in", ["draft", "sent"]]],
             "wells": {"value": {"agg": "count"}}, "ignore_filters": ["period"],
             "trend": {"field": "date_order", "interval": "month", "points": 12}},
            {"id": "monthly", "type": "bar", "title": "Revenue per month and salesperson", "x": 0, "y": 3, "w": 8, "h": 4,
             "dataset": "orm:sale.order", "where": [OPEN],
             "wells": {"axis": {"field": "date_order", "interval": "month"}, "legend": {"field": "user_id"},
                       "values": [{"field": "amount_total", "agg": "sum", "label": "Revenue"}]},
             "order": [{"field": "date_order", "dir": "asc"}], "limit": 12, "series_limit": 5,
             "options": {"stacked": True, "legend": "bottom"}},
            {"id": "categories", "type": "doughnut", "title": "Revenue by category", "x": 8, "y": 3, "w": 4, "h": 4,
             "dataset": "orm:sale.order.line", "where": [["state", "in", ["sale", "done"]]],
             "wells": {"category": {"field": "product_id.categ_id"},
                       "value": {"field": "price_subtotal", "agg": "sum", "label": "Revenue"}},
             "order": [{"measure": "price_subtotal:sum", "dir": "desc"}], "limit": 5,
             "options": {"other": True, "show_percent": True}},
            {"id": "yearly", "type": "line", "title": "Revenue this year against last year", "x": 0, "y": 7, "w": 6,
             "h": 4, "dataset": "orm:sale.order", "where": [OPEN],
             "wells": {"axis": {"field": "date_order", "interval": "month"},
                       "values": [{"field": "amount_total", "agg": "sum", "label": "Revenue"}]},
             "compare": {"field": "date_order", "period": "this_year", "against": "previous_year"},
             "options": {"smooth": True, "y_min": 0}, "ignore_filters": ["period"]},
            {"id": "matrix", "type": "pivot", "title": "Salesperson by quarter", "x": 6, "y": 7, "w": 6, "h": 4,
             "dataset": "orm:sale.order", "where": [OPEN],
             "wells": {"rows": [{"field": "user_id"}], "columns": [{"field": "date_order", "interval": "quarter"}],
                       "values": [{"field": "amount_total", "agg": "sum", "label": "Revenue"}]},
             "options": {"show_totals": True, "heatmap": True}, "ignore_filters": ["period"]},
            {"id": "top", "type": "table", "title": "Biggest orders", "x": 0, "y": 11, "w": 12, "h": 5,
             "dataset": "orm:sale.order", "where": [OPEN],
             "wells": {"columns": [{"field": "name"}, {"field": "partner_id"}, {"field": "user_id"},
                                   {"field": "date_order"}, {"field": "amount_total"}]},
             "order": [{"field": "amount_total", "dir": "desc"}], "limit": 15},
        ],
    }


def contacts_page():
    return {
        "schema": "dwo-dashboard/1", "title": "Contacts", "grid": {"cols": 12},
        "filters": [{"id": "created", "type": "date", "label": "Created", "default": "all",
                     "bind": [{"dataset": "orm:res.partner", "field": "create_date"}]}],
        "widgets": [
            {"id": "contacts", "type": "kpi", "title": "Contacts", "x": 0, "y": 0, "w": 3, "h": 2,
             "dataset": "orm:res.partner", "wells": {"value": {"agg": "count"}}},
            {"id": "companies", "type": "kpi", "title": "Companies", "x": 3, "y": 0, "w": 3, "h": 2,
             "dataset": "orm:res.partner", "where": [["is_company", "=", True]], "wells": {"value": {"agg": "count"}}},
            {"id": "by_country", "type": "bar", "title": "Top countries", "x": 6, "y": 0, "w": 6, "h": 4,
             "dataset": "orm:res.partner", "wells": {"axis": {"field": "country_id"}, "values": [{"agg": "count", "label": "Contacts"}]},
             "order": [{"measure": "__count", "dir": "desc"}], "limit": 8, "options": {"horizontal": True, "legend": "none"}},
            {"id": "latest", "type": "table", "title": "Latest contacts", "x": 0, "y": 4, "w": 12, "h": 5,
             "dataset": "orm:res.partner", "where": [["active", "=", True]],
             "wells": {"columns": [{"field": "name"}, {"field": "email"}, {"field": "country_id"}, {"field": "create_date"}]},
             "order": [{"field": "create_date", "dir": "desc"}], "limit": 15},
        ],
    }

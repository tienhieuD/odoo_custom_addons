# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models

PERIODS = (7, 30, 90)
OPEN_STAGES = ('in_progress', 'paused')
ENDED_STAGES = ('achieved', 'breached')
MAX_WEEKS = 12
MAX_DEFINITIONS = 10
ATTENTION_LIMIT = 10


class SlaTask(models.Model):
    _inherit = 'sla.task'

    @api.model
    def get_dashboard_data(self, period=30, filters=None):
        """Dữ liệu cho màn hình SLA Overview, MỘT lần gọi.

        Logic: chỉ đọc, không sudo (record rule theo công ty và quyền nhóm SLA
        áp dụng như danh sách thường); mọi số liệu lấy bằng `_read_group` /
        `search_count`, không lặp từng record (trừ 10 dòng "cần chú ý").
        Thẻ "stock" (đang chạy, sắp đến hạn, đang vi phạm) là tình trạng hiện
        tại; thẻ "flow" (% đạt, đã trễ) tính trên task KẾT THÚC trong kỳ
        (`end_time`). Kỳ trước: stock = ảnh chụp xấp xỉ tại đầu kỳ từ
        start/end/planned_end (không có lịch sử trạng thái), flow = kỳ liền kề.
        Mỗi thẻ trả kèm `domain` để mở danh sách `sla.task`.
        Refs: task 006 C3
        """
        period = period if period in PERIODS else 30
        filters = self._dashboard_clean_filters(filters)
        now = fields.Datetime.now()
        since = now - timedelta(days=period)
        prev_since = since - timedelta(days=period)
        base = self._dashboard_base_domain(filters)
        is_manager = self.env.user.has_group('dwo_sla_core.group_sla_manager')

        def open_at(moment):
            return [('start_time', '<=', moment), '|', ('end_time', '=', False),
                    ('end_time', '>', moment)]

        def ended_between(start, end):
            return [('stage', 'in', ENDED_STAGES), ('end_time', '>=', start),
                    ('end_time', '<=', end)]

        def count(domain):
            return self.search_count(domain)

        def rate(domain):
            row = self._read_group(domain, [], ['achieved_rate:avg', '__count'])
            value, total = row[0] if row else (None, 0)
            return None if not total or value is None else round(value * 100, 1)

        cur_ended = base + ended_between(since, now)
        prev_ended = base + ended_between(prev_since, since - timedelta(seconds=1))
        kpis = {
            'running': {
                'domain': base + [('stage', '=', 'in_progress')],
                'previous': count(base + open_at(since)),
            },
            'due_soon': {
                'domain': base + [('is_due_soon', '=', True)],
                'previous': count(base + open_at(since) + self._dashboard_due_soon_at(since)),
            },
            'breached': {
                'domain': base + [('outcome', '=', 'breached_open')],
                'previous': count(base + open_at(since) + [('planned_end_time', '<', since)]),
            },
            'achieved_rate': {
                'domain': cur_ended,
                'value': rate(cur_ended),
                'previous': rate(prev_ended),
            },
            'late': {
                'domain': base + [('outcome', '=', 'late'), ('end_time', '>=', since),
                                  ('end_time', '<=', now)],
                'previous': count(base + [('outcome', '=', 'late'), ('end_time', '>=', prev_since),
                                          ('end_time', '<', since)]),
            },
        }
        for key in ('running', 'due_soon', 'breached', 'late'):
            kpis[key]['value'] = count(kpis[key]['domain'])
        for kpi in kpis.values():
            value, previous = kpi['value'], kpi['previous']
            kpi['delta'] = None if value is None or previous is None else round(value - previous, 1)

        # Phạm vi biểu đồ: đang mở + đã kết thúc trong kỳ.
        scope = base + ['|', ('end_time', '=', False), ('end_time', '>=', since)]
        outcomes = dict(self._read_group(scope, ['outcome'], ['__count']))
        outcome_order = [key for key, _label in self._fields['outcome']._description_selection(self.env)]
        donut = [{'key': key, 'count': outcomes[key]} for key in outcome_order if outcomes.get(key)]

        per_definition = {}
        for definition, outcome, total in self._read_group(
                scope + [('outcome', 'in', ('on_time', 'late', 'breached_open'))],
                ['sla_id', 'outcome'], ['__count']):
            row = per_definition.setdefault(
                definition.id, {'id': definition.id, 'name': definition.name,
                                'on_time': 0, 'late': 0, 'breached_open': 0, 'total': 0})
            row[outcome] = total
            row['total'] += total
        bars = sorted(per_definition.values(), key=lambda r: (-r['total'], r['name']))[:MAX_DEFINITIONS]

        weekly = self._dashboard_weekly(base, since)

        attention_domain = base + [('stage', 'in', OPEN_STAGES), '|',
                                   ('has_breached', '=', True), ('is_due_soon', '=', True)]
        attention = self._dashboard_attention(attention_domain, is_manager)

        definitions = self.env['sla.definition'].search_fetch(
            [], ['name', 'type', 'target'], order='name, id')
        action = self.env['ir.actions.actions']._for_xml_id('dwo_sla_core.action_sla_task')
        return {
            'period': period,
            'filters': filters,
            'is_manager': is_manager,
            'has_data': bool(self.search_count([], limit=1)),
            'kpis': kpis,
            'donut': donut,
            'outcome_labels': dict(self._fields['outcome']._description_selection(self.env)),
            'scope_domain': scope,
            'bars': bars,
            'weekly': weekly,
            'attention': attention,
            'attention_domain': attention_domain,
            'definitions': [{'id': d.id, 'name': d.name, 'type': d.type, 'target': d.target}
                            for d in definitions],
            'action': {'id': action['id'], 'res_model': action['res_model'],
                       'view_mode': action['view_mode']},
        }

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    @api.model
    def _dashboard_clean_filters(self, filters):
        """Chỉ giữ giá trị hợp lệ của bộ lọc nhanh (client không đáng tin)."""
        filters = filters if isinstance(filters, dict) else {}
        types = {key for key, _label in self._fields['sla_type']._description_selection(self.env)}
        targets = {key for key, _label in self._fields['sla_target']._description_selection(self.env)}
        ids = filters.get('sla_ids') or []
        return {
            'sla_type': filters.get('sla_type') if filters.get('sla_type') in types else False,
            'sla_target': filters.get('sla_target') if filters.get('sla_target') in targets else False,
            'sla_ids': [i for i in ids if isinstance(i, int)] if isinstance(ids, (list, tuple)) else [],
        }

    @api.model
    def _dashboard_base_domain(self, filters):
        domain = []
        if filters['sla_type']:
            domain.append(('sla_type', '=', filters['sla_type']))
        if filters['sla_target']:
            domain.append(('sla_target', '=', filters['sla_target']))
        if filters['sla_ids']:
            domain.append(('sla_id', 'in', filters['sla_ids']))
        return domain

    @api.model
    def _dashboard_due_soon_at(self, moment):
        """Domain "sắp đến hạn" tại thời điểm `moment` (cho kỳ trước), cùng ngưỡng giờ
        như `is_due_soon`: theo định nghĩa, trống thì theo Settings."""
        default_hours = self._due_soon_hours_global()
        groups = self.env['sla.definition'].sudo().with_context(active_test=False)._read_group(
            [], ['due_soon_hours'], ['id:array_agg'])
        by_hours = {}
        for hours, ids in groups:
            by_hours.setdefault(hours or default_hours, []).extend(ids)
        domain = [('planned_end_time', '>', moment)]
        branches = [[('sla_id', 'in', ids), ('planned_end_time', '<=', moment + timedelta(hours=hours))]
                    for hours, ids in by_hours.items()]
        if not branches:
            return [(0, '=', 1)]
        or_part = []
        for index, branch in enumerate(branches):
            if index < len(branches) - 1:
                or_part.append('|')
            or_part.extend(['&', branch[0], branch[1]])
        return domain + or_part

    @api.model
    def _dashboard_weekly(self, base, since):
        """% đạt theo tuần (tối đa MAX_WEEKS tuần gần nhất) của task kết thúc trong kỳ."""
        domain = base + [('stage', 'in', ENDED_STAGES), ('end_time', '>=', since)]
        try:
            with self.env.cr.savepoint():
                rows = self._read_group(domain, ['end_time:week'], ['achieved_rate:avg', '__count'],
                                        order='end_time:week')
        except Exception:  # noqa: BLE001 -- múi giờ người dùng PostgreSQL không nhận ra (vd. Asia/Saigon)
            rows = self.with_context(tz='UTC')._read_group(
                domain, ['end_time:week'], ['achieved_rate:avg', '__count'], order='end_time:week')
        if not rows:
            return []
        points = {}
        for week, avg, total in rows:
            points[fields.Date.to_date(week)] = (None if avg is None else round(avg * 100, 1), total)
        week = min(points)
        last = max(points)
        series = []
        while week <= last:
            value, total = points.get(week, (None, 0))
            series.append({'week': fields.Date.to_string(week), 'rate': value, 'count': total})
            week += timedelta(days=7)
        return series[-MAX_WEEKS:]

    @api.model
    def _dashboard_attention(self, domain, is_manager):
        """10 task vi phạm/sắp đến hạn đầu bảng. `source_name` chỉ cho SLA Manager."""
        tasks = self.search(domain, order='has_breached desc, planned_end_time asc, id', limit=ATTENTION_LIMIT)
        if not tasks:
            return []
        models_ = {m['model']: m['name'] for m in self.env['ir.model'].sudo().search_read(
            [('model', 'in', tasks.mapped('res_model'))], ['model', 'name'])}
        rows = []
        for task in tasks:
            row = {
                'id': task.id,
                'definition': task.sla_id.name,
                'model': models_.get(task.res_model, task.res_model),
                'breached': task.has_breached,
                'stage': task.stage,
                'percent': task.business_percent_used,
                'planned_end_time': fields.Datetime.to_string(task.planned_end_time) or False,
            }
            if is_manager:
                row['source_name'] = task.source_name or False
            rows.append(row)
        return rows

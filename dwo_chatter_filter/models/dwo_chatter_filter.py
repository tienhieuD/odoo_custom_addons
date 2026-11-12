# -*- coding: utf-8 -*-
import colorsys
import logging
import random
import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
# Odoo 13 and older: safe_eval has no wrapped modules, the evaluation context takes the modules themselves
import datetime as safe_datetime
import time as safe_time

import dateutil as safe_dateutil
import dateutil.relativedelta  # noqa: F401
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
# a colour must read on a white page, as the text of an outlined chip and as the background of a chip
# with white text: a relative luminance of 0.18 or less gives a contrast of 4.5:1 or more with white
MAX_LUMINANCE = 0.18


def _luminance(red, green, blue):
    """Relative luminance (WCAG) of a colour given as three numbers from 0 to 1."""
    def linear(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * linear(red) + 0.7152 * linear(green) + 0.0722 * linear(blue)


def _hue_of(color):
    red, green, blue = (int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return colorsys.rgb_to_hsv(red, green, blue)[0]


def pick_color(used_colors, rng=random):
    """A new colour whose hue is far from the ones already used: the middle of the largest gap between
    them (with a little randomness), dark enough to read on a white page."""
    hues = sorted(_hue_of(c) for c in used_colors if c and HEX_COLOR.match(c))
    if not hues:
        hue = rng.random()
    else:
        # the gaps on the colour circle, the last one wraps around
        gaps = [(hues[(i + 1) % len(hues)] - hues[i]) % 1 or 1 for i in range(len(hues))]
        index = max(range(len(gaps)), key=gaps.__getitem__)
        jitter = (rng.random() - 0.5) * 0.3 * gaps[index]
        hue = (hues[index] + gaps[index] / 2 + jitter) % 1
    value = 0.95
    while value > 0.2:
        red, green, blue = colorsys.hsv_to_rgb(hue, 0.65, value)
        if _luminance(red, green, blue) <= MAX_LUMINANCE:
            break
        value -= 0.02
    return "#%02x%02x%02x" % (round(red * 255), round(green * 255), round(blue * 255))


class DwoChatterFilter(models.Model):
    _name = "dwo.chatter.filter"
    _description = "Chatter Quick Filter chip"
    _order = "sequence, id"

    name = fields.Char(
        string="Name", required=True, translate=True,
        help="The text of the chip above the messages of the chatter.\nExample: Quotes")
    sequence = fields.Integer(
        string="Sequence", default=lambda self: self._default_sequence(),
        help="The order of the chips: drag the lines of the list to change it.\nExample: 10")
    color = fields.Char(
        string="Color", required=True, default=lambda self: self._default_color(),
        help="The colour of the chip, as #rrggbb. A new chip gets a colour that is not used yet.\nExample: #714b67")
    domain = fields.Char(
        string="Messages shown", required=True, default="[]",
        help="The messages the chip shows, as a filter on the messages of the record. "
             "An empty filter shows all of them.\nExample: [('message_type', '=', 'email')]")
    active = fields.Boolean(
        default=True,
        help="Archive a chip to hide it without losing it.\nExample: archived")
    message_model = fields.Char(
        compute="_compute_message_model",
        help="The model the domain is about (for the domain editor).\nExample: mail.message")

    def _compute_message_model(self):
        for chip in self:
            chip.message_model = "mail.message"

    @api.model
    def _default_sequence(self):
        last = self.with_context(active_test=False).search([], order="sequence desc", limit=1)
        return (last.sequence + 10) if last else 10

    @api.model
    def _default_color(self):
        used = self.with_context(active_test=False).search([]).mapped("color")
        return pick_color(used)

    @api.constrains("color")
    def _check_color(self):
        for chip in self:
            if not HEX_COLOR.match(chip.color or ""):
                raise ValidationError(_("The color of %(name)s must look like #714b67.") % {"name": chip.name})

    def _dwo_eval_context(self):
        return {
            "uid": self.env.uid,
            "user": self.env.user,
            "time": safe_time,
            "datetime": safe_datetime,
            "relativedelta": safe_dateutil.relativedelta.relativedelta,
            "context_today": lambda: fields.Date.context_today(self),
        }

    def _dwo_domain(self):
        """The domain of the chip, on the messages."""
        self.ensure_one()
        return expression.normalize_domain(safe_eval(self.domain or "[]", self._dwo_eval_context()))

    @api.constrains("domain")
    def _check_domain(self):
        Message = self.env["mail.message"].sudo()
        for chip in self:
            try:
                with self.env.cr.savepoint():
                    Message.search(chip._dwo_domain(), limit=1)
            except Exception as error:  # a bad filter can fail in many ways: say which chip and why
                raise ValidationError(_(
                    "The filter of %(name)s is not valid: %(error)s") % {"name": chip.name, "error": error}) from error

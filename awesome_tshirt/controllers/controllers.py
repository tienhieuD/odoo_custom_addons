# -*- coding: utf-8 -*-
from odoo import http

class BlogController(http.Controller):
    @http.route('/article/', auth='public')
    def index(self, **kw):
        return "Hello, world"

# class AwesomeTshirt(http.Controller):
#     @http.route('/awesome_tshirt/awesome_tshirt', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/awesome_tshirt/awesome_tshirt/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('awesome_tshirt.listing', {
#             'root': '/awesome_tshirt/awesome_tshirt',
#             'objects': http.request.env['awesome_tshirt.awesome_tshirt'].search([]),
#         })

#     @http.route('/awesome_tshirt/awesome_tshirt/objects/<model("awesome_tshirt.awesome_tshirt"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('awesome_tshirt.object', {
#             'object': obj
#         })

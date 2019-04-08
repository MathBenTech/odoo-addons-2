# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LightingProductApplication(models.Model):
    _name = 'lighting.product.application'
    _order = 'name'

    name = fields.Char(string='Application', required=True, translate=True)

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['lighting.product'].search_count([('application_ids', '=', record.id)])

    attachment_ids = fields.One2many(comodel_name='lighting.product.application.attachment',
                                     inverse_name='application_id', string='Attachments', copy=True,
                                     track_visibility='onchange')
    attachment_count = fields.Integer(compute='_compute_attachment_count', string='Attachment(s)')

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = self.env['lighting.product.application.attachment'] \
                .search_count([('application_id', '=', record.id)])

    _sql_constraints = [('name_uniq', 'unique (name)', 'The application must be unique!'),
                        ]

    @api.multi
    def unlink(self):
        records = self.env['lighting.product'].search([('application_ids', 'in', self.ids)])
        if records:
            raise UserError(_("You are trying to delete a record that is still referenced!"))
        return super(LightingProductApplication, self).unlink()

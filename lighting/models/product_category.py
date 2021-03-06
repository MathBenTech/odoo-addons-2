# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _


class LightingProductCategory(models.Model):
    _name = 'lighting.product.category'
    _inherit = 'lighting.tree.mixin'
    _parent_name = 'parent_id'
    _rec_name = 'complete_name'
    _order = 'sequence,name'

    @api.model
    def _get_domain(self):
        model_id = self.env.ref('lighting.model_lighting_product').id
        return [('model_id', '=', model_id)]

    code = fields.Char(string='Code', size=5, required=True)

    name = fields.Char(required=True, translate=True)

    description_text = fields.Char(string='Description text', help='Text to show on a generated product description',
                                   translate=True)

    parent_id = fields.Many2one(comodel_name='lighting.product.category', string='Parent',
                                index=True, ondelete='cascade', track_visibility='onchange')
    child_ids = fields.One2many(comodel_name='lighting.product.category', inverse_name='parent_id',
                                string='Child Categories', track_visibility='onchange')

    root_id = fields.Many2one(comodel_name='lighting.product.category',
                              readonly=True, string='Root',
                              compute='_compute_root')

    def _compute_root(self):
        for rec in self:
            rec.root_id = rec._get_root()

    is_accessory = fields.Boolean(string="Is accessory")

    sequence = fields.Integer(required=True, default=1, help="The sequence field is used to define order")

    #### attributes
    attribute_ids = fields.Many2many(comodel_name='ir.model.fields',
                                     relation='lighting_product_category_field_attribute_rel',
                                     column1='category_id', column2='field_id',
                                     domain=_get_domain,
                                     string='Attributes')

    inherit_attributes = fields.Boolean(string='Inherit attributes')
    effective_attribute_ids = fields.Many2many(comodel_name='ir.model.fields',
                                               string='Effective attributes', readonly=True,
                                               compute='_compute_effective_attributes')

    def _get_parents_attributes(self):
        self.ensure_one()
        if not self.inherit_attributes:
            return self.attribute_ids
        else:
            if not self.parent_id:
                return self.attribute_ids
            else:
                return self.attribute_ids | self.parent_id._get_parents_attributes()

    def _compute_effective_attributes(self):
        for rec in self:
            rec.effective_attribute_ids = rec._get_parents_attributes()

    @api.onchange('inherit_attributes', 'attribute_ids')
    def onchange_attribute_ids(self):
        if self.inherit_attributes:
            self._compute_effective_attributes()

    #### fields
    field_ids = fields.Many2many(comodel_name='ir.model.fields',
                                 relation='lighting_product_category_field_field_rel',
                                 column1='category_id', column2='field_id',
                                 domain=_get_domain,
                                 string='Fields')

    inherit_fields = fields.Boolean(string='Inherit fields')
    effective_field_ids = fields.Many2many(comodel_name='ir.model.fields',
                                           string='Effective fields', readonly=True,
                                           compute='_compute_effective_fields')

    def _get_parents_fields(self):
        self.ensure_one()
        if not self.inherit_fields:
            return self.field_ids
        else:
            if not self.parent_id:
                return self.field_ids
            else:
                return self.field_ids | self.parent_id._get_parents_fields()

    def _compute_effective_fields(self):
        for rec in self:
            rec.effective_field_ids = rec._get_parents_fields()

    @api.onchange('inherit_fields', 'field_ids')
    def onchange_field_ids(self):
        if self.inherit_fields:
            self._compute_effective_fields()

    #### products
    product_ids = fields.One2many(comodel_name='lighting.product',
                                  inverse_name='category_id', string='Products')

    product_count = fields.Integer(compute='_compute_product_count', string='Product(s)')

    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec.product_ids)

    flat_product_ids = fields.Many2many(comodel_name='lighting.product', compute='_compute_flat_products')

    def _get_flat_products(self):
        self.ensure_one()
        if not self.child_ids:
            return self.product_ids
        else:
            products = self.env['lighting.product']
            for ch in self.child_ids:
                products += ch._get_flat_products()
            return products

    def _compute_flat_products(self):
        for rec in self:
            rec.flat_product_ids = rec._get_flat_products()

    flat_product_count = fields.Integer(compute='_compute_flat_product_count', string='Products (flat)')

    def _compute_flat_product_count(self):
        for rec in self:
            rec.flat_product_count = len(rec.flat_product_ids)

    attachment_ids = fields.One2many(comodel_name='lighting.product.category.attachment',
                                     inverse_name='category_id', string='Attachments', copy=True,
                                     track_visibility='onchange')
    attachment_count = fields.Integer(compute='_compute_attachment_count', string='Attachment(s)')

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = self.env['lighting.product.category.attachment'] \
                .search_count([('category_id', '=', record.id)])

    _sql_constraints = [('name_uniq', 'unique (parent_id,name)', 'The type must be unique by parent!'),
                        ('code_uniq', 'unique (code)', 'The code must be unique!')
                        ]

    def action_child(self):
        return {
            'name': _('Childs of %s') % self.complete_name,
            'type': 'ir.actions.act_window',
            'res_model': 'lighting.product.category',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('id', 'in', self.child_ids.mapped('id'))],
            'context': {'default_parent_id': self.id},
        }

    def action_flat_product(self):
        return {
            'name': _('Flat products below %s') % self.complete_name,
            'type': 'ir.actions.act_window',
            'res_model': 'lighting.product',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('id', 'in', self.flat_product_ids.mapped('id'))],
            'context': {'default_category_id': self.id},
        }

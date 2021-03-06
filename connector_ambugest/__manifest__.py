# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': "Ambugest-Odoo connector",
    'version': '11.0.0.14.1',
    'author': 'NuoBiT Solutions, S.L., Eric Antones',
    'license': 'AGPL-3',
    'category': 'Connector',
    'website': 'https://www.nuobit.com',
    'depends': [
        'partner_review',
        'sale_order_service',
        'connector_common',
        'l10n_es',
    ],
    'external_dependencies': {
        'python': [
            'pymssql',
        ],
    },
    'data': [
        'data/ir_cron.xml',
        'views/ambugest_backend_view.xml',
        'views/partner_view.xml',
        'views/product_product_view.xml',
        'views/sale_order_view.xml',
        'views/connector_ambugest_menu.xml',
        'security/connector_ambugest.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}

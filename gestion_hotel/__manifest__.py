# -*- coding: utf-8 -*-
{
    'name': "Hotel Management",

    'summary': """
            Manage and adminstrate hotel""",

    'description': """
        Keep on eye on everything.
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hotel',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','maintenance','account_tax_python','account','point_of_sale','contacts','hr_attendance','hr','stock','mail'],

    # always loaded
    'data': [
        'security/hotel_access.xml',
        'security/ir.model.access.csv',
        'data/hotel_reservation_sequence.xml',
        'views/root_menu.xml',
        'views/hotel_room.xml',
        'views/hotel_floor.xml',
        'views/hotel_room_type.xml',
        'views/hotel_services.xml',
        'views/hotel_service_type.xml',
        'views/hotel_clients.xml',
        'views/hotel_reservation.xml',
        'views/hotel_room_reservation_summary.xml',
        'views/AccountInvoiceHotel.xml',
        'views/CustomHotelInvoiceTemplateReport.xml',
        'views/assets.xml',
        'views/HotelAccountTax.xml',
        'views/productsReservations.xml',
        'views/hotel_stat_main_courante.xml',
        'views/hotel_ca_clients_charts_view.xml',
        'reports/hotel_main_courant_rapport.xml',
        'reports/hotel_main_courant_template.xml',
        'reports/hotel_free_stat_rooms_101.xml',
        'reports/ca_template_rapport.xml',
        # 'views/hotel_free_rooms_stat.xml',
        'views/hotel_free_stat_room_111.xml',
        'views/hotel_chiffre_affaire.xml',
        # 'data/email_template_view.xml',
    ],
    'demo': [
        'demo/hotel_client_demo.xml',
    ],
    'qweb': ['static/src/xml/hotel_room_summary.xml',
             'static/src/xml/hotel_room_stat_free_.xml',
             'static/src/xml/hotel_ca.xml',
             'static/src/xml/hotel_room_type_mobile.xml',
             ],
    'css': ['static/src/css/theme.css'],
}
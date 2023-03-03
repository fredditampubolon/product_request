#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning

class request_detail(models.Model):

    _name = "vit.request_detail"
    _description = "vit.request_detail"
    name = fields.Char( required=True, string="Name",  help="", )
    spesification = fields.Text( string="Spesification",  help="", )
    brochure = fields.Binary( string="Brochure",  help="", )
    quantity = fields.Integer( string="Quantity",  help="", )
    quantity_moved = fields.Integer( string="Quantity moved",  help="", compute="_compute_detail_qty")
    quantity_po = fields.Integer( string="Quantity po",  help="", compute="_compute_detail_qty")
    quantity_remaining = fields.Integer( string="Quantity remaining",  help="", compute="_compute_detail_qty")


    product_request_id = fields.Many2one(comodel_name="vit.product_request",  string="Product request",  help="", )
    product_id = fields.Many2one(comodel_name="product.product",  string="Product",  help="", )


    def _generate_data_from_transfer(self, transfer_ids, line):
        """
        Generate data from transfer.
        This function will generate quantity for Product Request base in Internal Transfer Activity.

        Args:
            transfer_ids: list => list of internal transfer data.
            line: list => list of product request data.

        Return : 
            qty move => Interger
        """
        move_line_obj = self.env['stock.move.line'].search([
                ('picking_id', 'in', transfer_ids.ids),
                ('product_id', '=', line.product_id.id)
                ])
        if move_line_obj:
            for move_line in move_line_obj:
                line.quantity_moved += move_line.qty_done
        return line.quantity_moved


    def _generate_data_from_purchase(self, po_ids, line):
        """
        Generate data from purchase.
        This function will generate quantity for Product Request base in procurement Activity.

        Args:
            transfer_ids: list => list of purchase order data.
            line: list => list of product request data.

        Return : 
            qty po => Interger
        """
        line_po_obj = self.env['purchase.order.line'].search([
                ('order_id', 'in', po_ids.ids),
                ('product_id', '=', line.product_id.id)
                ])
        for order_line in line_po_obj:
            line.quantity_po += order_line.product_qty
        return line.quantity_po



    def _compute_detail_qty(self):
        """
        Compute detail Qty.
        This function will generate qty move, qty po base on qty on going base on type requested.

        Return : 
            qty move => Interger
            qty po => Integer
        """
        po_ids = self.product_request_id.mapped('po_ids')
        transfer_ids = self.product_request_id.mapped('transfer_ids')

        for line in self:
            internal_transfer = self._generate_data_from_transfer(transfer_ids, line)
            purchase = self._generate_data_from_purchase(po_ids, line)

            line.quantity_remaining = line.quantity - (internal_transfer - purchase)





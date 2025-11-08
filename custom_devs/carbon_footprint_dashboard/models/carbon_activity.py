# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CarbonActivity(models.Model):
    _name = "carbon.activity"
    _description = "Carbon Emission Activity"
    _order = "activity_date desc, id desc"

    name = fields.Char(required=True)
    activity_date = fields.Date(default=fields.Date.context_today, required=True)
    emission_factor_id = fields.Many2one(
        "carbon.emission.factor",
        string="Emission Factor",
        required=True,
    )
    quantity = fields.Float(default=1.0, help="Activity amount in the same unit as the factor")
    emission_amount = fields.Float(
        string="Emission (kg CO2e)",
        compute="_compute_emission_amount",
        store=True,
    )
    source_document = fields.Char(help="External reference or document")
    project_id = fields.Many2one("carbon.project", string="Project")

    @api.depends("quantity", "emission_factor_id.factor")
    def _compute_emission_amount(self):
        for rec in self:
            rec.emission_amount = (rec.quantity or 0.0) * (rec.emission_factor_id.factor or 0.0)

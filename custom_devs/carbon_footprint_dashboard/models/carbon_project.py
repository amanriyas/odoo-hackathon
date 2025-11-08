# -*- coding: utf-8 -*-
from odoo import models, fields

class CarbonProject(models.Model):
    _name = "carbon.project"
    _description = "Carbon Reduction Project"
    _order = "start_date desc, id desc"

    name = fields.Char(required=True)
    start_date = fields.Date()
    end_date = fields.Date()
    target_reduction = fields.Float(help="Target reduction in kg CO2e")
    achieved_reduction = fields.Float(help="Actual reduction in kg CO2e")
    activity_ids = fields.One2many(
        "carbon.activity",
        "project_id",
        string="Related Activities",
    )

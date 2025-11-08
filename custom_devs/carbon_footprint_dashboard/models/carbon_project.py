from odoo import models, fields, api

class CarbonProject(models.Model):
    _name = "carbon.project"
    _description = "Carbon Project"
    _order = "start_date desc, id desc"

    name = fields.Char(required=True)
    start_date = fields.Date()
    end_date = fields.Date()
    target_reduction = fields.Float(string="Target (kg CO2e)")
    achieved_reduction = fields.Float(string="Achieved (kg CO2e)")

    activity_ids = fields.One2many(
        "carbon.activity",
        "project_id",
        string="Activities",
    )

    total_emissions = fields.Float(
        string="Total Emissions (kg CO2e)",
        compute="_compute_totals",
        store=False,
    )
    activity_count = fields.Integer(
        string="Activities",
        compute="_compute_totals",
        store=False,
    )

    @api.depends("activity_ids.emission_amount")
    def _compute_totals(self):
        for rec in self:
            emissions = sum(rec.activity_ids.mapped("emission_amount"))
            rec.total_emissions = emissions
            rec.activity_count = len(rec.activity_ids)

from odoo import models, fields, api
from datetime import date

class CarbonInitiative(models.Model):
    _name = "carbon.initiative"
    _description = "Green Initiative"

    name = fields.Char(required=True)
    category = fields.Selection([
        ('energy', 'Energy'),
        ('waste', 'Waste'),
        ('transport', 'Transport'),
        ('office', 'Office'),
        ('water', 'Water'),
    ], required=True)

    start_date = fields.Date(required=True)
    end_date = fields.Date()

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='draft')

    target_co2_reduction = fields.Float(required=True)
    actual_co2_reduction = fields.Float(
        compute="_compute_actual_reduction", store=True)
    progress_percentage = fields.Float(
        compute="_compute_progress", store=True)

    activity_ids = fields.One2many(
        "carbon.activity", "initiative_id")
    goal_ids = fields.One2many(
        "carbon.goal", "initiative_id")

    # -----------------------------
    #   COMPUTATIONS
    # -----------------------------

    @api.depends("activity_ids.co2_generated", "activity_ids.co2_saved")
    def _compute_actual_reduction(self):
        for rec in self:
            generated = sum(a.co2_generated for a in rec.activity_ids)
            saved = sum(a.co2_saved for a in rec.activity_ids)
            rec.actual_co2_reduction = saved - generated

    @api.depends("target_co2_reduction", "actual_co2_reduction")
    def _compute_progress(self):
        for rec in self:
            if rec.target_co2_reduction > 0:
                pct = (rec.actual_co2_reduction / rec.target_co2_reduction) * 100
                rec.progress_percentage = max(0, min(100, pct))
            else:
                rec.progress_percentage = 0

    @api.onchange("activity_ids")
    def _onchange_state(self):
        """ Improve state logic without adding fields """
        for rec in self:
            if rec.state == "cancelled":
                return  # don't touch cancelled

            if not rec.activity_ids:
                rec.state = "draft"
            elif rec.progress_percentage >= 100:
                rec.state = "completed"
            else:
                rec.state = "active"

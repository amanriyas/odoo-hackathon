from odoo import models, fields, api
from datetime import date

class CarbonGoal(models.Model):
    _name = "carbon.goal"
    _description = "Reduction Goal"

    name = fields.Char(required=True)
    target_date = fields.Date(required=True)
    target_co2_reduction = fields.Float(required=True)

    actual_co2_reduction = fields.Float(
        compute="_compute_actual", store=True)
    achievement_percentage = fields.Float(
        compute="_compute_percentage", store=True)

    state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('achieved', 'Achieved'),
        ('missed', 'Missed'),
    ], compute="_compute_state", store=True)

    initiative_id = fields.Many2one("carbon.initiative", required=True)
    reward_points = fields.Integer()

    # -----------------------------
    #   COMPUTATIONS
    # -----------------------------

    @api.depends("initiative_id.activity_ids", "target_date")
    def _compute_actual(self):
        for rec in self:
            relevant = rec.initiative_id.activity_ids.filtered(
                lambda a: a.activity_date <= rec.target_date
            )
            saved = sum(a.co2_saved for a in relevant)
            generated = sum(a.co2_generated for a in relevant)
            rec.actual_co2_reduction = saved - generated

    @api.depends("target_co2_reduction", "actual_co2_reduction")
    def _compute_percentage(self):
        for rec in self:
            if rec.target_co2_reduction > 0:
                pct = rec.actual_co2_reduction / rec.target_co2_reduction * 100
                rec.achievement_percentage = max(0, min(100, pct))
            else:
                rec.achievement_percentage = 0

    @api.depends("achievement_percentage", "target_date", "initiative_id.activity_ids")
    def _compute_state(self):
        today = date.today()
        for rec in self:

            if not rec.initiative_id.activity_ids:
                rec.state = "pending"
                continue

            if rec.achievement_percentage >= 100:
                rec.state = "achieved"
                continue

            if today <= rec.target_date:
                rec.state = "in_progress"
            else:
                rec.state = "missed"

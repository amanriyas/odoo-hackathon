from odoo import models, fields, api

class CarbonGoal(models.Model):
    _name = 'carbon.goal'
    _description = 'Carbon Reduction Goal'

    name = fields.Char(required=True)
    target_date = fields.Date(required=True)
    target_co2_reduction = fields.Float(required=True)
    actual_co2_reduction = fields.Float(compute='_compute_actual', store=True)
    achievement_percentage = fields.Float(compute='_compute_achievement', store=True)
    state = fields.Selection(compute='_compute_state', store=True)
    initiative_id = fields.Many2one('carbon.initiative', required=True)
    reward_points = fields.Integer()

    @api.depends('actual_co2_reduction','target_co2_reduction')
    def _compute_achievement(self):
        for record in self:
            record.achievement_percentage = (record.actual_co2_reduction / record.target_co2_reduction * 100) if record.target_co2_reduction else 0

    @api.depends('achievement_percentage')
    def _compute_state(self):
        for record in self:
            if record.achievement_percentage >= 100:
                record.state = 'achieved'
            elif fields.Date.today() > record.target_date:
                record.state = 'missed'
            elif record.achievement_percentage > 0:
                record.state = 'in_progress'
            else:
                record.state = 'pending'

    @api.depends('initiative_id.activity_ids.co2_saved')
    def _compute_actual(self):
        for record in self:
            activities = record.initiative_id.activity_ids
            record.actual_co2_reduction = sum(activities.mapped('co2_saved'))

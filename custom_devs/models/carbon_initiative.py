from odoo import models, fields, api

class CarbonInitiative(models.Model):
    _name = 'carbon.initiative'
    _description = 'CSR Environmental Initiative'

    name = fields.Char(required=True)
    category = fields.Selection([
        ('energy', 'Energy'),
        ('waste', 'Waste'),
        ('transport', 'Transport'),
        ('office', 'Office'),
        ('water', 'Water')
    ], required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date()
    state = fields.Selection([
        ('draft','Draft'),
        ('active','Active'),
        ('completed','Completed'),
        ('cancelled','Cancelled')
    ], default='draft')
    target_co2_reduction = fields.Float(required=True)
    actual_co2_reduction = fields.Float(compute='_compute_actual_co2', store=True)
    progress_percentage = fields.Float(compute='_compute_progress', store=True)
    activity_ids = fields.One2many('carbon.activity', 'initiative_id', string='Activities')
    goal_ids = fields.One2many('carbon.goal', 'initiative_id', string='Goals')

    @api.depends('activity_ids.co2_generated', 'activity_ids.co2_saved')
    def _compute_actual_co2(self):
        for record in self:
            record.actual_co2_reduction = sum(record.activity_ids.mapped('co2_saved')) - sum(record.activity_ids.mapped('co2_generated'))

    @api.depends('actual_co2_reduction','target_co2_reduction')
    def _compute_progress(self):
        for record in self:
            record.progress_percentage = (record.actual_co2_reduction / record.target_co2_reduction * 100) if record.target_co2_reduction else 0

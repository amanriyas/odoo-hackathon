from odoo import models, fields, api

class CarbonActivity(models.Model):
    _name = 'carbon.activity'
    _description = 'Carbon Activity'

    name = fields.Char(compute='_compute_name', store=True)
    activity_type = fields.Selection([
        ('electricity','Electricity'),
        ('fuel','Fuel'),
        ('paper','Paper'),
        ('waste','Waste'),
        ('water','Water')
    ], required=True)
    activity_date = fields.Date(required=True)
    quantity = fields.Float(required=True)
    unit = fields.Selection([
        ('kwh','kWh'),
        ('liters','Liters'),
        ('kg','Kg'),
        ('sheets','Sheets')
    ], required=True)
    emission_factor = fields.Float()
    co2_generated = fields.Float(compute='_compute_co2', store=True)
    co2_saved = fields.Float()
    initiative_id = fields.Many2one('carbon.initiative', string='Initiative')
    employee_id = fields.Many2one('hr.employee', string='Employee')

    @api.depends('activity_type','quantity','emission_factor')
    def _compute_co2(self):
        for record in self:
            record.co2_generated = record.quantity * (record.emission_factor or 0)

    @api.depends('activity_type','activity_date')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.activity_type} on {record.activity_date}"

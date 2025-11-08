from odoo import models, fields

class CarbonEmissionFactor(models.Model):
    _name = "carbon.emission.factor"
    _description = "Carbon Emission Factor"
    _order = "name"

    name = fields.Char(required=True)
    category = fields.Char()
    unit_of_measure = fields.Char(string="Unit", default="kWh")
    factor = fields.Float(
        string="Emission Factor (kg CO2e per unit)",
        required=True,
    )

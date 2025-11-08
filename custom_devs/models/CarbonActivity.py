from odoo import models, fields, api

class CarbonActivity(models.Model):
    _name = "carbon.activity"
    _description = "Carbon Activity Record"

    name = fields.Char(compute="_compute_name", store=True)
    activity_type = fields.Selection([
        ('electricity', 'Electricity'),
        ('fuel', 'Fuel'),
        ('paper', 'Paper'),
        ('travel', 'Travel'),
        ('waste', 'Waste'),
        ('water', 'Water'),
    ], required=True)

    activity_date = fields.Date(required=True)
    quantity = fields.Float(required=True)
    unit = fields.Selection([
        ('kwh', 'kWh'),
        ('liters', 'Liters'),
        ('kg', 'Kilograms'),
        ('km', 'Kilometers'),
        ('sheets', 'Sheets'),
    ], required=True)

    emission_factor = fields.Float()
    co2_generated = fields.Float(compute="_compute_co2", store=True)
    co2_saved = fields.Float(compute="_compute_co2", store=True)

    initiative_id = fields.Many2one("carbon.initiative")
    employee_id = fields.Many2one("res.users")

    # -----------------------------
    #   COMPUTED FIELDS
    # -----------------------------

    @api.depends("activity_type", "quantity", "unit", "activity_date")
    def _compute_name(self):
        for rec in self:
            qty_display = f"{rec.quantity}{rec.unit}" if rec.quantity else ""
            date_display = rec.activity_date or ""
            rec.name = f"{rec.activity_type.capitalize()} - {qty_display} ({date_display})"

    @api.depends("quantity", "emission_factor", "activity_type")
    def _compute_co2(self):
        for rec in self:

            factor = rec.emission_factor or 0  # robust fallback

            # Default behavior:
            rec.co2_generated = 0
            rec.co2_saved = 0

            # Emission-related activity
            if rec.activity_type in ("electricity", "fuel", "travel", "waste"):
                rec.co2_generated = rec.quantity * factor

            # Reduction-related activity
            if rec.activity_type in ("paper", "office", "water"):
                rec.co2_saved = rec.quantity * factor

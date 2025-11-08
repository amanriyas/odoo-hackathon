from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CarbonActivity(models.Model):
    _name = "carbon.activity"
    _description = "Carbon Emission Activity"
    _order = "activity_date desc, id desc"

    name = fields.Char()
    activity_date = fields.Date(required=True, default=fields.Date.context_today)
    emission_factor_id = fields.Many2one(
        "carbon.emission.factor",
        string="Emission Factor",
        required=True,
    )
    quantity = fields.Float(required=True, default=1.0)
    emission_amount = fields.Float(
        string="Emission (kg CO2e)",
        compute="_compute_emission_amount",
        store=True,
    )
    source_document = fields.Char()
    project_id = fields.Many2one("carbon.project", string="Project")

    @api.depends("quantity", "emission_factor_id.factor")
    def _compute_emission_amount(self):
        for rec in self:
            rec.emission_amount = (rec.quantity or 0.0) * (rec.emission_factor_id.factor or 0.0)

    @api.constrains("quantity")
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError("Quantity must be greater than 0.")

    @api.model
    def create(self, vals):
        # If a list of vals (bulk create), handle each one
        if isinstance(vals, list):
            for val in vals:
                if not val.get("name"):
                    val["name"] = self.env["ir.sequence"].next_by_code("carbon.activity") or "Activity"
            return super(CarbonActivity, self).create(vals)

        # If a single record
        if not vals.get("name"):
            vals["name"] = self.env["ir.sequence"].next_by_code("carbon.activity") or "Activity"
        return super(CarbonActivity, self).create(vals)

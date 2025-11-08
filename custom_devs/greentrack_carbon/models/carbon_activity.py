# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


# UAE Standard Emission Factors
EMISSION_FACTORS = {
    'electricity': 0.45,  # kg CO2 per kWh (UAE Grid Average)
    'fuel': 2.31,         # kg CO2 per liter (Gasoline - EPA Standard)
    'paper': 0.01,        # kg CO2 per sheet (Industry Average)
    'travel': 0.12,       # kg CO2 per km (Average Sedan)
    'waste': 0.5,         # kg CO2 per kg (Landfill Average)
    'water': 0.0003,      # kg CO2 per liter (Treatment Process)
}


class CarbonActivity(models.Model):
    """Carbon Activity - Individual carbon-generating or carbon-saving events"""

    _name = "carbon.activity"
    _description = "Carbon Activity"
    _order = "activity_date desc"
    _rec_name = "name"

    # Auto-generated name
    name = fields.Char(
        string="Activity Description",
        compute='_compute_name',
        store=True,
        help="Auto-generated description of the activity"
    )

    # Activity Details
    activity_type = fields.Selection(
        selection=[
            ('electricity', 'Electricity Usage'),
            ('fuel', 'Fuel Consumption'),
            ('paper', 'Paper Usage'),
            ('travel', 'Travel (Car/Transport)'),
            ('waste', 'Waste Generated'),
            ('water', 'Water Usage'),
        ],
        string="Activity Type",
        required=True,
        help="Type of carbon-generating or saving activity"
    )

    activity_date = fields.Date(
        string="Activity Date",
        required=True,
        default=fields.Date.context_today,
        help="When did this activity occur?"
    )

    # Quantity and Measurements
    quantity = fields.Float(
        string="Quantity",
        required=True,
        help="How much? (e.g., 100 kWh, 50 liters, 500 sheets)",
        default=0.0
    )

    unit = fields.Selection(
        selection=[
            ('kwh', 'kWh (Kilowatt-hours)'),
            ('liters', 'Liters'),
            ('kg', 'Kilograms'),
            ('km', 'Kilometers'),
            ('sheets', 'Sheets'),
        ],
        string="Unit",
        required=True,
        help="Unit of measurement"
    )

    # Emission Calculations
    emission_factor = fields.Float(
        string="Emission Factor",
        help="kg CO2 per unit (auto-filled from API or defaults)",
        digits=(12, 4),
        default=0.0
    )

    co2_generated = fields.Float(
        string="CO2 Generated (kg)",
        compute='_compute_co2',
        store=True,
        help="Total CO2 generated: quantity × emission_factor"
    )

    co2_saved = fields.Float(
        string="CO2 Saved (kg)",
        help="For reduction activities - positive value means CO2 saved",
        default=0.0
    )

    # Relationships
    initiative_id = fields.Many2one(
        comodel_name='carbon.initiative',
        string="Initiative",
        ondelete='cascade',
        help="Link to carbon reduction initiative"
    )

    employee_id = fields.Many2one(
        comodel_name='res.users',
        string="Employee",
        default=lambda self: self.env.user,
        help="Employee who logged this activity"
    )

    # Source tracking
    source = fields.Selection(
        selection=[
            ('manual', 'Manual Entry'),
            ('api', 'API Integration'),
            ('system', 'System Generated'),
        ],
        string="Data Source",
        default='manual',
        help="How was this activity recorded?"
    )

    # Notes
    notes = fields.Text(
        string="Notes",
        help="Additional comments or details about this activity"
    )

    # Computed Methods
    @api.depends('activity_type', 'quantity', 'activity_date')
    def _compute_name(self):
        """Auto-generate descriptive name for the activity"""
        for activity in self:
            if activity.activity_type and activity.quantity:
                type_label = dict(activity._fields['activity_type'].selection).get(activity.activity_type, '')
                unit_label = dict(activity._fields['unit'].selection).get(activity.unit, '') if activity.unit else ''
                date_str = activity.activity_date.strftime('%Y-%m-%d') if activity.activity_date else 'No date'

                activity.name = f"{type_label} - {activity.quantity} {unit_label} on {date_str}"
            else:
                activity.name = "New Activity"

    @api.depends('quantity', 'emission_factor')
    def _compute_co2(self):
        """Calculate CO2 generated based on quantity and emission factor"""
        for activity in self:
            if activity.quantity and activity.emission_factor:
                activity.co2_generated = round(activity.quantity * activity.emission_factor, 2)

                # If co2_saved is not manually set, use co2_generated as the saved amount
                # (assuming this is a reduction activity)
                if not activity.co2_saved:
                    activity.co2_saved = activity.co2_generated

                _logger.info(
                    f"Activity CO2 calculation: {activity.quantity} × {activity.emission_factor} = "
                    f"{activity.co2_generated} kg CO2"
                )
            else:
                activity.co2_generated = 0.0

    # Onchange Methods
    @api.onchange('activity_type')
    def _onchange_activity_type(self):
        """Auto-fill emission factor and recommended unit when activity type changes"""
        if self.activity_type:
            # Get emission factor from defaults
            emission_factor = self._get_default_emission_factor(self.activity_type)
            self.emission_factor = emission_factor

            # Set recommended unit based on activity type
            unit_mapping = {
                'electricity': 'kwh',
                'fuel': 'liters',
                'paper': 'sheets',
                'travel': 'km',
                'waste': 'kg',
                'water': 'liters',
            }
            self.unit = unit_mapping.get(self.activity_type, 'kg')

            _logger.info(
                f"Activity type changed to '{self.activity_type}': "
                f"Emission factor = {emission_factor}, Unit = {self.unit}"
            )

    # Helper Methods
    def _get_default_emission_factor(self, activity_type):
        """
        Get default emission factor for activity type
        This method can be extended in Phase 4 to fetch from external API
        """
        return EMISSION_FACTORS.get(activity_type, 0.0)

    # Constraints
    @api.constrains('quantity')
    def _check_quantity(self):
        """Ensure quantity is positive"""
        for activity in self:
            if activity.quantity < 0:
                raise ValidationError(
                    _('Quantity must be a positive value!')
                )

    @api.constrains('emission_factor')
    def _check_emission_factor(self):
        """Ensure emission factor is non-negative"""
        for activity in self:
            if activity.emission_factor < 0:
                raise ValidationError(
                    _('Emission factor cannot be negative!')
                )

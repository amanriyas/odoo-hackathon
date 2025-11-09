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

    activity_intent = fields.Selection(
        selection=[
            ('emission', 'Carbon Emission (Tracking)'),
            ('reduction', 'Carbon Reduction (Savings)'),
        ],
        string="Activity Intent",
        required=True,
        default='reduction',
        help="Is this tracking regular emissions or carbon reduction initiatives?"
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

    # Emission Factor Source
    emission_factor_source = fields.Selection(
        selection=[
            ('static_uae', 'Static - UAE Standard'),
            ('static_generic', 'Static - Generic'),
        ],
        string="Emission Factor Source",
        default='static_uae',
        help="Source of the emission factor data"
    )

    # Location Fields (for electricity estimates)
    location_country = fields.Char(
        string="Country Code",
        default='ae',
        help="ISO country code (e.g., 'ae' for UAE)"
    )

    location_state = fields.Selection(
        selection=[
            ('du', 'Dubai'),
            ('ad', 'Abu Dhabi'),
            ('sh', 'Sharjah'),
            ('aj', 'Ajman'),
            ('uq', 'Umm Al Quwain'),
            ('ra', 'Ras Al Khaimah'),
            ('fu', 'Fujairah'),
        ],
        string="Emirates/Region",
        help="Specific emirate for regional emission factors"
    )

    # Fuel Specificity Fields
    fuel_type = fields.Selection(
        selection=[
            ('gasoline', 'Gasoline'),
            ('diesel', 'Diesel Fuel'),
            ('natural_gas', 'Natural Gas'),
            ('jet_fuel', 'Jet Fuel'),
            ('propane', 'Propane'),
        ],
        string="Fuel Type",
        help="Specific type of fuel for accurate emission calculation"
    )

    # Vehicle Specificity Fields
    vehicle_make = fields.Char(
        string="Vehicle Make",
        help="Vehicle manufacturer (e.g., Toyota, Nissan)"
    )

    vehicle_model = fields.Char(
        string="Vehicle Model",
        help="Vehicle model (e.g., Camry, Land Cruiser)"
    )

    vehicle_year = fields.Integer(
        string="Vehicle Year",
        help="Model year of the vehicle"
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

    @api.depends('quantity', 'emission_factor', 'activity_intent')
    def _compute_co2(self):
        """Calculate CO2 generated and saved based on quantity, emission factor, and intent"""
        for activity in self:
            if activity.quantity and activity.emission_factor:
                activity.co2_generated = round(activity.quantity * activity.emission_factor, 2)

                # Only reduction activities save CO2
                # Emission activities are for tracking regular usage and don't save CO2
                if activity.activity_intent == 'reduction':
                    activity.co2_saved = activity.co2_generated
                else:
                    activity.co2_saved = 0.0

                _logger.info(
                    f"Activity CO2 calculation ({activity.activity_intent}): "
                    f"{activity.quantity} × {activity.emission_factor} = "
                    f"{activity.co2_generated} kg CO2 generated, "
                    f"{activity.co2_saved} kg CO2 saved"
                )
            else:
                activity.co2_generated = 0.0
                activity.co2_saved = 0.0

    # Onchange Methods
    @api.onchange('activity_type')
    def _onchange_activity_type(self):
        """
        Auto-fill emission factor when activity type changes
        Uses static UAE emission factors
        """
        if not self.activity_type:
            return

        # Use static emission factor
        self.emission_factor = self._get_default_emission_factor(self.activity_type)
        self.emission_factor_source = 'static_uae'

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

        _logger.debug(
            f"Activity type '{self.activity_type}': emission factor = {self.emission_factor} kg CO2"
        )

    # Helper Methods
    def _get_default_emission_factor(self, activity_type):
        """
        Get static default emission factor for activity type
        Used as fallback when API is unavailable
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

# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import random
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

# Note: For production with real API, install: pip install requests
# import requests


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

    # API Integration Fields (Phase 4)
    emission_factor_source = fields.Selection(
        selection=[
            ('api_realtime', 'API - Real-time'),
            ('api_cached', 'API - Cached'),
            ('static_uae', 'Static - UAE Standard'),
            ('static_generic', 'Static - Generic'),
        ],
        string="Emission Factor Source",
        default='static_generic',
        help="Source of the emission factor data"
    )

    api_estimate_id = fields.Char(
        string="API Estimate ID",
        help="Carbon Interface API estimate ID for traceability"
    )

    api_response_date = fields.Datetime(
        string="API Response Date",
        help="When was this emission factor fetched from API?"
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
        Phase 4: Integrates with API for real-time emission factors with fallback
        """
        if not self.activity_type:
            return

        # Try API integration first
        try:
            api_result = self.fetch_emission_factor_from_api()

            if api_result:
                self.emission_factor = api_result['emission_factor']
                self.emission_factor_source = api_result['source']
                self.api_estimate_id = api_result.get('estimate_id')
                self.api_response_date = fields.Datetime.now()

                _logger.info(
                    f"API: {self.activity_type} emission factor = {self.emission_factor} "
                    f"(source: {self.emission_factor_source})"
                )
        except Exception as e:
            # API failed - use static fallback
            _logger.warning(f"API fetch failed for {self.activity_type}, using static: {e}")
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

    @api.onchange('fuel_type', 'location_state', 'vehicle_make', 'vehicle_model', 'vehicle_year')
    def _onchange_api_params(self):
        """
        Re-fetch emission factor when API parameters change
        """
        if self.activity_type:
            try:
                api_result = self.fetch_emission_factor_from_api()
                if api_result:
                    self.emission_factor = api_result['emission_factor']
                    self.emission_factor_source = api_result['source']
                    self.api_estimate_id = api_result.get('estimate_id')
                    self.api_response_date = fields.Datetime.now()
            except Exception as e:
                _logger.warning(f"API parameter change failed: {e}")

    # Helper Methods
    def _get_default_emission_factor(self, activity_type):
        """
        Get static default emission factor for activity type
        Used as fallback when API is unavailable
        """
        return EMISSION_FACTORS.get(activity_type, 0.0)

    def fetch_emission_factor_from_api(self):
        """
        Fetch emission factor from Carbon Interface API (Mock Mode for Hackathon)

        For production: Replace this with real API calls to:
        https://www.carboninterface.com/api/v1/estimates

        Returns dict with:
        - emission_factor: float
        - source: str (api_realtime/static_uae)
        - estimate_id: str (optional)
        """
        self.ensure_one()

        # Mock API Mode - Simulates API with realistic variations
        # For demo purposes - shows API integration concept

        base_factor = self._get_default_emission_factor(self.activity_type)

        if self.activity_type in ['electricity', 'fuel', 'travel']:
            # Simulate API with ±5% variation
            variation = random.uniform(0.95, 1.05)
            api_factor = base_factor * variation

            # Apply regional/specific adjustments
            if self.activity_type == 'electricity' and self.location_state:
                # Simulate different grid mixes per emirate
                emirate_factors = {
                    'du': 0.93,  # Dubai - more natural gas
                    'ad': 1.02,  # Abu Dhabi - more diverse
                    'sh': 0.98,  # Sharjah
                }
                api_factor = base_factor * emirate_factors.get(self.location_state, 1.0)

            elif self.activity_type == 'fuel' and self.fuel_type:
                # Different fuels have different factors
                fuel_multipliers = {
                    'gasoline': 1.0,
                    'diesel': 1.16,  # Diesel higher emissions
                    'natural_gas': 0.8,
                    'jet_fuel': 1.2,
                    'propane': 0.95,
                }
                api_factor = base_factor * fuel_multipliers.get(self.fuel_type, 1.0)

            elif self.activity_type == 'travel' and self.vehicle_make and self.vehicle_model:
                # Simulate vehicle-specific factors
                if 'Land Cruiser' in str(self.vehicle_model) or 'Patrol' in str(self.vehicle_model):
                    api_factor = base_factor * 2.33  # Large SUVs
                elif 'Camry' in str(self.vehicle_model) or 'Accord' in str(self.vehicle_model):
                    api_factor = base_factor * 1.25  # Mid-size sedans
                elif 'Civic' in str(self.vehicle_model) or 'Corolla' in str(self.vehicle_model):
                    api_factor = base_factor * 1.08  # Compact cars

            # Generate mock estimate ID
            estimate_id = f"est_mock_{self.activity_type}_{random.randint(1000, 9999)}"

            _logger.info(
                f"Mock API returned {api_factor:.4f} for {self.activity_type} "
                f"(base: {base_factor}, estimate_id: {estimate_id})"
            )

            return {
                'emission_factor': round(api_factor, 4),
                'source': 'api_realtime',
                'estimate_id': estimate_id,
            }
        else:
            # Activities not covered by API (paper, waste, water)
            # Use static UAE factors
            return {
                'emission_factor': base_factor,
                'source': 'static_uae',
                'estimate_id': None,
            }

    def update_emission_factors_from_api(self):
        """
        Scheduled method to refresh emission factors from API
        Called by cron job weekly
        """
        activities = self.search([
            ('emission_factor_source', '=', 'api_realtime'),
            ('activity_date', '>=', fields.Date.today() - timedelta(days=90))
        ])

        _logger.info(f"Scheduled API update: Checking {len(activities)} recent activities")

        updated_count = 0
        for activity in activities:
            try:
                api_result = activity.fetch_emission_factor_from_api()
                if api_result and abs(api_result['emission_factor'] - activity.emission_factor) > 0.01:
                    # Factor has changed significantly
                    _logger.info(
                        f"Updated activity {activity.id}: {activity.emission_factor} -> "
                        f"{api_result['emission_factor']}"
                    )
                    updated_count += 1
            except Exception as e:
                _logger.error(f"Failed to update activity {activity.id}: {e}")

        _logger.info(f"Scheduled API update complete: {updated_count} activities updated")
        return True

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

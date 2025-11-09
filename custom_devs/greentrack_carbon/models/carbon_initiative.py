# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class CarbonInitiative(models.Model):
    """Carbon Reduction Initiative - Represents CSR environmental programs/projects"""

    _name = "carbon.initiative"
    _description = "Carbon Reduction Initiative"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "start_date desc"
    _rec_name = "name"

    # Avoid conflicts with mail.activity.mixin
    _mail_post_access = 'read'

    # Basic Information
    name = fields.Char(
        string="Initiative Name",
        required=True,
        tracking=True,
        help="Name of the carbon reduction initiative"
    )

    description = fields.Text(
        string="Description",
        help="What is this initiative about? Objectives and scope."
    )

    category = fields.Selection(
        selection=[
            ('energy', 'Energy Efficiency'),
            ('waste', 'Waste Reduction'),
            ('transport', 'Sustainable Transport'),
            ('office', 'Green Office'),
            ('water', 'Water Conservation'),
        ],
        string="Category",
        required=True,
        tracking=True,
        help="Type of environmental initiative"
    )

    # Dates
    start_date = fields.Date(
        string="Start Date",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        help="When does this initiative begin?"
    )

    end_date = fields.Date(
        string="End Date",
        tracking=True,
        help="When does this initiative end? (Optional for ongoing programs)"
    )

    # Status
    state = fields.Selection(
        selection=[
             ('completed', 'Completed'),
             ('active', 'Active'),
            ('draft', 'Draft'),
            ('cancelled', 'Cancelled'),
        ],
        string="Status",
        required=True,
        default='draft',
        tracking=True,
        help="Current status of the initiative"
    )

    # CO2 Targets and Progress
    target_co2_reduction = fields.Float(
        string="Target CO2 Reduction (kg)",
        required=True,
        help="Goal: How many kg of CO2 should this initiative reduce?",
        default=0.0
    )

    actual_co2_reduction = fields.Float(
        string="Actual CO2 Reduction (kg)",
        compute='_compute_actual_reduction',
        store=True,
        help="Actually reduced CO2 based on logged activities"
    )

    progress_percentage = fields.Float(
        string="Progress (%)",
        compute='_compute_progress',
        store=True,
        help="Percentage of target achieved"
    )

    # Relationships
    carbon_activity_ids = fields.One2many(
        comodel_name='carbon.activity',
        inverse_name='initiative_id',
        string="Carbon Activities",
        help="Carbon activities associated with this initiative"
    )

    goal_ids = fields.One2many(
        comodel_name='carbon.goal',
        inverse_name='initiative_id',
        string="Goals",
        help="Milestones and targets for this initiative"
    )

    # UI and Display

    activity_count = fields.Integer(
        string="Activity Count",
        compute='_compute_activity_count',
        help="Number of activities logged for this initiative"
    )

    # AI Prediction Fields (Phase 5)
    predicted_next_month_co2 = fields.Float(
        string="Predicted Next Month CO2 (kg)",
        compute='_compute_ai_predictions',
        help="AI prediction for CO2 savings next month"
    )

    trend_indicator = fields.Selection(
        selection=[
            ('improving', 'Improving'),
            ('stable', 'Stable'),
            ('declining', 'Declining'),
        ],
        string="Trend",
        compute='_compute_ai_predictions',
        help="Trend analysis: improving, stable, or declining"
    )

    top_activity_type = fields.Char(
        string="Top Activity Type",
        compute='_compute_ai_predictions',
        help="Activity type with highest CO2 savings contribution"
    )

    prediction_confidence = fields.Float(
        string="Prediction Confidence (%)",
        compute='_compute_ai_predictions',
        help="Confidence score for AI predictions (0-100%)"
    )

    # Computed Methods
    @api.depends('carbon_activity_ids', 'carbon_activity_ids.co2_saved')
    def _compute_actual_reduction(self):
        """Calculate total CO2 saved from all activities"""
        for initiative in self:
            total_saved = sum(initiative.carbon_activity_ids.mapped('co2_saved'))
            initiative.actual_co2_reduction = total_saved
            _logger.info(
                f"Initiative '{initiative.name}': Computed CO2 reduction = {total_saved} kg "
                f"from {len(initiative.carbon_activity_ids)} activities"
            )

    @api.depends('actual_co2_reduction', 'target_co2_reduction')
    def _compute_progress(self):
        """Calculate progress percentage"""
        for initiative in self:
            if initiative.target_co2_reduction > 0:
                progress = (initiative.actual_co2_reduction / initiative.target_co2_reduction) * 100
                initiative.progress_percentage = round(progress, 2)
            else:
                initiative.progress_percentage = 0.0

    @api.depends('carbon_activity_ids')
    def _compute_activity_count(self):
        """Count number of activities"""
        for initiative in self:
            initiative.activity_count = len(initiative.carbon_activity_ids)

    @api.depends('carbon_activity_ids', 'carbon_activity_ids.co2_saved', 'carbon_activity_ids.activity_date')
    def _compute_ai_predictions(self):
        """Calculate AI predictions using the prediction engine"""
        prediction_engine = self.env['carbon.prediction']

        for initiative in self:
            # Only compute if we have sufficient data (at least 2 activities)
            if len(initiative.carbon_activity_ids) >= 2:
                try:
                    # Predict next month CO2
                    initiative.predicted_next_month_co2 = prediction_engine.predict_next_month_co2(initiative.id)

                    # Calculate trend
                    initiative.trend_indicator = prediction_engine.calculate_trend(initiative.id)

                    # Get top activity type
                    initiative.top_activity_type = prediction_engine.get_top_activity_type(initiative.id)

                    # Get confidence score
                    initiative.prediction_confidence = prediction_engine.get_confidence_score(initiative.id)

                    _logger.debug(
                        f"AI predictions for '{initiative.name}': "
                        f"Predicted={initiative.predicted_next_month_co2} kg, "
                        f"Trend={initiative.trend_indicator}, "
                        f"Top Type={initiative.top_activity_type}"
                    )
                except Exception as e:
                    _logger.warning(f"Failed to compute AI predictions for initiative {initiative.id}: {e}")
                    initiative.predicted_next_month_co2 = 0.0
                    initiative.trend_indicator = 'stable'
                    initiative.top_activity_type = False
                    initiative.prediction_confidence = 0.0
            else:
                # Insufficient data
                initiative.predicted_next_month_co2 = 0.0
                initiative.trend_indicator = 'stable'
                initiative.top_activity_type = False
                initiative.prediction_confidence = 0.0

    # Constraints
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Ensure end date is after start date"""
        for initiative in self:
            if initiative.end_date and initiative.start_date:
                if initiative.end_date < initiative.start_date:
                    raise ValidationError(
                        _('End date must be after start date!')
                    )

    @api.constrains('target_co2_reduction')
    def _check_target(self):
        """Ensure target is positive"""
        for initiative in self:
            if initiative.target_co2_reduction < 0:
                raise ValidationError(
                    _('Target CO2 reduction must be a positive value!')
                )

    # Action Methods for Smart Buttons
    def action_view_activities(self):
        """Open activities related to this initiative"""
        self.ensure_one()
        return {
            'name': _('Carbon Activities'),
            'type': 'ir.actions.act_window',
            'res_model': 'carbon.activity',
            'view_mode': 'list,form',
            'domain': [('initiative_id', '=', self.id)],
            'context': {
                'default_initiative_id': self.id,
            },
        }

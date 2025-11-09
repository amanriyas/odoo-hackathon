# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class CarbonGoal(models.Model):
    """Carbon Reduction Goal - Reduction targets and milestones"""

    _name = "carbon.goal"
    _description = "Carbon Reduction Goal"
    _order = "target_date desc"
    _rec_name = "name"

    # Basic Information
    name = fields.Char(
        string="Goal Name",
        required=True,
        help="Name of this carbon reduction goal or milestone"
    )

    description = fields.Text(
        string="Description",
        help="Details about this goal and how to achieve it"
    )

    # Target Settings
    target_date = fields.Date(
        string="Target Date",
        required=True,
        help="Deadline to achieve this goal"
    )

    target_co2_reduction = fields.Float(
        string="Target CO2 Reduction (kg)",
        required=True,
        help="How many kg of CO2 should be reduced by the target date?",
        default=0.0
    )

    # Progress Tracking
    actual_co2_reduction = fields.Float(
        string="Actual CO2 Reduction (kg)",
        compute='_compute_actual',
        store=True,
        help="Current progress - CO2 reduced so far from initiative activities"
    )

    achievement_percentage = fields.Float(
        string="Achievement (%)",
        compute='_compute_achievement',
        store=True,
        help="Percentage of target achieved: (actual/target) × 100"
    )

    # Goal Status
    state = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('achieved', 'Achieved'),
            ('missed', 'Missed'),
        ],
        string="Status",
        compute='_compute_state',
        store=True,
        help="Current status of the goal based on achievement and deadline"
    )

    # Relationship
    initiative_id = fields.Many2one(
        comodel_name='carbon.initiative',
        string="Initiative",
        required=True,
        ondelete='cascade',
        help="Carbon initiative this goal belongs to"
    )

    # Impact Display
    impact = fields.Text(
        compute='_compute_impact',
        string="Impact",
        help="Environmental impact equivalent of achieving this goal"
    )

    # Computed Methods
    @api.depends('target_co2_reduction')
    def _compute_impact(self):
        """Compute impact and display in familiar terms like saved trees, cars off road, etc."""
        for goal in self:
            if goal.target_co2_reduction > 0:
                trees_saved = goal.target_co2_reduction / 21.77
                cars_off_road = goal.target_co2_reduction / 4040
                
                trees_formatted = "{:,.0f}".format(trees_saved)
                cars_formatted = "{:,.1f}".format(cars_off_road)
                co2_formatted = "{:,.0f}".format(goal.target_co2_reduction)
                
                tree_plural = 'S' if trees_saved != 1 else ''
                car_plural = 'S' if cars_off_road != 1 else ''
                
                goal.impact = (
                    "  🌳  " + trees_formatted + " TREE" + tree_plural + " PLANTED\n"
                    "      └─ Absorbing CO2 for an entire year\n"
                    "\n"
                    "  🚗  " + cars_formatted + " CAR" + car_plural + " OFF THE ROAD\n"
                    "      └─ Equivalent to 365 days of emissions\n"
                    "\n"
                    "  💚  " + co2_formatted + " KG CO2 PREVENTED\n"
                    "      └─ Making a real difference for our planet!\n"
                    "\n"
                )
            else:
                goal.impact = "Set a target reduction to see environmental impact"

    @api.depends('initiative_id', 'initiative_id.carbon_activity_ids', 'initiative_id.carbon_activity_ids.co2_saved', 'target_date')
    def _compute_actual(self):
        """
        Calculate actual CO2 reduction from initiative activities up to target date
        Only counts activities that occurred before or on the target date
        """
        for goal in self:
            if goal.initiative_id and goal.target_date:
                # Get all activities from the initiative up to the target date
                activities = goal.initiative_id.carbon_activity_ids.filtered(
                    lambda a: a.activity_date and a.activity_date <= goal.target_date
                )
                total_saved = sum(activities.mapped('co2_saved'))
                goal.actual_co2_reduction = total_saved

                _logger.info(
                    f"Goal '{goal.name}': Computed actual reduction = {total_saved} kg CO2 "
                    f"from {len(activities)} activities up to {goal.target_date}"
                )
            else:
                goal.actual_co2_reduction = 0.0

    @api.depends('actual_co2_reduction', 'target_co2_reduction')
    def _compute_achievement(self):
        """Calculate achievement percentage"""
        for goal in self:
            if goal.target_co2_reduction > 0:
                achievement = (goal.actual_co2_reduction / goal.target_co2_reduction) * 100
                goal.achievement_percentage = round(achievement, 2)
            else:
                goal.achievement_percentage = 0.0

    @api.depends('achievement_percentage', 'target_date', 'actual_co2_reduction')
    def _compute_state(self):
        """
        Determine goal state based on achievement and deadline
        Logic:
        - pending: No progress yet (0% achievement)
        - in_progress: Some progress, deadline not yet passed
        - achieved: Target met or exceeded (≥100%)
        - missed: Deadline passed but target not met
        """
        for goal in self:
            today = date.today()

            if goal.achievement_percentage >= 100:
                # Target achieved or exceeded
                goal.state = 'achieved'
                _logger.info(
                    f"Goal '{goal.name}' achieved! "
                    f"Reduced {goal.actual_co2_reduction} kg CO2"
                )

            elif goal.actual_co2_reduction == 0:
                # No progress yet
                goal.state = 'pending'

            elif goal.target_date and goal.target_date < today:
                # Deadline has passed but target not met
                goal.state = 'missed'

            else:
                # Some progress, deadline still in future
                goal.state = 'in_progress'

    # Constraints
    @api.constrains('target_date')
    def _check_target_date(self):
        """Warn if target date is in the past (but don't block)"""
        for goal in self:
            if goal.target_date and goal.target_date < date.today():
                _logger.warning(
                    f"Goal '{goal.name}' has target date in the past: {goal.target_date}"
                )

    @api.constrains('target_co2_reduction')
    def _check_target(self):
        """Ensure target is positive"""
        for goal in self:
            if goal.target_co2_reduction <= 0:
                raise ValidationError(
                    _('Target CO2 reduction must be greater than zero!')
                )

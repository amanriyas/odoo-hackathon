# -*- coding: utf-8 -*-

from odoo import models, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from statistics import mean, stdev
import logging

_logger = logging.getLogger(__name__)


class CarbonPrediction(models.AbstractModel):
    """
    Carbon Prediction Engine
    Provides AI/ML predictions for carbon initiatives using statistical analysis
    """

    _name = 'carbon.prediction'
    _description = 'Carbon Prediction Engine'

    def get_monthly_data(self, initiative_id, months=6):
        """
        Extract and aggregate activities by month for an initiative

        Args:
            initiative_id: ID of carbon.initiative
            months: Number of past months to analyze

        Returns:
            list of tuples: [(month_number, total_co2_saved), ...]
        """
        initiative = self.env['carbon.initiative'].browse(initiative_id)

        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - relativedelta(months=months)

        # Get activities in date range
        activities = initiative.carbon_activity_ids.filtered(
            lambda a: a.activity_date >= start_date and a.activity_date <= end_date
        )

        if not activities:
            return []

        # Group by month
        monthly_data = {}
        for activity in activities:
            # Get month key (months since start_date)
            months_diff = (activity.activity_date.year - start_date.year) * 12 + \
                         (activity.activity_date.month - start_date.month)

            if months_diff not in monthly_data:
                monthly_data[months_diff] = 0.0

            monthly_data[months_diff] += activity.co2_saved

        # Convert to sorted list of tuples
        result = sorted(monthly_data.items())

        _logger.debug(f"Monthly data for initiative {initiative_id}: {result}")
        return result

    def simple_linear_regression(self, data_points):
        """
        Calculate linear regression manually (without numpy)

        Args:
            data_points: list of tuples [(x1, y1), (x2, y2), ...]

        Returns:
            dict: {'slope': m, 'intercept': b, 'r_squared': r2}
        """
        if not data_points or len(data_points) < 2:
            return {'slope': 0, 'intercept': 0, 'r_squared': 0}

        n = len(data_points)
        x_values = [x for x, y in data_points]
        y_values = [y for x, y in data_points]

        # Calculate means
        mean_x = mean(x_values)
        mean_y = mean(y_values)

        # Calculate slope and intercept using least squares method
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in data_points)
        denominator = sum((x - mean_x) ** 2 for x in x_values)

        if denominator == 0:
            slope = 0
            intercept = mean_y
        else:
            slope = numerator / denominator
            intercept = mean_y - slope * mean_x

        # Calculate R-squared
        ss_total = sum((y - mean_y) ** 2 for y in y_values)
        ss_residual = sum((y - (slope * x + intercept)) ** 2 for x, y in data_points)

        r_squared = 1 - (ss_residual / ss_total) if ss_total > 0 else 0

        return {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_squared
        }

    @api.model
    def predict_next_month_co2(self, initiative_id):
        """
        Predict CO2 savings for the next month

        Args:
            initiative_id: ID of carbon.initiative

        Returns:
            float: Predicted CO2 savings in kg
        """
        # Get historical data (last 6 months)
        monthly_data = self.get_monthly_data(initiative_id, months=6)

        if not monthly_data or len(monthly_data) < 2:
            # Insufficient data - return average if any data exists
            if monthly_data:
                return monthly_data[0][1]
            return 0.0

        # Perform linear regression
        regression = self.simple_linear_regression(monthly_data)

        # Predict next month (one month beyond last data point)
        last_month_number = monthly_data[-1][0]
        next_month_number = last_month_number + 1

        predicted_co2 = regression['slope'] * next_month_number + regression['intercept']

        # Ensure non-negative prediction
        predicted_co2 = max(0, predicted_co2)

        _logger.info(
            f"Prediction for initiative {initiative_id}: {predicted_co2:.2f} kg CO2 "
            f"(slope: {regression['slope']:.2f}, R²: {regression['r_squared']:.2f})"
        )

        return round(predicted_co2, 2)

    @api.model
    def calculate_trend(self, initiative_id):
        """
        Calculate trend: improving, stable, or declining

        Args:
            initiative_id: ID of carbon.initiative

        Returns:
            str: 'improving', 'stable', or 'declining'
        """
        monthly_data = self.get_monthly_data(initiative_id, months=6)

        if not monthly_data or len(monthly_data) < 3:
            return 'stable'  # Insufficient data

        # Split into recent (last 3 months) vs earlier (first 3 months)
        if len(monthly_data) >= 6:
            earlier = [y for x, y in monthly_data[:3]]
            recent = [y for x, y in monthly_data[-3:]]
        else:
            # If less than 6 months, split in half
            mid = len(monthly_data) // 2
            earlier = [y for x, y in monthly_data[:mid]]
            recent = [y for x, y in monthly_data[mid:]]

        avg_earlier = mean(earlier)
        avg_recent = mean(recent)

        # Calculate percentage change
        if avg_earlier > 0:
            pct_change = ((avg_recent - avg_earlier) / avg_earlier) * 100
        else:
            pct_change = 0

        # Classify trend
        if pct_change > 10:
            return 'improving'
        elif pct_change < -10:
            return 'declining'
        else:
            return 'stable'

    @api.model
    def get_top_activity_type(self, initiative_id):
        """
        Identify which activity type contributes most to CO2 savings

        Args:
            initiative_id: ID of carbon.initiative

        Returns:
            str: Activity type label (e.g., 'Electricity Usage')
        """
        initiative = self.env['carbon.initiative'].browse(initiative_id)

        if not initiative.carbon_activity_ids:
            return False

        # Sum CO2 saved by activity type
        type_totals = {}
        for activity in initiative.carbon_activity_ids:
            activity_type = activity.activity_type
            if activity_type not in type_totals:
                type_totals[activity_type] = 0.0
            type_totals[activity_type] += activity.co2_saved

        if not type_totals:
            return False

        # Find top contributor
        top_type = max(type_totals.items(), key=lambda x: x[1])[0]

        # Get human-readable label
        activity_type_labels = dict(
            self.env['carbon.activity']._fields['activity_type'].selection
        )

        return activity_type_labels.get(top_type, top_type)

    @api.model
    def get_confidence_score(self, initiative_id):
        """
        Calculate confidence score for predictions based on data quality

        Args:
            initiative_id: ID of carbon.initiative

        Returns:
            float: Confidence score 0-100%
        """
        monthly_data = self.get_monthly_data(initiative_id, months=6)

        if not monthly_data:
            return 0.0

        # Base confidence on data volume
        data_volume_score = min(len(monthly_data) / 6.0, 1.0) * 40  # Max 40 points

        # Calculate regression R-squared if enough data
        if len(monthly_data) >= 3:
            regression = self.simple_linear_regression(monthly_data)
            r_squared_score = regression['r_squared'] * 60  # Max 60 points
        else:
            r_squared_score = 0

        confidence = data_volume_score + r_squared_score

        return round(min(confidence, 100), 1)

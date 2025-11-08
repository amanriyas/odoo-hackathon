# -*- coding: utf-8 -*-
{
    'name': 'GreenTrack - Carbon Intelligence Platform',
    'version': '1.0.0',
    'category': 'Sustainability',
    'summary': 'AI-Powered Carbon Management for UAE Enterprises - Net Zero 2050',
    'description': """
        GreenTrack - Carbon Intelligence Platform
        ==========================================

        Empowers UAE organizations to plan, manage, and measure the impact of their
        CSR and sustainability initiatives, aligned with Net Zero 2050 and UN SDGs.

        Key Features:
        -------------
        * Track carbon-generating activities in real-time
        * Visualize environmental impact through interactive dashboards
        * Predict future emissions using AI/ML
        * Generate actionable recommendations
        * Gamify sustainability to drive employee engagement
        * Automatic CSR compliance reporting

        Core Modules:
        -------------
        * Carbon Initiatives - Environmental programs and projects
        * Carbon Activities - Individual emission and reduction events
        * Carbon Goals - Milestones and targets with gamification

        Innovation Features:
        -------------------
        * External API integration for real-world emission factors
        * AI/ML predictive analytics
        * Interactive dashboards with charts and pivot tables
        * Workflow automation and smart notifications
    """,
    'author': 'GreenTrack Team',
    'website': 'https://www.greentrack.ae',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/carbon_initiative_views.xml',
        'views/carbon_activity_views.xml',
        'views/carbon_goal_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
        'data/cron_jobs.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 10,
}

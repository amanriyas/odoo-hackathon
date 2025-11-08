# -*- coding: utf-8 -*-
{
    "name": "Carbon Footprint Dashboard",
    "version": "19.0.1.0.0",
    "summary": "Track emission activities, factors and projects",
    "author": "Aquib (hackathon)",
    "website": "",
    "category": "Tools",
    "depends": ["base"],
    "data": [
        "security/carbon_security.xml",
        "security/ir.model.access.csv",
        "data/carbon_emission_factor_data.xml",
        "views/carbon_emission_factor_views.xml",
        "views/carbon_activity_views.xml",
        "views/carbon_project_views.xml",
        "views/menu_views.xml",
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}

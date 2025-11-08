{
    "name": "Carbon Footprint Dashboard",
    "version": "19.0.3.0.0",
    "summary": "Simple carbon activities, factors and projects",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/carbon_emission_factor_data.xml",
        "data/demo_data.xml",
        "views/carbon_emission_factor_views.xml",
        "views/carbon_activity_views.xml",
        "views/carbon_project_views.xml",
        "views/menu_views.xml",
    ],
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}
{
    'name': 'GreenTrack CSR Tracker',
    'version': '1.0',
    'author': 'Dynasty',
    'depends': ['base', 'hr'],  
    'data': [
        'security/ir.model.access.csv',
        'views/carbon_initiative_views.xml',
        'views/carbon_activity_views.xml',
        'views/carbon_goal_views.xml',
    ],
    'installable': True,
    'application': True,
}

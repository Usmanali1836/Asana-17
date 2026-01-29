# -*- coding: utf-8 -*-

{
    'name': 'Asana Odoo Connector',
    'version': '17.0.1.0.0',
    'category': 'Project',
    'summary': "With this module, you can easily connect the projects, tasks "
               "and partners in the odoo to asana",
    'description': """With this module, user can connect the projects, tasks and
    the customers in the odoo to asana, which means the projects, tasks and 
    customers in the odoo can be seen in the asana also vice versa""",
    'author': 'Lahore Analytica',
    'company': 'Lahore Analytica',
    'maintainer': 'Lahore Analytica',
    'website': "https://www.lahoreanalytica.com/",
    'depends': ['project'],
    'data': [
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'views/project_task_type_views.xml',
        'views/res_config_settings_views.xml',
        'data/ir_actions_data.xml',
    ],
    'external_dependencies': {
        'python': [
            'asana',
        ],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

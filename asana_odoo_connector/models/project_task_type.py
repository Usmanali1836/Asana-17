# -*- coding: utf-8 -*-

from odoo import fields, models


class ProjectTaskType(models.Model):
    """
    Inherits the model project.task.type to add the extra fields for importing
    and exporting of the data from odoo to asana
    """
    _inherit = 'project.task.type'

    asana_ref = fields.Char(string='Asana Reference',
                            help='Asana Reference ID for the project record')

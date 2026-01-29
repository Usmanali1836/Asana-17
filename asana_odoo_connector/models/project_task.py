# -*- coding: utf-8 -*-
###############################################################################
#    Lahore Analytica
###############################################################################
from odoo import fields, models


class ProjectTask(models.Model):
    """
    Inherits the model project.task to add extra fields for the working of
    importing and exporting of the data from odoo to asana
    """
    _inherit = 'project.task'

    asana_ref = fields.Char(string='Asana Reference',
                            help='Asana Reference ID for the project record')

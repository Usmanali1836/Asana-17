# -*- coding: utf-8 -*-

import logging
import requests
from odoo import fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
try:
    import asana
except ImportError:
    _logger.debug('Cannot `import asana`.')


def action_show_notification(success):
    """
    Method action_show_notification used to notify whether the connection to the asana is
    successful or not.
    """
    notification = {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': _('Connection successful!') if success is True else _(
                'Connection not successful!'),
            'message': 'Connection to Asana is successful.' if success is True else 'Connection to Asana is not successful.',
            'sticky': True,
            'type': 'success' if success is True else 'danger'
        }
    }
    return notification


def action_fetch_project_stages(project_gid, api_client):
    """
    Method action_fetch_project_stages used to import the project stages from
    asana to odoo
    """
    api_instance = asana.SectionsApi(api_client)
    section_response = api_instance.get_sections_for_project(
        project_gid)
    return section_response


class ResConfigSettings(models.TransientModel):
    """
    Inherits the model Res Config Settings to add extra fields and
    functionalities to this model
    """
    _inherit = 'res.config.settings'

    asana_workspace_ref = fields.Char(string='Workspace ID',
                                help='ID of the workspace in asana',
                                config_parameter='asana_odoo_connector.asana_workspace_ref')
    asana_app_token = fields.Char(string='App Token',
                            help='Personal Access Token of the corresponding '
                                 'asana account',
                            config_parameter='asana_odoo_connector.asana_app_token')

    def action_test_connection(self):
        """
        Method action_test_connection to test the connection from odoo to asana
        """
        workspace_gid = self.asana_workspace_ref
        api_endpoint = f'https://app.asana.com/api/1.0/workspaces/{workspace_gid}'
        access_token = self.asana_app_token
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        response = requests.get(api_endpoint, headers=headers, timeout=10)
        if response.status_code == 200:
            success = True
            notification = action_show_notification(success)
            self.env['ir.config_parameter'].sudo().set_param(
                'asana_odoo_connector.connection_successful', True)
            return notification
        success = False
        notification = action_show_notification(success)
        return notification

    def action_fetch_projects(self):
        """
        Method action_fetch_projects to import the project from asana to odoo
        """
        configuration = asana.Configuration()
        configuration.access_token = self.asana_app_token
        api_client = asana.ApiClient(configuration)
        project_instance = asana.ProjectsApi(api_client)
        section_instance = asana.SectionsApi(api_client)
        workspace = self.asana_workspace_ref
        opts = {
            'workspace': workspace
        }
        try:
            project_response = project_instance.get_projects(opts)
            for project in project_response:
                asana_gid = project['gid']
                existing_project = self.env['project.project'].search(
                    [('asana_ref', '=', asana_gid)])
                if not existing_project:
                    opts = {}
                    section_data = section_instance.get_sections_for_project(
                        asana_gid, opts)
                    type_ids = [
                        (0, 0, {'name': section['name'],
                                'asana_ref': section['gid']})
                        for section in section_data]
                    new_project = self.env['project.project'].create({
                        'name': project['name'],
                        'asana_ref': asana_gid,
                        'type_ids': type_ids
                    })
                else:
                    pass
        except Exception as exc:
            raise ValidationError(
                _('Please check the workspace ID or the app token')) from exc
    def action_sync_all_tasks(self):
        """
        Method action_sync_all_tasks to import tasks from asana to odoo
        for all linked projects
        """
        configuration = asana.Configuration()
        configuration.access_token = self.asana_app_token
        api_client = asana.ApiClient(configuration)
        
        # Search for all projects that have an Asana GID
        projects = self.env['project.project'].search([('asana_ref', '!=', False)])
        
        try:
            for project in projects:
                self.action_fetch_tasks(
                    api_client=api_client,
                    project_id=project.id,
                    asana_gid=project.asana_ref
                )
            
            success = True
            notification = action_show_notification(success)
            notification['params']['message'] = 'Tasks imported successfully for all linked projects.'
            return notification
            
        except Exception as exc:
             raise ValidationError(
                _('Error importing tasks. Please check connection.')) from exc

    def action_fetch_tasks(self, api_client, project_id, asana_gid):
        """
        Method action_fetch_tasks to import tasks from the asana to odoo
        """
        api_instance = asana.TasksApi(api_client)
        section_instance = asana.SectionsApi(api_client)
        opts = {}
        section_data = section_instance.get_sections_for_project(asana_gid,
                                                                 opts)
        for section in section_data:
            opts ={}
            task_response = api_instance.get_tasks_for_section(section['gid'],
                                                               opts)
            for task in task_response:
                existing_task = self.env['project.task'].search(
                    [('asana_ref', '=', task['gid']),
                     ('project_id', '=', project_id)])
                if not existing_task:
                    self.env['project.task'].create({
                        'name': task['name'],
                        'project_id': project_id,
                        'asana_ref': task['gid'],
                        'stage_id': self.env['project.task.type'].search(
                            [('asana_ref', '=', section['gid']),
                             ('project_ids', '=', project_id)]).id,
                    })

# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP,  Open Source Management Solution,  third party addon
#    Copyright (C) 2019 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation,  either version 3 of the
#    License,  or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not,  see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    onboard_stage_id = fields.Many2one(comodel_name="hr.onboard.stage")
    onboard_respons_ids = fields.Many2many(comodel_name='survey.user_input')
    email = fields.Char(string='Email', track_visibility='onchange')
    login = fields.Char(related='user_id.login', track_visibility='onchange')

    @api.model
    def _read_group_onboard_stage_id(self, present_ids, domain, **kwargs):
        stages = self.env['hr.onboard.stage'].search([]).name_get()
        folded = {
            self.env.ref('hr_onboarding.state_completed').id: True
        }
        return stages, folded

    _group_by_full = {
        'onboard_stage_id': _read_group_onboard_stage_id
    }

    @api.multi
    def action_onboard_form(self):
        self.ensure_one()
        if self.onboard_stage_id.view_id:
            view = self.env.ref('hr_onboarding.wizard_employee_form_hr_onboard_company_info')
            return {
                'type': 'ir.actions.act_window',
                'name': _('Update Company Info'),
                'key2': 'client_action_multi',
                'res_model': 'hr.employee.company.info.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view.id,
                'target': 'new',
                'context': {},
            }
        if self.onboard_stage_id.survey_id:
            return self.onboard_stage_id.survey_id.action_start_survey()


class hr_onboard_stage(models.Model):
    """
   Stages in onboarding
    """
    _name = 'hr.onboard.stage'
    _description = "Onboard Stage"

    name = fields.Char(string='Name', required=True)
    technical_name = fields.Char(string='Technical Name', required=True)
    sequence = fields.Integer(string='Sequence')
    color = fields.Integer(string='Color Index')
    fold = fields.Boolean(string='Folded in Kanban View', help='This stage is folded in the kanban view when there are no records in that state to display.')
    view_id = fields.Many2one(comodel_name='ir.ui.view', strig='View')
    survey_id = fields.Many2many(comodel_name='survey.survey', string='Survey')


class survey_survey(models.Model):
    _inherit = 'survey.survey'

    @api.one
    def save_lines(self, user_input_id, question, post, answer_tag):
        # TODO: catch question datas
        return super(survey_survey, self).save_lines(user_input_id, question, post, answer_tag)


class hr_employee_company_info_wizard(models.TransientModel):
    _name = 'hr.employee.company.info.wizard'

    user_name = fields.Char(string='User Name', help='Name for login', required=True)
    password = fields.Char(string='Password', required=True)
    confirm_password = fields.Char(string='Confirm Password', required=True)
    email = fields.Char(string='Email', required=True)

    @api.multi
    def confirm(self):
        # TODO: check password
        pass

class hr_employee_contract_info_wizard(models.TransientModel):
    _name = 'hr.employee.contract.info.wizard'

    department_id = fields.Char(string='Department', comodel_name='hr.department')
    job_id = fields.Char(string='Job', comodel_name='hr.job')

    @api.multi
    def confirm(self):
        pass

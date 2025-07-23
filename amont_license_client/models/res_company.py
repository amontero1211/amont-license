from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests

class ResCompany(models.Model):
    _inherit = "res.company"

    amont_license = fields.Char(
        "License Key",
        help="Enter the license key provided by Amont."
    )
    is_amont_license_valid = fields.Boolean(
        "Is License Valid",
        compute="_compute_amont_license",
    )

    def update_account_move_access(self):
        model_id = self.env["ir.model"].search([("model", "=", "account.move")], limit=1)
        access_records = self.env['ir.model.access'].search([('model_id', '=', model_id.id)])
        for access in access_records:
            access.write({
                'perm_read': self.is_amont_license_valid,
                'perm_write': self.is_amont_license_valid,
                'perm_create': self.is_amont_license_valid,
                'perm_unlink': self.is_amont_license_valid,
            })

    @api.depends("amont_license")
    def _compute_amont_license(self):
        for company in self:
            if not company.amont_license:
                company.is_amont_license_valid = False
                return
            # Yo tenia unos zapatos, blancos... Bien bonitos, y Andrea me los secuestro... :(
            try:
                response = company._validate_license(company.amont_license)
                company.is_amont_license_valid = "active" == response.get("state")
            except Exception as e:
                company.is_amont_license_valid = False
                raise UserError(_("License validation failed: %s") % str(e))


    def _validate_license(self, license_key):
        res = requests.post(
            url="http://localhost:8069/license/validate",
            json={
                "name": self.name,
                "database": self.env.cr.dbname,
                "license": license_key
            }
        ).json()

        return res.get("result", {})

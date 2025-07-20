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

    @api.depends("amont_license")
    def _compute_amont_license(self):
        if self.amont_license:
            try:
                # Simulate a license validation call
                response = self._validate_license(self.amont_license)
                self.is_amont_license_valid = "active" == response.get("state")
            except Exception as e:
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

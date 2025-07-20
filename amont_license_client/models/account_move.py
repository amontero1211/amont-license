from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    is_amont_license_valid = fields.Boolean(related="company_id.is_amont_license_valid")

    @api.model_create_multi
    def create(self, vals_list):
        # Ensure that the company has a valid Amont license before creating an account move
        for vals in vals_list:
            if not vals.get("company_id"):
                continue
            
            company = self.env["res.company"].browse(vals["company_id"])
            if not company.is_amont_license_valid:
                raise UserError(_("Cannot create account move: Amont license is not active for this company."))
        
        return super().create(vals_list)

    def validate_amont_license(self):
        print("Validating Amont license for account move...")
        return self.is_amont_license_valid

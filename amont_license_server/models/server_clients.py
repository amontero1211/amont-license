from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import uuid
import hashlib

STATE = [
    ("active", "Active"),
    ("expired", "Expired")
]

class ServerClient(models.Model):
    _name = "amont.server.client"
    _description = "Customers associated with the server"


    name = fields.Char(required=True)
    database = fields.Char(required=True)
    license = fields.Char()
    state = fields.Selection(STATE, compute="_compute_state")
    start_date = fields.Date()
    end_date = fields.Date()


    @api.depends("start_date", "end_date")
    def _compute_state(self):
        for client in self:
            if client.start_date and client.end_date:
                flag = client.start_date <= fields.Date.today() <= client.end_date
                client.state = "active" if flag else "expired"
            else:
                client.state = "expired"


    def generate_license(self):
        # Generar un UUID aleatorio
        generated_uuid = uuid.uuid4()
        
        # Crear un hash SHA-256 para mayor seguridad
        hash_license = hashlib.sha256(str(generated_uuid).encode()).hexdigest()
        
        # Formatear la clave de licencia
        self.license = "-".join([hash_license[i:i+5] for i in range(0, 25, 5)]).upper()
        self.start_date = fields.Date.today()
        self.end_date = fields.Datetime.now() + relativedelta(years=1)


    @api.model
    def validate_license(self, client, database, license):
        return self.search_read([
            ("name", "=", client),
            ("database", "=", database),
            ("license", "=", license),
        ], fields=["name", "database", "license", "state"])
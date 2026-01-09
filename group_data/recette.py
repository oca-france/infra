import os

environement_name = "recette"
odoo_admin_password = os.environ["ODOO_OCA_FRANCE_ADMIN_PASSWORD_RECETTE"]
server_env_ir_config_parameters = [
    "ribbon.name=RECETTE",
]
    
from pyinfra import host, local

local.include("tasks/common.py")
local.include("tasks/fail2ban.py")

if "odoo" in host.groups:
    local.include("tasks/odoo_base.py")
    local.include("tasks/oca_france.py")

if "send_prod_to_recette" in host.groups:
    local.include("tasks/send_prod_to_recette.py")
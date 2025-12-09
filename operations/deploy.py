from pyinfra import host, local

local.include("tasks/common.py")

if "odoo" in host.groups:
    local.include("tasks/odoo_base.py")
    local.include("tasks/oca_france.py")
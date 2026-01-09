from pyinfra import host, local

local.include("tasks/common.py")
local.include("tasks/fail2ban.py")

if "odoo" in host.groups:
    local.include("tasks/odoo_base.py")
    local.include("tasks/oca_france.py")

    if "odoo_weekly_restore" in host.groups:
        local.include("tasks/odoo_weekly_restore.py")

    if "odoo_daily_backup" in host.groups:
        local.include("tasks/odoo_daily_backup.py")

    if "odoo_auto_deploy" in host.groups:
        local.include("tasks/odoo_auto_deploy.py")
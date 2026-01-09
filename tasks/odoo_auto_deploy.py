from pyinfra.operations import server, files, systemd
from pyinfra import host

odoo_user = host.data.odoo_username
odoo_home = f"/home/{odoo_user}"


files.template(
    name="Deploy odoo-auto-deploy.sh script",
    src="templates/odoo-auto-deploy.sh.j2",
    dest=f"{odoo_home}/scripts/odoo-auto-deploy",
    user=odoo_user,
    group=odoo_user,
    mode="755",
    odoo_username=odoo_user,
    _su_user=odoo_user,
)
files.template(
    name="Deploy odoo-auto-deploy.service",
    src="templates/odoo-auto-deploy.service.j2",
    dest="/etc/systemd/system/odoo-auto-deploy.service",
    user="root",
    group="root",
    mode="644",
    odoo_username=odoo_user,
)

files.template(
    name="Deploy odoo-auto-deploy.timer",
    src="templates/odoo-auto-deploy.timer.j2",
    dest="/etc/systemd/system/odoo-auto-deploy.timer",
    user="root",
    group="root",
    mode="644",
)

# Enable and start the auto-deploy timer
systemd.service(
    name="Enable and start odoo-auto-deploy.timer",
    service="odoo-auto-deploy.timer",
    enabled=True,
    running=True,
    daemon_reload=True,
    _sudo=True,
)

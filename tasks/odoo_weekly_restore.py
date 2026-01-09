from pyinfra.operations import server, files, systemd
from pyinfra import host



odoo_user = host.data.odoo_username
odoo_home = f"/home/{odoo_user}"
dumps_dir = f"{odoo_home}/.odoo_dumps"

server.user_authorized_keys(
    name="Deploy odoo-backup public key",
    user=host.data.odoo_username,
    public_keys=[
        "files_secret/odoo-backup.pub",
    ],
)
files.directory(
    name="Create dump directory",
    path=dumps_dir,
    user=odoo_user,
    group=odoo_user,
    mode="755",
    _su_user=odoo_user,
)

files.template(
    name="Deploy odoo-weekly-deploy.service",
    src="templates/odoo-weekly-deploy.service.j2",
    dest="/etc/systemd/system/odoo-weekly-deploy.service",
    user="root",
    group="root",
    mode="644",
    odoo_username=odoo_user,
)

files.template(
    name="Deploy odoo-weekly-deploy.timer",
    src="templates/odoo-weekly-deploy.timer.j2",
    dest="/etc/systemd/system/odoo-weekly-deploy.timer",
    user="root",
    group="root",
    mode="644",
)

# Enable and start the weekly timer
systemd.service(
    name="Enable and start odoo-weekly-deploy.timer",
    service="odoo-weekly-deploy.timer",
    enabled=True,
    running=True,
    daemon_reload=True,
    _sudo=True,
)

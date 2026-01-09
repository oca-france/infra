from pyinfra.operations import server, files
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
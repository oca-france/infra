import io
from pyinfra.operations import files, systemd, server
from pyinfra import host

odoo_user = host.data.odoo_username
odoo_home = f"/home/{odoo_user}"
ssh_dir = f"{odoo_home}/.ssh"
scripts_dir = f"{odoo_home}/scripts"
dumps_dir = f"{odoo_home}/.odoo_dumps"

# 1. Deploy SSH private key
files.directory(
    name="Ensure .ssh directory exists",
    path=ssh_dir,
    user=odoo_user,
    group=odoo_user,
    mode="700",
    _su_user=odoo_user,
)

files.put(
    name="Deploy odoo-backup private key",
    src="files_secret/odoo-backup",
    dest=f"{ssh_dir}/id_odoo_backup",
    user=odoo_user,
    group=odoo_user,
    mode="600",
    _su_user=odoo_user,
)

# 2. Configure SSH config
ssh_config_content = f"""
Host oca-france-recette
    HostName 51.91.29.181
    Port 11083
    User odoo
    IdentityFile ~/.ssh/id_odoo_backup
    StrictHostKeyChecking no
"""

files.put(
    name="Configure SSH for odoo user",
    dest=f"{ssh_dir}/config",
    src=io.StringIO(ssh_config_content.strip()),
    user=odoo_user,
    group=odoo_user,
    mode="644",
    _su_user=odoo_user,
)

# 3. Create dump directory
files.directory(
    name="Create dump directory",
    path=dumps_dir,
    user=odoo_user,
    group=odoo_user,
    mode="755",
    _su_user=odoo_user,
)

# 4. Deploy the sync script
files.template(
    name="Deploy send_to_recette.sh script",
    src="templates/odoo-send-to-recette.sh.j2",
    dest=f"{scripts_dir}/send_to_recette.sh",
    user=odoo_user,
    group=odoo_user,
    mode="755",
    odoo_username=odoo_user,
    working_directory=f"{odoo_home}/oca-france",
    database_name="oca-france-production",
    _su_user=odoo_user,
)

# 5. Deploy systemd service and timer
# We deploy these to /etc/systemd/system/ so they can be managed by root but run as odoo
service_name = "odoo-send-to-recette"

files.template(
    name=f"Deploy {service_name}.service",
    src="templates/odoo-send-to-recette.service.j2",
    dest=f"/etc/systemd/system/{service_name}.service",
    user="root",
    group="root",
    mode="644",
    odoo_username=odoo_user,
)

files.template(
    name=f"Deploy {service_name}.timer",
    src="templates/odoo-send-to-recette.timer.j2",
    dest=f"/etc/systemd/system/{service_name}.timer",
    user="root",
    group="root",
    mode="644",
)

# 6. Enable and start the timer
systemd.service(
    name=f"Enable and start {service_name}.timer",
    service=f"{service_name}.timer",
    enabled=True,
    running=True,
    daemon_reload=True,
    _sudo=True,
)

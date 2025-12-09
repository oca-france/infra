"""Here we setup things with root that are required for Odoo instance"""
from pyinfra.operations import apt, snap, server, postgresql, files, systemd
from pyinfra import host

# make use uv is present
# install from curl to get version 0.9.11 with 
# exclude-dependencies support
# snap.package(
#     name="Install uv",
#     packages=["astral-uv", ],
#     classic=True,
# )
# make sure odoo user is set
server.user(
    name="Create Odoo server user",
    user=host.data.odoo_username,
    shell="/bin/bash",
    present=True,
)

postgresql.role(
    name="Crate Odoo postgresql user role",
    role=host.data.odoo_username,
    present= True,
    # password: str | None = None,
    login = True,
    superuser = False,
    createdb= True,
    # Details for speaking to PostgreSQL via `psql` CLI
    # psql_user: str | None = None,
    # psql_password: str | None = None,
    # psql_host: str | None = None,
    # psql_port: int | None = None,
    # psql_database: str | None = None,
    _su_user="postgres"
)
# allow Odoo user to launch systemd unit that programm run as him

polkit_config = files.template(
    name=f"Configure odoo systemd polkit rule",
    src=f"templates/odoo-systemd-polkit-rule.rules.j2",
    dest="/etc/polkit-1/rules.d/50-odoo-service.rules",
    user="root",
    group="root",
    mode="655",
    user_name=host.data.odoo_username,
)

systemd.service(
    name=f"Ensure polkit rules are take into account",
    service=f"polkit.service",
    running=True,
    reloaded=polkit_config.changed,
    daemon_reload=polkit_config.changed,
    restarted=polkit_config.changed,
    enabled=True,
)

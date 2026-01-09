"""Here we setup all things that we can do as Odoo user"""
from group_data.prod import environement_name
from pyinfra.operations import git, files, systemd
from pyinfra import host

working_directory = f"/home/{host.data.odoo_username}/oca-france"
data_directory = f"/home/{host.data.odoo_username}/oca-france-data"
odoo_config_path = f"/home/{host.data.odoo_username}/.odoorc"

# clone repository to the proper version
git.repo(
    name="OCA Odoo project",
    src="https://github.com/oca-france/oca-france-custom",
    dest=f"/home/{host.data.odoo_username}/oca-france",
    branch="18.0",
    pull=True,
    rebase=False,
    # user: str | None=None,
    # group: str | None=None,
    # ssh_keyscan=False,
    # update_submodules=False,
    # recursive_submodules=False, **kwargs,
    _su_user=host.data.odoo_username,
)

# first setup db done manually
# odoo@oca-france:~/oca-france$ uv run click-odoo-initdb -c ~/.odoorc -n oca-france-production -m oca_france_all --log-level info --no-cache --no-demo
# and then enable unaccent extention: 
# oca-france-production=> CREATE EXTENSION unaccent;

odoo_config = files.template(
    name=f"odoo.conf",
    src=f"templates/odoo.conf.j2",
    dest=odoo_config_path,
    mode="655",
    odoo_data=data_directory,
    admin_passwd=host.data.odoo_admin_password,
    environement_name=host.data.environement_name,
    server_env_ir_config_parameters=host.data.server_env_ir_config_parameters,
    _su_user=host.data.odoo_username
)
git_changed = git.worktree(
    name="OCA Odoo project",
    worktree=working_directory,
    detached=False,
    new_branch="prod",
    commitish="18.0",
    assume_repo_exists=True,
    force=True,
    # from_remote_branch: tuple[str, str] | None=None,
    #  assume_repo_exists=False,
    _su_user=host.data.odoo_username,
)

service_config = files.template(
    name=f"Configure odoo-oca-france systemd unit",
    src=f"templates/odoo-oca-france.service.j2",
    dest="/etc/systemd/system/odoo-oca-france.service",
    user="root",
    group="root",
    mode="655",
    working_directory=working_directory,
    user_name=host.data.odoo_username,
    environement_name=host.data.environement_name,
    config_path=odoo_config_path,
)
if service_config.changed:
    systemd.daemon_reload(
        name="relaod systemd unints",
    )

systemd.service(
    name=f"Ensure odoo-oca-france.service is enabled and running",
    service=f"odoo-oca-france.service",
    running=True,
    restarted=service_config.changed or git_changed.changed,
    enabled=True,
    command=None,
    _su_user=host.data.odoo_username,
)

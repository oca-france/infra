from pyinfra.operations import apt, server

update_apt_repos = apt.update(
    name="Update apt repositories",
    cache_time=86400,  # 86400s is 24 hours
)

if update_apt_repos.changed:
    apt.upgrade(name="Upgrade apt packages")


# Update package list and install packages
apt.packages(
    name="Install acl required by some pyinfra states",
    packages=["acl"],
)

server.locale(
    name="Ensure fr_FR.UTF-8 locale is present",
    locale="fr_FR.UTF-8",
)

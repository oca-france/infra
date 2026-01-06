from pyinfra.operations import apt, systemd

apt.packages(
    name="Ensure fail2ban is installed",
    packages=["fail2ban"],
)

systemd.service(
    name=f"Ensure fail2ban.service is enabled and running",
    service="fail2ban.service",
    running=True,
    command=None,
    enabled=True,
)

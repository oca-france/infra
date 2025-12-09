# Infra OCA France

## Project Purpose
This project is a configuration manager based on [pyinfra](https://pyinfra.com/)
to manage the configuration of LXD containers provided by Aunéor Conseil.

## Usage

### Environment Variables

This project uses environment variables for configuration, including secrets.
1. Copy the template:
   ```bash
   cp .env.template .env
   ```
2. Edit `.env` and fill in the required variables (e.g., `ODOO_OCA_FRANCE_ADMIN_PASSWORD_PROD`).
   > **Note**: This file contains secrets, so it is git-ignored. Ensure you handle it securely.

### SSH Configuration

To successfully connect to the servers, ensure your SSH config (`~/.ssh/config`) includes the following hosts:

```ssh
Host oca-france-recette
  Hostname test.oca-fance.fr
  User <USER>
  Port <USE_PROPER_PORT>
  IdentityFile <PATH_TO_YOUR_KEY>

Host oca-france-prod
  Hostname www.oca-france.fr
  User <USER>
  Port <USE_PROPER_PORT>
  IdentityFile <PATH_TO_YOUR_KEY>
```

### Running Commands

Please refer to the `Makefile` for available commands and usage.
```bash
make help
```
Example to apply configuration to the receipt environment:
```bash
make apply-recette
```

## States Description

The configuration is split into different "states" or tasks:

- **`common`** (`tasks/common.py`): Handles basic system setup, including:
  - Updating and upgrading `apt` packages.
  - Installing essential packages (e.g., `acl`).
  - Setting up the locale (`fr_FR.UTF-8`).

- **`odoo_base`** (`tasks/odoo_base.py`): Prepares the server for Odoo:
  - Creates the Odoo system user.
  - Creates the PostgreSQL user role.
  - Configures Polkit rules to allow the Odoo user to manage specific systemd services.

- **`oca_france`** (`tasks/oca_france.py`): Deploys and configures the specific OCA France Odoo instance:
  - Manages the source code via Git.
  - Generates the Odoo configuration file (`.odoorc`).
  - Sets up and manages the Systemd service (`odoo-oca-france.service`).

## Odoo Instance Focus

The Odoo instance is deployed using the `oca_france` state. It ensures:
- The code is pulled from the `oca-france-custom` repository.
- A virtual environment (managed by `uv`) is used for dependencies.
- The instance runs as a systemd service, configured via templates.

## Roadmap / Ideas

- [ ] Implement Fail2ban for better security.
- [ ] Add monitoring tools.

## Odoo Deployment Workflow

I would recommand to use this repository to configure scripts
that helps github action to update test and production environments but not
rely on pyinfra to actually deploy new Odoo version while both should not
conflict.

### Test Environment

The goal is to update the test environment automatically when code is merged.

- **Trigger**: Merge to the `18.0` branch.
- **Data**: Updates with a neutralized database dump from the previous day.
- **Action**: GitHub Action connects via SSH to the receipt server.
    - Stop odoo service.
    - Dump the current test database.
    - Drop the current test database.
    - Restore the last neutralized dump.
    - Synchronise filesotre.
    - Update the code to the head of the `18.0` branch.
    - Start odoo service, which will:
        - Install python dependencies.
        - Update odoo modules.
        - run the service


### Production Environment

The production environment changes are controlled via tags.

- **Trigger**: Pushing a "gliding" tag named `production`.
- **Permissions**: Restricted rights on who can push this tag.
- **Action**: CI triggers and updates the production instance.
    - Stop odoo service.
    - Dump the current production database.
    - Update the code to the `production` tag.
    - Start odoo service, which will:
        - Install python dependencies.
        - Update odoo modules.
        - run the service

### Manual CI Actions

- Mechanism to manually trigger a restoration of the previous day's anonymized dump such as the [test environment deployment](#test-environment).

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

## Odoo Deployment Workflow

The deployment is managed by a core script located at `/home/odoo/scripts/deploy`. This script handles service stopping, database dumping, code updates (reset hard to a git reference), optional database restoration, and service restarting.

Currently, we do not use GitHub Actions directly to push code but rather rely on the server to pull and deploy via scheduled tasks or manual triggers.

### Recette (Test Environment)

The recette environment is designed to be automatically updated and refreshed with production data.

- **Automatic Update on Merge**:
    - **Trigger**: Checks every minute for new commits on the `18.0` branch.
    - **Mechanism**: Systemd timer `odoo-auto-deploy.timer`/`service`.
    - **Script**: `/home/odoo/scripts/odoo-auto-deploy` which calls `deploy --restore origin/18.0`.
    - **Result**: The instance is always up-to-date with the latest `18.0` code.

- **Weekly Production Refresh**:
    - **Trigger**: Every Monday at 04:00.
    - **Mechanism**: Systemd timer `odoo-weekly-deploy.timer`/`service`.
    - **Script**: Calls `deploy -R origin/18.0`.
    - **Action**: Restores the latest production dump (neutralized) to the recette instance.

### Production Environment

Production updates are intentional and manual. They are controlled via git tags.

- **Tag Format**: `18.0-YYYYMMDD` (e.g., `18.0-20260110`).
- **Process**:
    1. Create and push a tag from your local machine:
       ```bash
       git tag 18.0-20260110
       git push origin 18.0-20260110
       ```
    2. Connect to the production server:
       ```bash
       ssh oca-france-prod
       ```
    3. Run the deployment script as the `odoo` user:
       ```bash
       sudo -u odoo /home/odoo/scripts/deploy 18.0-20260110
       ```

### Deployment Script Details

The `deploy` script (`templates/deploy.sh.j2`) performs the following steps:
1. **Fetch**: Fetches the latest code from origin.
2. **Reset**: Hard resets the repository to the specified `<git-reference>`.
3. **Stop**: Stops the `odoo-oca-france` service.
4. **Backup**: Creates a safety backup of the current database in `~/.odoo_dumps/before-deploy`.
5. **Restore (Optional)**: If `-R` or `--restore` is used, restores the latest production data from `~/.odoo_dumps/production-data/`.
6. **Start**: Starts the `odoo-oca-france` service.

# Deploy to EC2 (client_manager)

This document explains how to use the `scripts/deploy_to_ec2.sh` script to deploy the `client_manager` application to an EC2 instance and how to set up a `systemd` unit if needed.

Prerequisites (on the EC2 instance):

- An Ubuntu user (default: `ubuntu`) with your SSH key authorized.
- Git installed and configured: `sudo apt update && sudo apt install -y git`.
- Python 3.10+ and `python3-venv` installed: `sudo apt install -y python3 python3-venv python3-pip`.
- A systemd service unit named `xpages` (see `deploy/xpages.service` template below) or adjust `--service` to your service name.
- The remote user must be able to run `sudo systemctl restart xpages` (passwordless sudo for systemctl is helpful).

Basic usage

On your local machine (repo root):

```bash
./scripts/deploy_to_ec2.sh \
  --host 34.228.17.38 \
  --key ~/.ssh/xpages-key.pem \
  --user ubuntu \
  --repo git@github.com:rootkitoriginal/client_manager.git \
  --app-dir /home/ubuntu/client_manager \
  --branch main \
  --service xpages
```

What the script does

- SSH to the host and create the application directory (if missing).
- Clone the repo (or pull) and checkout the requested branch.
- Create or reuse a Python `venv` and install `requirements.txt`.
- Restart the `systemd` service and print its status.
- Tail the last 200 lines of `/var/log/cloud-init-output.log`.

If the service fails to start

- SSH manually and inspect logs:

```bash
ssh -i ~/.ssh/xpages-key.pem ubuntu@34.228.17.38
sudo journalctl -u xpages -b --no-pager | tail -n 200
sudo systemctl status xpages
sudo tail -n 200 /var/log/cloud-init-output.log
```

Systemd unit template

If you don't have a `systemd` service for the app, you can use the provided template `deploy/xpages.service` and copy it to `/etc/systemd/system/xpages.service` on the EC2 instance, then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable xpages
sudo systemctl start xpages
```

Security notes

- It's recommended to create a dedicated system user (e.g., `xpages`) to run the service. Adjust `User=` and `Group=` in the unit file accordingly.
- Don't hardcode secrets in the repo. Use environment variables or a secrets manager.

Further customization

- If you need to run database migrations, seed steps, or other build steps, add them to the `deploy_to_ec2.sh` script or create a separate remote hook script that the deploy script calls after pulling.


sudo nano /etc/systemd/system/xpages.service

# Cole o conteúdo acima, salve e saia

# Recarregue o systemd
sudo systemctl daemon-reload

# Reinicie o serviço
sudo systemctl restart xpages.service

# Verifique o status
sudo systemctl status xpages.service


[Unit]
Description=Client Manager Application
After=network.target
Wants=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/client_manager
ExecStart=/usr/bin/python3 run.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/home/ubuntu/client_manager

[Install]
WantedBy=multi-user.target
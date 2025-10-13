#!/usr/bin/env bash
set -euo pipefail

# Deploy script for EC2 instances running the client_manager app
# Usage:
#  ./scripts/deploy_to_ec2.sh \ 
#    --host 34.228.17.38 \ 
#    --key ~/.ssh/xpages-key.pem \ 
#    --user ubuntu \ 
#    --repo git@github.com:rootkitoriginal/client_manager.git \ 
#    --app-dir /home/ubuntu/client_manager \ 
#    --branch main \ 
#    --service xpages

print_usage() {
  sed -n '1,120p' <<'USAGE'
Usage: deploy_to_ec2.sh [options]

Options:
  --host HOST            Remote host or IP (required)
  --key KEY_PATH         SSH private key path (required)
  --user USER            SSH user (default: ubuntu)
  --repo REPO_URL        Git repo URL (default: origin remote)
  --app-dir APP_DIR      Remote application directory (default: /home/$USER/client_manager)
  --branch BRANCH        Git branch to deploy (default: main)
  --service SERVICE_NAME systemd service name to restart (default: xpages)
  --help                 Show this help
USAGE
}

# Default values
USER="ubuntu"
REPO=""
APP_DIR=""
BRANCH="main"
SERVICE_NAME="xpages"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host)
      HOST="$2"; shift 2;;
    --key)
      KEY="$2"; shift 2;;
    --user)
      USER="$2"; shift 2;;
    --repo)
      REPO="$2"; shift 2;;
    --app-dir)
      APP_DIR="$2"; shift 2;;
    --branch)
      BRANCH="$2"; shift 2;;
    --service)
      SERVICE_NAME="$2"; shift 2;;
    --help)
      print_usage; exit 0;;
    *)
      echo "Unknown option: $1"; print_usage; exit 1;;
  esac
done

# Validate required args
if [[ -z "${HOST:-}" || -z "${KEY:-}" ]]; then
  echo "Error: --host and --key are required"
  print_usage
  exit 2
fi

# Set sensible defaults
REPO_ARG="${REPO:-git@github.com:rootkitoriginal/client_manager.git}"
APP_DIR_ARG="${APP_DIR:-/home/${USER}/client_manager}"

SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

echo "Deploying to ${HOST} as ${USER}"

ssh -i "${KEY}" ${SSH_OPTS} "${USER}@${HOST}" bash -s <<EOF
set -euo pipefail

echo "Ensuring app directory exists: ${APP_DIR_ARG}"
if [ ! -d "${APP_DIR_ARG}" ]; then
  mkdir -p "${APP_DIR_ARG}"
  chown ${USER}:${USER} "${APP_DIR_ARG}"
fi

cd "${APP_DIR_ARG}"

if [ -d .git ]; then
  echo "Git repo exists — fetching and checking out ${BRANCH}"
  git fetch --all --prune
  git checkout ${BRANCH}
  git pull origin ${BRANCH}
else
  echo "Cloning ${REPO_ARG} into ${APP_DIR_ARG}"
  git clone --branch ${BRANCH} ${REPO_ARG} .
fi

echo "Setting up Python virtualenv"
if [ ! -d venv ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

echo "Restarting systemd service: ${SERVICE_NAME}"
sudo systemctl daemon-reload || true
sudo systemctl restart ${SERVICE_NAME}
sudo systemctl status ${SERVICE_NAME} --no-pager

echo "Tailing last 200 lines of cloud-init-output.log"
sudo tail -n 200 /var/log/cloud-init-output.log || true
EOF

echo "Deploy script finished. If the service failed to start, SSH into the host and run:\n  sudo journalctl -u ${SERVICE_NAME} -b --no-pager | tail -n 200"

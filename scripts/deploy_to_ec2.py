#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import sys
from pathlib import Path

def main():
    """
    Main function to handle argument parsing and deployment process.
    """
    parser = argparse.ArgumentParser(
        description="Deploy a Git repository to an EC2 instance.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("--host", required=True, help="Remote host or IP (required)")
    parser.add_argument("--key", required=True, type=Path, help="SSH private key path (required)")
    parser.add_argument("--user", default="ubuntu", help="SSH user (default: ubuntu)")
    parser.add_argument("--repo", default="git@github.com:xtdev2025/client_manager.git", help="Git repo URL (default: git@github.com:xtdev2025/client_manager.git)")
    parser.add_argument("--app-dir", help="Remote application directory (default: /home/<user>/client_manager)")
    parser.add_argument("--branch", default="main", help="Git branch to deploy (default: main)")
    parser.add_argument("--service", default="xpages", help="systemd service name to restart (default: xpages)")
    parser.add_argument("--token", help="Optional GitHub token for HTTPS authentication")

    args = parser.parse_args()

    # Expand user path for the SSH key
    key_path = args.key.expanduser().resolve()
    if not key_path.is_file():
        print(f"❌ Error: SSH key not found at {key_path}", file=sys.stderr)
        sys.exit(1)

    # Set sensible defaults that depend on other arguments
    app_dir = args.app_dir or f"/home/{args.user}/client_manager"
    
    if args.token:
        # If a token is provided, force HTTPS URL format
        repo_url = args.repo
        if repo_url.startswith("git@"):
            # Convert SSH URL to HTTPS
            repo_url = repo_url.replace("git@github.com:", "https://github.com/").replace(".git", "") + ".git"
        
        # Inject the token into the URL
        repo_url = repo_url.replace("https://", f"https://{args.token}@")
        
        # Remote script for HTTPS with token
        remote_script = f"""
set -euo pipefail
echo "🚀 --- Starting Deployment on {args.host} (using HTTPS with token) ---"
"""
    else:
        # Default to SSH URL if no token
        repo_url = args.repo
        if not repo_url.startswith("git@"):
            # Convert HTTPS URL to SSH
            repo_url = repo_url.replace("https://github.com/", "git@github.com:").replace(".git", "") + ".git"

        # Remote script for SSH
        remote_script = f"""
set -euo pipefail
echo "🚀 --- Starting Deployment on {args.host} (using SSH) ---"
echo "🔎 Ensuring GitHub is in known_hosts..."
mkdir -p ~/.ssh
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts
sort -u ~/.ssh/known_hosts -o ~/.ssh/known_hosts
"""

    # --- Remote Script (common part) ---
    remote_script += f"""
echo "Ensuring app directory exists: {app_dir}"
if [ ! -d "{app_dir}" ]; then
  echo "Creating directory {app_dir}..."
  sudo mkdir -p "{app_dir}"
  sudo chown {args.user}:{args.user} "{app_dir}"
fi

cd "{app_dir}"

if [ -d .git ]; then
  echo "✅ Git repo exists — fetching and checking out '{args.branch}'"
  # Add the repository directory to the list of safe directories
  git config --global --add safe.directory {app_dir}
  git fetch --all --prune
  git checkout {args.branch}
  git reset --hard origin/{args.branch}
  git pull origin {args.branch}
else
  echo "Cloning {repo_url} into {app_dir}"
  git clone --branch {args.branch} {repo_url} .
fi

echo "🐍 Setting up Python virtualenv..."
if [ ! -d venv ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
if [ -f requirements.txt ]; then
  echo "Installing dependencies from requirements.txt..."
  pip install -r requirements.txt
fi

echo "🔄 Restarting systemd service: {args.service}"
sudo systemctl daemon-reload || true
sudo systemctl restart {args.service}

echo "📊 Checking service status..."
sudo systemctl status {args.service} --no-pager

echo "📜 Tailing last 100 lines of cloud-init-output.log..."
sudo tail -n 100 /var/log/cloud-init-output.log || echo "Could not read cloud-init-output.log"

echo "🎉 --- Deployment script finished. ---"
"""

    ssh_command = [
        "ssh",
        "-i", str(key_path),
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        f"{args.user}@{args.host}",
        "bash -s"
    ]

    print(f"🛰️  Deploying to {args.host} as {args.user}...")

    try:
        # We pipe the output directly to the user's terminal
        process = subprocess.run(
            ssh_command,
            input=remote_script,
            text=True,
            check=True,
        )
        print("\n✅ Deploy successful!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Deploy failed with exit code {e.returncode}", file=sys.stderr)
        # stderr is already piped, so no need to print e.stderr
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ Error: 'ssh' command not found. Is OpenSSH client installed?", file=sys.stderr)
        sys.exit(1)
    finally:
        print(f"\n💡 If the service failed, SSH into the host and run:")
        print(f"  sudo journalctl -u {args.service} -b --no-pager | tail -n 200")


if __name__ == "__main__":
    main()

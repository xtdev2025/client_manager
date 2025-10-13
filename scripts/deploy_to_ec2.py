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
    
    # Process repository URL based on token presence
    if args.token:
        print("🔑 Using GitHub token for authentication")
        # If a token is provided, force HTTPS URL format
        repo_url = args.repo
        
        # Convert SSH URL to HTTPS if needed
        if repo_url.startswith("git@"):
            repo_url = repo_url.replace("git@github.com:", "https://github.com/")
            if not repo_url.endswith(".git"):
                repo_url += ".git"
        
        # Ensure it's HTTPS and inject token
        if repo_url.startswith("https://"):
            # Extract the part after https://
            repo_without_protocol = repo_url[8:]
            repo_url = f"https://{args.token}@{repo_without_protocol}"
        else:
            print(f"❌ Error: Unsupported repository URL format: {repo_url}", file=sys.stderr)
            sys.exit(1)
            
        print(f"🔒 Using authenticated repo URL: {repo_url.split('@')[0]}@***")

        # Remote script for HTTPS with token
        remote_script = f"""
set -euo pipefail
echo "🚀 --- Starting Deployment on {args.host} (using HTTPS with token) ---"
"""
    else:
        # Default to SSH URL if no token
        repo_url = args.repo
        if repo_url.startswith("https://"):
            # Convert HTTPS URL to SSH
            repo_url = repo_url.replace("https://github.com/", "git@github.com:")
            if not repo_url.endswith(".git"):
                repo_url += ".git"

        print(f"🔑 Using SSH authentication for repository")
        
        # Remote script for SSH
        remote_script = f"""
set -euo pipefail
echo "🚀 --- Starting Deployment on {args.host} (using SSH) ---"
echo "🔎 Ensuring GitHub is in known_hosts..."
mkdir -p ~/.ssh
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts 2>/dev/null
ssh-keyscan -t ecdsa github.com >> ~/.ssh/known_hosts 2>/dev/null
ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts 2>/dev/null
sort -u ~/.ssh/known_hosts -o ~/.ssh/known_hosts
chmod 600 ~/.ssh/known_hosts
"""

    # --- Remote Script (common part) ---
    remote_script += f"""
echo "📁 Ensuring app directory exists: {app_dir}"
sudo mkdir -p "{app_dir}"
sudo chown {args.user}:{args.user} "{app_dir}"

cd "{app_dir}"

# Configure git safe directory
git config --global --add safe.directory "{app_dir}" || true

if [ -d .git ]; then
  echo "✅ Git repo exists — fetching and checking out '{args.branch}'"
  # Check if we need to switch remote URL (if token changed)
  CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
  EXPECTED_REMOTE="{repo_url}"
  if [ "$CURRENT_REMOTE" != "$EXPECTED_REMOTE" ]; then
    echo "🔄 Updating remote URL from origin"
    git remote set-url origin "$EXPECTED_REMOTE" || git remote add origin "$EXPECTED_REMOTE"
  fi
  
  git fetch --all --prune
  git checkout {args.branch} 2>/dev/null || git checkout -b {args.branch} --track origin/{args.branch}
  git reset --hard origin/{args.branch}
  echo "🔄 Pulling latest changes..."
  git pull origin {args.branch}
else
  echo "🔨 Cloning repository into {app_dir}"
  # Remove any existing files in case of failed previous clone
  sudo rm -rf "{app_dir}"/*
  sudo rm -rf "{app_dir}"/.* 2>/dev/null || true
  
  # Clone the repository
  if git clone --branch {args.branch} "{repo_url}" .; then
    echo "✅ Repository cloned successfully"
  else
    echo "❌ Failed to clone repository"
    echo "💡 Troubleshooting tips:"
    echo "   - Check if the token has repository access"
    echo "   - Verify the repository URL: {repo_url.split('@')[0] + '@***' if args.token else repo_url}"
    echo "   - Check network connectivity to GitHub"
    exit 1
  fi
fi

echo "🐍 Setting up Python virtualenv..."
if [ ! -d venv ]; then
  python3 -m venv venv
  echo "✅ Virtual environment created"
fi

source venv/bin/activate

echo "📦 Upgrading pip and installing dependencies..."
pip install --upgrade pip

if [ -f requirements.txt ]; then
  echo "📋 Installing dependencies from requirements.txt..."
  pip install -r requirements.txt
  echo "✅ Dependencies installed"
else
  echo "⚠️  No requirements.txt found"
fi

echo "🔄 Restarting systemd service: {args.service}"
sudo systemctl daemon-reload 2>/dev/null || true

# Stop service gracefully
echo "⏹️  Stopping service..."
sudo systemctl stop {args.service} 2>/dev/null || true

# Wait a moment
sleep 2

echo "▶️  Starting service..."
sudo systemctl start {args.service}

echo "📊 Checking service status..."
if sudo systemctl is-active --quiet {args.service}; then
  echo "✅ Service {args.service} is running"
  sudo systemctl status {args.service} --no-pager -l
else
  echo "❌ Service {args.service} failed to start"
  sudo systemctl status {args.service} --no-pager -l
  exit 1
fi

echo "📜 Checking application logs..."
# Try to get recent journal logs for the service
sudo journalctl -u {args.service} -n 50 --no-pager 2>/dev/null || echo "Could not retrieve journal logs"

echo "🎉 --- Deployment finished successfully! ---"
"""

    ssh_command = [
        "ssh",
        "-i", str(key_path),
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=30",
        f"{args.user}@{args.host}",
        "bash -s"
    ]

    print(f"🛰️  Deploying to {args.host} as {args.user}...")
    print(f"📦 Repository: {args.repo}")
    print(f"🌿 Branch: {args.branch}")
    print(f"📁 App directory: {app_dir}")
    print(f"⚙️  Service: {args.service}")

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
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ Error: 'ssh' command not found. Is OpenSSH client installed?", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
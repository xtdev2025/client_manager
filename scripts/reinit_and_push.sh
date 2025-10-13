#!/usr/bin/env bash
set -euo pipefail

# reinit_and_push.sh
# Safely reinitialize git history and push the project to a new remote as a "fresh" repository.
# Two methods available:
#  - orphan: create an orphan branch, commit all files, force-push to the target branch, delete temporary branch
#  - fresh : remove .git, git init, commit and push (simpler, destructive)

print_usage() {
  cat <<'USAGE'
Usage: reinit_and_push.sh --new-url <git-url> [options]

Options:
  --new-url URL      (required) new remote repository URL, e.g. git@github.com:youruser/newrepo.git
  --branch BRANCH    target branch name on remote (default: main)
  --method METHOD    'orphan' (default) or 'fresh'
  --remote REMOTE    remote name to set (default: origin)
  --yes              skip confirmation prompts (dangerous)
  --help             show this help

Examples:
  # Create an orphan branch and force-push it to new remote's 'main'
  ./scripts/reinit_and_push.sh --new-url git@github.com:you/newrepo.git --branch main

  # Remove .git and reinit then push
  ./scripts/reinit_and_push.sh --new-url git@github.com:you/newrepo.git --method fresh --yes
USAGE
}

NEW_URL=""
BRANCH="main"
METHOD="orphan"
REMOTE="origin"
ASSUME_YES=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --new-url)
      NEW_URL="$2"; shift 2;;
    --branch)
      BRANCH="$2"; shift 2;;
    --method)
      METHOD="$2"; shift 2;;
    --remote)
      REMOTE="$2"; shift 2;;
    --yes)
      ASSUME_YES=1; shift 1;;
    --help)
      print_usage; exit 0;;
    *)
      echo "Unknown arg: $1"; print_usage; exit 1;;
  esac
done

if [[ -z "$NEW_URL" ]]; then
  echo "Error: --new-url is required"
  print_usage
  exit 2
fi

if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is required" >&2
  exit 3
fi

echo "This operation is destructive to git history."
echo "Method: ${METHOD}. Target remote: ${REMOTE} -> ${NEW_URL}. Branch: ${BRANCH}"

if [[ $ASSUME_YES -ne 1 ]]; then
  read -p "Are you sure you want to proceed? Type 'YES' to continue: " CONFIRM
  if [[ "$CONFIRM" != "YES" ]]; then
    echo "Aborted by user. No changes made."; exit 4
  fi
fi

PWD_ROOT=$(pwd)
echo "Working in ${PWD_ROOT}"

if [[ "$METHOD" == "orphan" ]]; then
  TMP_BRANCH="reinit_temp_$(date +%s)"
  echo "Creating orphan branch: ${TMP_BRANCH}"
  git checkout --orphan "${TMP_BRANCH}"
  # Remove all tracked files from index (keeps work tree)
  git reset --hard
  # Add everything and create a fresh commit
  git add --all
  git commit -m "Initial commit"

  echo "Removing existing remote '${REMOTE}' (if exists) and adding new remote"
  git remote remove "${REMOTE}" 2>/dev/null || true
  git remote add "${REMOTE}" "${NEW_URL}"

  echo "Force-pushing ${TMP_BRANCH} to ${REMOTE}/${BRANCH}"
  git push -u "${REMOTE}" "${TMP_BRANCH}:${BRANCH}" --force

  echo "Deleting temporary branch locally: ${TMP_BRANCH}"
  git checkout --detach
  git branch -D "${TMP_BRANCH}"

  echo "Finished. Repository history has been replaced on ${REMOTE}/${BRANCH}."

elif [[ "$METHOD" == "fresh" ]]; then
  echo "Removing .git directory (DESCTRUCTIVE)"
  rm -rf .git
  git init
  git add --all
  git commit -m "Initial commit"
  git remote add "${REMOTE}" "${NEW_URL}"
  git branch -M "${BRANCH}"
  git push -u "${REMOTE}" "${BRANCH}" --force
  echo "Finished fresh reinit and push to ${REMOTE}/${BRANCH}."
else
  echo "Unknown method: ${METHOD}"; exit 5
fi

echo "Recommended: verify the remote repository now (on GitHub/GitLab) and remove any webhooks/CI settings if necessary."

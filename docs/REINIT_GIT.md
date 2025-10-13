# Reinitialize Git history and push as a new repository

This guide explains how to remove the existing git history and push a fresh repository to a new remote. Use extreme caution — this operation rewrites history and will make previous commits unreachable from the new remote.

Safety checklist

- Make a local backup (copy the project directory) before running any destructive command.
- Confirm you have the correct `--new-url` (target repository) and that it's empty or you intend to overwrite it.
- Consider using the `orphan` method first (safer) before using `fresh` which removes `.git` entirely.

Script: `scripts/reinit_and_push.sh`

Examples

- Orphan branch (recommended):

```bash
./scripts/reinit_and_push.sh --new-url git@github.com:youruser/newrepo.git --branch main
```

- Fresh reinit (very destructive):

```bash
./scripts/reinit_and_push.sh --new-url git@github.com:youruser/newrepo.git --method fresh --yes
```

Afterwards

- Check the remote repository on GitHub/GitLab to ensure the new commit is present.
- Remove any secrets, tokens or credentials from the repository before pushing (search for `.env` and credentials in code).
- Update CI/CD or webhooks on the remote if needed.

If you'd like, I can:

- Scan the repository for common secrets and sensitive files to remove before reinit.
- Create a small .gitignore template and ensure `.env` or keys are excluded.
- Run the reinit steps for you (I will not run destructive operations without your explicit confirmation and the exact `--new-url`).

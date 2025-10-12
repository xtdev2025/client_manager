#!/bin/bash

# This is a sample Gemini pre-commit hook.
# You can find more information about hooks here:
# https://docs.gemini.com/cli/hooks

# Run the linter.
if ! flake8 .; then
    echo "❌ Linting failed. Please fix the issues before committing."
    exit 1
fi

# Run the tests.
if ! pytest; then
    echo "❌ Tests failed. Please fix the failing tests before committing."
    exit 1
fi

echo "✅ All checks passed. Proceeding with commit."

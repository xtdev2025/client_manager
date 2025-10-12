#!/bin/bash

# This is a sample Gemini pre-commit hook.
# You can find more information about hooks here:
# https://docs.gemini.com/cli/hooks

# Run the linter.
flake8 .

# Run the tests.
pytest

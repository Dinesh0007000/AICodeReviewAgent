#!/bin/bash
set -e  # Exit on any error
echo "Installing Java..."
apt-get update && apt-get install -y openjdk-11-jre
echo "Installing ESLint..."
npm install eslint
echo "Creating ESLint config..."
echo '{"env": {"es2021": true, "node": true}, "extends": "eslint:recommended", "rules": {"semi": ["error", "always"], "no-unused-vars": "error"}}' > .eslintrc.json

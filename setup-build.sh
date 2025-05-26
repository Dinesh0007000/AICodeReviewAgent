#!/bin/bash
set -e  # Exit on any error
apt-get update || { echo "Failed to update apt-get"; exit 1; }
apt-get install -y openjdk-11-jre || { echo "Failed to install OpenJDK"; exit 1; }
npm run install-eslint || { echo "Failed to install ESLint"; exit 1; }
echo '{"env": {"es2021": true, "node": true}, "extends": "eslint:recommended", "rules": {"semi": ["error", "always"], "no-unused-vars": "error"}}' > .eslintrc.json || { echo "Failed to create .eslintrc.json"; exit 1; }

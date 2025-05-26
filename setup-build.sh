#!/bin/bash
apt-get update
apt-get install -y openjdk-11-jre
npm run install-eslint
wget -O checkstyle.jar https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.3.1/checkstyle-10.3.1-all.jar
wget -O sun_checks.xml https://raw.githubusercontent.com/checkstyle/checkstyle/master/src/main/resources/sun_checks.xml
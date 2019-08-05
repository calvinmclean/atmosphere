#!/bin/bash

# Set so that if any command fails, the script will exit and fail
set -e

# Setup Atmosphere environment
cd /opt/dev/atmosphere
source /opt/env/atmosphere/bin/activate

# Install pre-dependencies
apt-get update && apt-get install -y postgresql
pip install -U pip==9.0.3 setuptools
pip install pip-tools==1.11.0
sed -i "s/^bind 127.0.0.1 ::1$/bind 127.0.0.1/" /etc/redis/redis.conf
service redis-server start

# Wait for DB to be active
echo "Waiting for postgres..."
while ! nc -z localhost 5432; do sleep 5; done

# Configure password for connecting to postgres
echo "localhost:5432:postgres:atmosphere_db_user:atmosphere_db_pass" > ~/.pgpass
chmod 600 ~/.pgpass

function run_tests_for_distribution() {
  echo "----- RUNNING TESTS FOR $1 -----"
  psql -c "CREATE DATABASE atmosphere_db WITH OWNER atmosphere_db_user;" -h localhost -U atmosphere_db_user -d postgres
  ./travis/check_properly_generated_requirements.sh
  pip uninstall -y backports.ssl-match-hostname
  pip-sync requirements.txt
  cp ./variables.ini.dist ./variables.ini
  ./configure
  python manage.py check
  python manage.py makemigrations --dry-run --check
  patch variables.ini variables_for_testing_$1.ini.patch
  ./configure
  pip-sync dev_requirements.txt
  ./travis/check_for_dead_code_with_vulture.sh
  yapf --diff -p -- $(git ls-files | grep '\.py$')
  prospector --profile prospector_profile.yaml --messages-only -- $(git ls-files | grep '\.py$')
  coverage run manage.py test --keepdb --noinput --settings=atmosphere.settings
  coverage run --append manage.py behave --keepdb --tags ~@skip-if-$1 --settings=atmosphere.settings --format rerun --outfile rerun_failing.features
  if [ -f 'rerun_failing.features' ]; then python manage.py behave --logging-level DEBUG --capture-stderr --capture --verbosity 3 --keepdb @rerun_failing.features; fi
  python manage.py makemigrations --dry-run --check
}

run_tests_for_distribution cyverse
psql -c "DROP DATABASE atmosphere_db" -h localhost -U atmosphere_db_user -d postgres
psql -c "DROP DATABASE test_atmosphere_db" -h localhost -U atmosphere_db_user -d postgres
run_tests_for_distribution jetstream

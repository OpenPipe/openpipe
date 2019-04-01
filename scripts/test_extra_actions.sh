#/!bin/sh
set -eu

python -m openpipe.cli install-action-lib -ua jinja
python -m openpipe.cli test transform using jinja

python -m openpipe.cli install-action-lib -ua ckan
python -m openpipe.cli test read from ckan

python -m openpipe.cli install-action-lib -ua influxdb
python -m openpipe.cli help write to influxdb

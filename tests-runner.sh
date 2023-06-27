#!/usr/bin/env bash
cd /builds/python-portfolio/retail-portal/
pip install --upgrade pip
pip install tox 'virtualenv>20.0.0'
if [[ -z "${REMOVE_TOX_CACHE}" ]]; then
  echo "Using cached tox folder";
  tox
else
  echo "Recreating tox folder"
  tox -r
fi
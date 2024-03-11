#!/bin/bash
# basic reference for writing script for travis

set -ev

poetry export --without-hashes -f requirements.txt -o requirements.txt
poetry export --without-hashes --with dev -f requirements.txt -o requirements-test.txt

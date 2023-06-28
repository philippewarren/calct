#!/usr/bin/env bash

echo "########################## black ##########################"
python -m black --check calct tests
echo "########################## isort ##########################"
python -m isort --check-only calct tests
echo "########################## pyright ########################"
python -m pyright calct tests
echo "########################## mypy ###########################"
python -m mypy -p calct -p tests
echo "########################## flake8 #########################"
python -m flake8 calct tests
echo "########################## pylint #########################"
python -m pylint calct tests

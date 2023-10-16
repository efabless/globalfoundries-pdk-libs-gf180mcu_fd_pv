# Copyright 2022 GlobalFoundries PDK Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# The top directory where environment will be created.
TOP_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))

# A pip `requirements.txt` file.
# https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format
REQUIREMENTS_FILE := requirements.txt

# https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
ENVIRONMENT_FILE := pdk_regression.yml

# Path to regression
KLAYOUT_DRC_TESTS := klayout/drc/testing/

KLAYOUT_LVS_TESTS := klayout/lvs/testing/


include third_party/make-env/conda.mk

# Lint python code
lint_python: | $(CONDA_ENV_PYTHON)
	@$(IN_CONDA_ENV) flake8 .

# Lint ruby code
lint_ruby:| $(CONDA_ENV_PYTHON)
	@$(IN_CONDA_ENV) gem install rubocop
	@ln -s $$CONDA_PREFIX/bin/ruby $$CONDA_PREFIX/share/rubygems/bin/ruby
	@$(IN_CONDA_ENV) rubocop .

################################################################################
## DRC Regression section
################################################################################
#=================================
# ----- test-DRC_regression ------
#=================================
.ONESHELL:
test-DRC-main : | $(CONDA_ENV_PYTHON) 
	@$(IN_CONDA_ENV) python3 $(KLAYOUT_DRC_TESTS)/run_regression.py

.ONESHELL:
test-DRC-% : | $(CONDA_ENV_PYTHON)
	@which python3
	@$(IN_CONDA_ENV) python3 $(KLAYOUT_DRC_TESTS)/run_regression.py --table=$*

#=================================
# -------- test-DRC-switch -------
#=================================
# LVS main testing
test-DRC-switch: | $(CONDA_ENV_PYTHON)
	@$(IN_CONDA_ENV) klayout -v

################################################################################
## LVS Regression section
################################################################################
#=================================
# ----- test-LVS_regression ------
#=================================
.ONESHELL:
test-LVS-main: | $(CONDA_ENV_PYTHON)
	@$(IN_CONDA_ENV) cd $(KLAYOUT_LVS_TESTS) && make test-LVS-main

.ONESHELL:
test-LVS-% : | $(CONDA_ENV_PYTHON)
	@$(IN_CONDA_ENV) cd $(KLAYOUT_LVS_TESTS) && make test-LVS-$*

#=================================
# -------- test-LVS-switch -------
#=================================
test-LVS-switch: | $(CONDA_ENV_PYTHON)
	@$(IN_CONDA_ENV) cd $(KLAYOUT_LVS_TESTS) && make test-LVS-switch

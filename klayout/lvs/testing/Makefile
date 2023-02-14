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

#=========================================================================
# ---------------------------------- LVS ---------------------------------
#=========================================================================

SHELL        := /bin/bash
Testing_DIR  ?= $(shell pwd)

.DEFAULT_GOAL := all

all: test-LVS

test-LVS: Add_run-dir  test-LVS-switch  test-LVS-main

#=================================
# ----- test-LVS_regression ------
#=================================

.ONESHELL:
test-LVS-main: test-LVS-MOS  test-LVS-BJT  test-LVS-DIODE  test-LVS-RES  test-LVS-MIMCAP  test-LVS-MOSCAP  test-LVS-MOS_SAB

.ONESHELL:
test-LVS-%:
	@ python3 run_regression.py --device=$*

#=================================
# -------- test-LVS-switch -------
#=================================

.ONESHELL:
test-LVS-switch:
	@cd $(Testing_DIR)
	@cd ..
	@echo "========== LVS-Switch testing =========="
	@python3 run_lvs.py --design=testing/extraction_checking/sample_nfet_03v3.gds --net=sample_nfet_03v3.spice --gf180mcu=A 
	@python3 run_lvs.py --design=testing/extraction_checking/sample_nfet_03v3.gds --net=sample_nfet_03v3.spice --gf180mcu=B
	@python3 run_lvs.py --design=testing/extraction_checking/sample_nfet_03v3.gds --net=sample_nfet_03v3.spice --gf180mcu=C

#==========================
# --------- HELP ----------
#==========================

# Help Target
help:
	@echo "\n ==== The following are some of the valid targets for this Makefile ====\n"
	@echo "... all                  	(the default if no target is provided          )"
	@echo "... Add_run-dir          	(Create output directory of all runs           )"
	@echo "... test-LVS             	(To run LVS full regression                    )"
	@echo "... test-LVS-switch      	(To run switch checking regression             )"
	@echo "... test-LVS-gf180mcu_fd_sc	(To run standard cells LVS regression          )"
	@echo "... test-LVS-main        	(To run main LVS regression for all devices    )"
	@echo "... test-LVS_MOS         	(To run main LVS regression for MOS devices    )"
	@echo "... test-LVS_BJT         	(To run main LVS regression for BJT devices    )"
	@echo "... test-LVS_DIODE       	(To run main LVS regression for diode devices  )"
	@echo "... test-LVS_RES         	(To run main LVS regression for diode devices  )"
	@echo "... test-LVS_MIMCAP      	(To run main LVS regression for diode devices  )"
	@echo "... test-LVS_MOSCAP      	(To run main LVS regression for diode devices  )"
	@echo "... test-LVS_MOS-SAB     	(To run main LVS regression for SAB MOS devices)"

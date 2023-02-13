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

"""Run GlobalFoundries 180nm MCU LVS Regression.

Usage:
    run_regression.py (--help| -h)
    run_regression.py (--device=<device_name>) [--mp=<num>] [--run_name=<run_name>]

Options:
    --help -h                 Print this help message.
    --device=<device_name>    Name of device that we want to run regression for, Allowed values (MOS, BJT, DIODE, RES, MIMCAP, MOSCAP, MOS_SAB).
    --mp=<num>                The number of threads used in run.
    --run_name=<run_name>     Select your run name.
"""

from datetime import datetime
from docopt import docopt
import os
import logging
from subprocess import check_call
import glob


def check_klayout_version():
    """
    check_klayout_version checks klayout version and makes sure it would work with the DRC.
    """
    # ======= Checking Klayout version =======
    klayout_v_ = os.popen("klayout -b -v").read()
    klayout_v_ = klayout_v_.split("\n")[0]
    klayout_v_list = []

    if klayout_v_ == "":
        logging.error("Klayout is not found. Please make sure klayout is installed.")
        exit(1)
    else:
        klayout_v_list = [int(v) for v in klayout_v_.split(" ")[-1].split(".")]

    logging.info(f"Your Klayout version is: {klayout_v_}")

    if len(klayout_v_list) < 1 or len(klayout_v_list) > 3:
        logging.error("Was not able to get klayout version properly.")
        exit(1)
    elif len(klayout_v_list) >= 2 or len(klayout_v_list) <= 3:
        if klayout_v_list[1] < 28:
            logging.error("Prerequisites at a minimum: KLayout 0.28.0")
            logging.error(
                "Using this klayout version has not been assesed in this development. Limits are unknown"
            )
            exit(1)


def lvs_check(output_path, table, devices):

    # counters
    pass_count = 0
    fail_count = 0

    # Generate databases
    for device in devices:
        layout = device[0]

        # Get switches
        if layout == "sample_ggnfet_06v0_dss":
            switches = " -rd lvs_sub=sub!"
        else:
            switches = " -rd lvs_sub=vdd!"

        if len(device) > 1:
            switches = device[1] + switches

        # Check if device is mosfet or esd
        if "sample" in layout:
            net = f"{layout}.src"
        else:
            net = layout

        if os.path.exists(f"testcases/{layout}.gds") and os.path.exists(f"testcases/{net}.cdl"):
            layout_path = f"testcases/{layout}.gds"
            netlist_path = f"testcases/{net}.cdl"
        elif os.path.exists(f"man_testcases/{layout}.gds") and os.path.exists(f"man_testcases/{net}.cdl"):
            layout_path = f"man_testcases/{layout}.gds"
            netlist_path = f"man_testcases/{net}.cdl"
        else:
            logging.error(f"{net} testcase is not exist, please recheck")
            exit(1)

        # Get netlist without $ and ][
        with open(netlist_path, "r") as file:
            spice_netlist = file.read()

        # Replace the target string
        spice_netlist = spice_netlist.replace("$SUB=", "")
        spice_netlist = spice_netlist.replace("$", "")
        spice_netlist = spice_netlist.replace("[", "")
        spice_netlist = spice_netlist.replace("]", "")

        # Cloning run files into run dir
        device_dir = table.split(" ")[0]
        os.makedirs(f"{output_path}/LVS_{device_dir}", exist_ok=True)
        check_call(
            f"cp -f {layout_path} {netlist_path} {output_path}/LVS_{device_dir}/",
            shell=True,
        )

        # Write clean netlist in run folder
        final_layout = f"{output_path}/LVS_{device_dir}/{layout}.gds"
        final_netlist = f"{output_path}/LVS_{device_dir}/{net}_generated.cdl"
        pattern_log = f"{output_path}/LVS_{device_dir}/{layout}.log"

        with open(final_netlist, "w") as file:
            file.write(spice_netlist)

        # command to run drc
        call_str = f"klayout -b -r ../gf180mcu.lvs -rd input={final_layout} -rd report={layout}.lvsdb -rd schematic={layout}_generated.cdl -rd target_netlist={layout}_extracted.cir {switches} > {pattern_log} 2>&1"

    # Starting klayout run
        try:
            check_call(call_str, shell=True)
        except Exception as e:
            logging.error("%s generated an exception: %s" % (final_layout, e))
            raise

        if os.path.exists(pattern_log):
            with open(pattern_log) as result_file:
                result = result_file.read()
            if "Congratulations! Netlists match" in result:
                logging.info(f"{layout} testcase passed")
                pass_count += 1
            else:
                fail_count += 1
                logging.error(f"{layout} testcase failed.")
                logging.error(f"Please recheck {layout_path} file.")
                exit(1)
        else:
            logging.error("Klayout LVS run failed")
            exit(1)

    logging.info("==================================")
    logging.info(f"NO. OF PASSED {table} : {pass_count}")
    logging.info(f"NO. OF FAILED {table} : {fail_count}")
    logging.info("==================================\n")

    if fail_count > 0:
        return False
    else:
        return True


def main(output_path, device):
    """
    Main Procedure.

    This function is the main execution procedure

    Parameters
    ----------
    output_path : str
        Path string to the location of the output results of the run.
    device : str or None
        Name of device that we want to run regression for.
    Returns
    -------
    bool
        If all regression passed, it returns true. If any of the rules failed it returns false.
    """

    ## Check Klayout version
    check_klayout_version()

    # MOSFET devices
    mos_devices = [
        ["sample_pfet_06v0_dn"],
        ["sample_nfet_10v0_asym"],
        ["sample_nfet_03v3"],
        ["sample_pfet_05v0_dn"],
        ["sample_pfet_06v0"],
        ["sample_nfet_05v0"],
        ["sample_nfet_06v0"],
        ["sample_nfet_06v0_dn"],
        ["sample_pfet_10v0_asym"],
        ["sample_nfet_05v0_dn"],
        ["sample_pfet_05v0"],
        ["sample_pfet_03v3"],
        ["sample_nfet_06v0_nvt"],
    ]

    # BJT
    bjt_devices = [
        ["npn_10p00x10p00"],
        ["npn_05p00x05p00"],
        ["npn_00p54x16p00"],
        ["npn_00p54x08p00"],
        ["npn_00p54x04p00"],
        ["npn_00p54x02p00"],
        ["pnp_10p00x10p00"],
        ["pnp_05p00x05p00"],
        ["pnp_10p00x00p42"],
        ["pnp_05p00x00p42"],
    ]

    # Diode
    diode_devices = [
        ["diode_nd2ps_03v3"],
        ["diode_nd2ps_03v3_dn"],
        ["diode_nd2ps_06v0"],
        ["diode_nd2ps_06v0_dn"],
        ["diode_pd2nw_03v3"],
        ["diode_pd2nw_03v3_dn"],
        ["diode_pd2nw_06v0"],
        ["diode_pd2nw_06v0_dn"],
        ["diode_nw2ps_03v3"],
        ["diode_nw2ps_06v0"],
        ["diode_pw2dw_03v3"],
        ["diode_pw2dw_06v0"],
        ["diode_dw2ps_03v3"],
        ["diode_dw2ps_06v0"],
        ["sc_diode"],
    ]

    # Resistor
    res_devices = [
        ["pplus_u"],
        ["nplus_s"],
        ["pplus_u_dw"],
        ["nplus_s_dw"],
        ["pplus_s"],
        ["pplus_s_dw"],
        ["nplus_u_dw"],
        ["nplus_u"],
        ["nwell"],
        ["pwell"],
        ["ppolyf_s"],
        ["ppolyf_u_3k", "-rd poly_res=3k"],
        ["ppolyf_s_dw"],
        ["ppolyf_u_1k", "-rd poly_res=1k"],
        ["ppolyf_u_3k_6p0_dw", "-rd poly_res=3k"],
        ["npolyf_u_dw"],
        ["ppolyf_u_3k_dw", "-rd poly_res=3k"],
        ["ppolyf_u_3k_6p0", "-rd poly_res=3k"],
        ["npolyf_s"],
        ["ppolyf_u_1k_6p0_dw", "-rd poly_res=1k"],
        ["ppolyf_u"],
        ["npolyf_u"],
        ["ppolyf_u_2k_dw", "-rd poly_res=2k"],
        ["npolyf_s_dw"],
        ["ppolyf_u_2k_6p0_dw", "-rd poly_res=2k"],
        ["ppolyf_u_2k_6p0", "-rd poly_res=2k"],
        ["ppolyf_u_dw"],
        ["ppolyf_u_1k_6p0", "-rd poly_res=1k"],
        ["ppolyf_u_2k", "-rd poly_res=2k"],
        ["ppolyf_u_1k_dw", "-rd poly_res=1k"],
        ["rm1"],
        ["rm2"],
        ["rm3"],
        ["tm6k", "-rd metal_top=6K"],
        ["tm9k", "-rd metal_top=9K"],
        ["tm30k", "-rd metal_top=30K"],
        ["tm11k", "-rd metal_top=11K"],
    ]

    # MIM Capacitor
    mimcap_devices = [
        ["cap_mim_1f0_m2m3_noshield", "-rd mim_option=A -rd mim_cap=1"],
        ["cap_mim_1f5_m2m3_noshield", "-rd mim_option=A -rd mim_cap=1.5"],
        ["cap_mim_2f0_m2m3_noshield", "-rd mim_option=A -rd mim_cap=2"],
        ["cap_mim_1f0_m3m4_noshield", "-rd mim_option=B -rd mim_cap=1"],
        ["cap_mim_1f5_m3m4_noshield", "-rd mim_option=B -rd mim_cap=1.5"],
        ["cap_mim_2f0_m3m4_noshield", "-rd mim_option=B -rd mim_cap=2"],
        ["cap_mim_1f0_m4m5_noshield", "-rd mim_option=B -rd mim_cap=1"],
        ["cap_mim_1f5_m4m5_noshield", "-rd mim_option=B -rd mim_cap=1.5"],
        ["cap_mim_2f0_m4m5_noshield", "-rd mim_option=B -rd mim_cap=2"],
        ["cap_mim_1f0_m5m6_noshield", "-rd mim_option=B -rd mim_cap=1"],
        ["cap_mim_1f5_m5m6_noshield", "-rd mim_option=B -rd mim_cap=1.5"],
        ["cap_mim_2f0_m5m6_noshield", "-rd mim_option=B -rd mim_cap=2"]
    ]

    # MOS Capacitor
    moscap_devices = [
        ["cap_pmos_03v3_b"],
        ["cap_nmos_03v3_b"],
        ["cap_nmos_03v3"],
        ["cap_nmos_06v0_b"],
        ["cap_pmos_06v0_dn"],
        ["cap_nmos_06v0"],
        ["cap_pmos_03v3_dn"],
        ["cap_pmos_06v0"],
        ["cap_nmos_03v3_dn"],
        ["cap_pmos_06v0_b"],
        ["cap_pmos_03v3"],
        ["cap_nmos_06v0_dn"],
    ]

    # ESD (SAB MOSFET)
    mos_sab_devices = [
        ["sample_pfet_05v0_dss"],
        ["sample_nfet_05v0_dss"],
        ["sample_pfet_03v3_dn_dss"],
        ["sample_pfet_03v3_dss"],
        ["sample_pfet_05v0_dn_dss"],
        ["sample_nfet_06v0_dss"],
        ["sample_pfet_06v0_dn_dss"],
        ["sample_nfet_06v0_dn_dss"],
        ["sample_nfet_03v3_dn_dss"],
        ["sample_nfet_05v0_dn_dss"],
        ["sample_nfet_03v3_dss"],
        ["sample_pfet_06v0_dss"],
    ]

    # eFuse
    efuse_devices = [["efuse"]]

    all_devices = {"MOS": mos_devices, "BJT": bjt_devices, "DIODE": diode_devices,
                   "RES": res_devices, "MIMCAP": mimcap_devices, "MOSCAP": moscap_devices,
                   "MOS_SAB": mos_sab_devices, "EFUSE": efuse_devices}

    # Starting LVS regression
    run_status = False

    if device in all_devices :
        logging.info(f"Running Global Foundries 180nm MCU LVS regression on {device}")
        run_status = lvs_check(output_path, f"{device} DEVICES", all_devices[device])
    else:
        logging.error("Allowed devices are (MOS, BJT, DIODE, RES, MIMCAP, MOSCAP, MOS_SAB) only")
        exit(1)

    if run_status:
        logging.info("LVS regression test completed successfully.")
    else:
        logging.error("LVS regression test failed.")
        exit(1)


if __name__ == "__main__":

    # docopt reader
    args = docopt(__doc__, version="LVS Regression: 0.2")

    # arguments
    run_name = args["--run_name"]
    device = args["--device"]

    if run_name is None:
        # logs format
        run_name = datetime.utcnow().strftime("unit_tests_%Y_%m_%d_%H_%M_%S")

    # Paths of regression dirs
    testing_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(testing_dir, run_name)

    # Creating output dir
    os.makedirs(output_path, exist_ok=True)

    # logs format
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler(os.path.join(output_path, "{}.log".format(run_name))),
            logging.StreamHandler(),
        ],
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    # Calling main function
    run_status = main(output_path, device)

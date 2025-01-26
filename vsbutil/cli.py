import argparse
from pathlib import Path
import sys

from ._vsbutil import VerySeriousButton, MODKEYS, KEYCODES
from .__init__ import __version__


def parse_hex(x):
    return int(x.strip().split("0x", 1)[-1], base=16)


def handle_cmdline_args(argv):
    ap = argparse.ArgumentParser(
        prog=argv[0], description="Very Serious Button service tool")
    ap.add_argument(
        "--serial",
        default=None,
        help="serial number of VSB unit to connect to"
        )
    ap.add_argument(
        "--version", action="store_true", help="print version of this software"
        )
    subparser = ap.add_subparsers(dest="cmd")
    subparser.add_parser("list", help="list serial numbers of attached VSBs")
    subparser.add_parser("getserial", help="get VSB serial number")
    subparser.add_parser("getdevinfo", help="get VSB device info")
    subparser.add_parser("getconfig", help="get VSB device configuration")
    subparser.add_parser(
        "wipeconfig",
        help="initialize stored configuration to factory defaults"
        )
    subparser.add_parser(
        "saveconfig", help="store current configuration to EEPROM")
    subparser.add_parser(
        "loadconfig", help="read stored configuration from EEPROM")
    subparser.add_parser("getfuckyou", help="retrieve a fuckyou")
    setjoy = subparser.add_parser("setjoy", help="set VSB to gamepad mode")
    setkey = subparser.add_parser(
        "setkey", help="set VSB to single keyboard key mode")
    setkey.add_argument(
        "keygroup",
        metavar="KEYS",
        help="plus-separated group of key names, e.g. 'LALT+LSHIFT+F'"
        )
    setkeys = subparser.add_parser(
        "setkeyseq", help="set VSB to keyboard sequence mode")
    setkeys.add_argument(
        "keygroups",
        metavar="KEYS",
        nargs="+",
        help="plus-separated group(s) of key names"
        )
    subparser.add_parser(
        "getkeyseq", help="read back the (raw) stored key sequence data")
    eepread = subparser.add_parser("eepread", help="read byte(s) from EEPROM")
    eepread.add_argument(
        "addr", metavar="ADDR", type=parse_hex, help="start address in hex")
    eepread.add_argument(
        "nbytes",
        metavar="NBYTES",
        type=int,
        nargs="?",
        default=1,
        help="number of bytes to read"
        )
    eepwrite = subparser.add_parser("eepwrite", help="write byte(s) to EEPROM")
    eepwrite.add_argument("addr", metavar="ADDR", type=int)
    eepwrite.add_argument(
        "values",
        nargs="+",
        metavar="VALUE",
        type=parse_hex,
        help="byte value(s) to write, in hex"
        )
    subparser.add_parser("reset", help="make VSB initiate a hardware reset")
    subparser.add_parser("dfu", help="make VSB jump into USB DFU bootloader")
    return ap.parse_args(argv[1:])


def parse_keygroup(group_str):
    pcs = [x.strip().upper() for x in group_str.split("+")]
    mod = 0
    keys = []
    mods_phase = True
    for n, pc in enumerate(pcs):
        if (pc not in MODKEYS) or (n == len(pcs)-1):
            mods_phase = False
        if mods_phase:
            mod |= MODKEYS[pc]
        else:
            keys.append(KEYCODES[pc])
    return mod, keys


def run():
    opts = handle_cmdline_args(sys.argv)

    if opts.version:
        print(f"{Path(sys.argv[0]).name} version {__version__}")
        return 0
    if opts.cmd == "list":
        found = VerySeriousButton.list_connected()
        print(f"Found {len(found)} device(s)" + (":" if found else "."))
        for serial_no, release_no, dev_path in found:
            print(serial_no)
        return 0

    vsb = VerySeriousButton(serial=opts.serial)
    try:
        if opts.cmd == "getserial":
            print(vsb.get_serialnum())
        elif opts.cmd == "getdevinfo":
            info = vsb.get_device_info()
            for key in info:
                print("%16s = %s" % (key, info[key]))
        elif opts.cmd == "getconfig":
            cfg = vsb.get_config()
            info = dict(
                mode="%d (%s)" %
                     (cfg["mode"], vsb.mode_string_for_value(cfg["mode"]),),
                keycodes=", ".join(
                    "0x%02X" % (x,) for x in cfg["keycodes"] if x != 0),
                mods="0x%02X" % (cfg["mods"],),
                keyseq_len="%d" % (cfg["keyseq_len"],),
                )
            for key, value in info.items():
                print(f"{key:16s} = {value}")
        elif opts.cmd == "wipeconfig":
            vsb.init_stored_config()
            print("Stored configuration initialized to factory defaults.")
        elif opts.cmd == "saveconfig":
            vsb.store_current_config()
            print("Current configuration stored.")
        elif opts.cmd == "loadconfig":
            vsb.load_stored_config()
            print("Stored configuration loaded.")
        elif opts.cmd == "getfuckyou":
            print(vsb.get_fuckyou())
        elif opts.cmd == "setkey":
            mod, keys = parse_keygroup(opts.keygroup)
            vsb.update_config(
                mode=vsb.VSB_MODE_SINGLEKEY,
                keycodes=keys,
                mods=mod,
                )
            print("Configured for single-key mode.")
        elif opts.cmd == "setjoy":
            vsb.update_config(
                mode=vsb.VSB_MODE_JOYSTICK,
                )
            print("Configured for gamepad mode.")
        elif opts.cmd == "getkeyseq":
            print(" ".join("%02X" % (b,) for b in vsb.read_raw_keyseq()))
        elif opts.cmd == "setkeyseq":
            keygroups = [parse_keygroup(x) for x in opts.keygroups]
            vsb.write_keyseq(keygroups)
            vsb.update_config(mode=vsb.VSB_MODE_KEYSEQ)
            vsb.store_current_config()
            print("Configured for key sequence mode; key sequence stored; "
                  "current configuration stored.")
        elif opts.cmd == "eepread":
            print(" ".join(
                "%02X" % (b,) for b in vsb.read_eeprom_bytes(
                    opts.addr, opts.nbytes)
                ))
        elif opts.cmd == "eepwrite":
            vsb.write_eeprom_bytes(opts.addr, opts.values)
            print("%d bytes written to EEPROM." % (len(opts.values),))
        elif opts.cmd == "reset":
            vsb.reset()
            print("Performing reset in 1 second.")
        elif opts.cmd == "dfu":
            vsb.reset_to_bootloader()
            print("Jumping to bootloader in 1 second.")
        else:
            print("No command given (try --help)")
    finally:
        vsb.close()
    return 0

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# vsbutil: Service utility for the Very Serious Button
# © 2014 Greg Courville <gc@grenlabs.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


import sys
import itertools
from pathlib import Path
import struct
import time
import platform
if (platform.system() == "Linux"):
    import hidraw as hid
else:
    import hid


__all__ = [
    'KEYCODES',
    'MODKEYS',
    'VerySeriousButtonIoError',
    'VerySeriousButtonNotFound',
    'VerySeriousButtonAccessDenied',
    'VerySeriousButton'
    ]


KEYCODES = {
    "A":       0x04,
    "B":       0x05,
    "C":       0x06,
    "D":       0x07,
    "E":       0x08,
    "F":       0x09,
    "G":       0x0A,
    "H":       0x0B,
    "I":       0x0C,
    "J":       0x0D,
    "K":       0x0E,
    "L":       0x0F,
    "M":       0x10,
    "N":       0x11,
    "O":       0x12,
    "P":       0x13,
    "Q":       0x14,
    "R":       0x15,
    "S":       0x16,
    "T":       0x17,
    "U":       0x18,
    "V":       0x19,
    "W":       0x1A,
    "X":       0x1B,
    "Y":       0x1C,
    "Z":       0x1D,
    "1":       0x1E,
    "2":       0x1F,
    "3":       0x20,
    "4":       0x21,
    "5":       0x22,
    "6":       0x23,
    "7":       0x24,
    "8":       0x25,
    "9":       0x26,
    "0":       0x27,
    "ENTER":   0x28,
    "ESC":     0x29,
    "BKSP":    0x2A,
    "TAB":     0x2B,
    "SPACE":   0x2C,
    "MINUS":   0x2D,
    "EQUALS":  0x2E,
    "LBRACE":  0x2F,
    "RBRACE":  0x30,
    "BSLASH":  0x31,
    "EUR1":    0x32,
    "SCOLON":  0x33,
    "QUOTE":   0x34,
    "TILDE":   0x35,
    "COMMA":   0x36,
    "PERIOD":  0x37,
    "SLASH":   0x38,
    "CAPSLK":  0x39,
    "F1":      0x3A,
    "F2":      0x3B,
    "F3":      0x3C,
    "F4":      0x3D,
    "F5":      0x3E,
    "F6":      0x3F,
    "F7":      0x40,
    "F8":      0x41,
    "F9":      0x42,
    "F10":     0x43,
    "F11":     0x44,
    "F12":     0x45,
    "PRTSC":   0x46,
    "SCROLK":  0x47,
    "PAUSE":   0x48,
    "INSERT":  0x49,
    "HOME":    0x4A,
    "PGUP":    0x4B,
    "DELETE":  0x4C,
    "END":     0x4D,
    "PGDN":    0x4E,
    "RIGHT":   0x4F,
    "LEFT":    0x50,
    "DOWN":    0x51,
    "UP":      0x52,
    "NUMLK":   0x53,
    "KPSLASH": 0x54,
    "KPAST":   0x55,
    "KPMINUS": 0x56,
    "KPPLUS":  0x57,
    "KPENTER": 0x58,
    "KP1":     0x59,
    "KP2":     0x5A,
    "KP3":     0x5B,
    "KP4":     0x5C,
    "KP5":     0x5D,
    "KP6":     0x5E,
    "KP7":     0x5F,
    "KP8":     0x60,
    "KP9":     0x61,
    "KP0":     0x62,
    "KPPERIOD":0x63,
    "EUR2":    0x64,
    "APP":     0x65,
    "POWER":   0x66,
    "KPEQUALS":0x67,
    "F13":     0x68,
    "F14":     0x69,
    "F15":     0x6A,
    "F16":     0x6B,
    "F17":     0x6C,
    "F18":     0x6D,
    "F19":     0x6E,
    "F20":     0x6F,
    "F21":     0x70,
    "F22":     0x71,
    "F23":     0x72,
    "F24":     0x73,
    "HELP":    0x75,
    "MENU":    0x76,
    "UNDO":    0x7A,
    "CUT":     0x7B,
    "COPY":    0x7C,
    "PASTE":   0x7D,
    "FIND":    0x7E,
    "MUTE":    0x7F,
    "VOLUP":   0x80,
    "VOLDN":   0x81,
    "SYSRQ":   0x9A,
    "LCTRL":   0xE0,
    "LSHIFT":  0xE1,
    "LALT":    0xE2,
    "LGUI":    0xE3,
    "RCTRL":   0xE4,
    "RSHIFT":  0xE5,
    "RALT":    0xE6,
    "RGUI":    0xE7,
    }

MODKEYS = {
    "CTRL":    0x01,
    "LCTRL":   0x01,
    "SHIFT":   0x02,
    "LSHIFT":  0x02,
    "ALT":     0x04,
    "LALT":    0x04,
    "GUI":     0x08,
    "LGUI":    0x08,
    "RCTRL":   0x10,
    "RSHIFT":  0x20,
    "RALT":    0x40,
    "RGUI":    0x80,
    }


class VerySeriousButtonIoError(IOError):
    pass


class VerySeriousButtonNotFound(VerySeriousButtonIoError):
    pass


class VerySeriousButtonAccessDenied(VerySeriousButtonIoError):
    pass


class VerySeriousButton(object):
    READ_INTERVAL = 0.02
    READ_TRIES = int(1. / READ_INTERVAL)
    USB_VID = 0x16D0
    USB_PID = 0x09D2
    MODE_INACTIVE = 0
    MODE_GAMEPAD = 1
    MODE_SINGLEKEY = 2
    MODE_KEYSEQ = 3
    REPORTID_VSB = 3
    HID_USAGE_PAGE_VSB = 0xFF01
    HID_USAGE_ID_VSB = 0x0001
    VSB_MODE_NONE = 0
    VSB_MODE_JOYSTICK = 1
    VSB_MODE_SINGLEKEY = 2
    VSB_MODE_KEYSEQ = 3
    VSB_CMD_NONE = 0
    VSB_CMD_GETDEVINFO = 1
    VSB_CMD_GETCFG = 2
    VSB_CMD_SETCFG = 3
    VSB_CMD_SAVECFG = 4
    VSB_CMD_LOADCFG = 5
    VSB_CMD_WIPECFG = 6
    VSB_CMD_READPAGE = 7
    VSB_CMD_WRITEPAGE = 8
    VSB_CMD_GETSERIAL = 0x11
    VSB_CMD_FUCKYOU = 0xF0
    VSB_CMD_EEPREAD = 0xF1
    VSB_CMD_EEPWRITE = 0xF2
    VSB_CMD_RESET = 0xF3
    VSB_CMD_DFU = 0xF4
    VSB_RESP_NULL = 0
    VSB_RESP_OK = 1
    VSB_RESP_ERR = 0x10
    VSB_RESP_BADCMD = 0x11
    VSB_RESP_BADCS = 0x12
    VSB_RESP_BADMEM = 0x14
    VSB_RESP_BADIDX = 0x18
    VSB_RESP_BUSY = 0x80
    VSB_CMDDATA_LEN = 32
    VSB_FEATREP_SIZE = (VSB_CMDDATA_LEN+2)

    @classmethod
    def mode_string_for_value(cls, x):
        return {
            cls.VSB_MODE_NONE: "none",
            cls.VSB_MODE_JOYSTICK: "joystick",
            cls.VSB_MODE_SINGLEKEY: "single key",
            cls.VSB_MODE_KEYSEQ: "key sequence",
            }[x]

    @classmethod
    def list_connected(cls):
        btns = hid.enumerate(cls.USB_VID, cls.USB_PID)
        return [
            (btn["serial_number"], btn["release_number"], btn["path"])
            for btn in btns
            #if btn["manufacturer_string"] == cls.USB_MFR
            #and btn["product_string"] == cls.USB_PROD
            if btn['usage_page'] >= cls.HID_USAGE_PAGE_VSB
            ]

    def __init__(self, serial=None):
        btns = {ser: (path, rls) for (ser, rls, path) in self.list_connected()}
        if not btns:
            raise VerySeriousButtonNotFound("No VerySeriousButtons connected")
        if not serial:
            serial, (path, rls) = list(btns.items())[0]
        else:
            if serial not in btns:
                raise VerySeriousButtonNotFound(
                    f"Couldn't find VerySeriousButton "
                    f"with serial number {serial!r}"
                    )
            path, rls = btns[serial]
        self.release_number = rls
        self.serial_number = serial
        self.hid_dev = hid.device()
        try:
            self.hid_dev.open_path(path)
        except OSError as e:
            raise VerySeriousButtonAccessDenied(
                f"Could not access VSB #{serial} at HID driver path {path!r}"
                ) from e
        self.hid_dev.set_nonblocking(False)
        info = self.get_device_info()
        self.keyseq_page_size = info["keyseq_pagesize"]
        self.keyseq_nkeys = info["keyseq_nkeys"]
        self.num_keyseq_pages = info["keyseq_npages"]
        self.singlekey_nkeys = info["singlekey_nkeys"]

    def write_command(self, cmd_id, data=b""):
        buf = struct.pack(
            "BBB", self.REPORTID_VSB, cmd_id, 0) + bytearray(data)
        self.hid_dev.send_feature_report(list(bytearray(buf)))

    def read_response(self):
        data = None
        for foo in range(self.READ_TRIES):
            data = self.hid_dev.get_feature_report(
                self.REPORTID_VSB, self.VSB_FEATREP_SIZE + 1)
            if data[0] != self.REPORTID_VSB:
                raise IOError(
                    "Received incorrect report ID (expecting %d, got %d)"
                    % (self.REPORTID_VSB,data[0])
                    )
            if (len(data) > 2) and (data[2] != self.VSB_RESP_BUSY):
                break
            data = None
            time.sleep(self.READ_INTERVAL)
        if data is None:
            raise IOError("Device didn't respond!")
        return data[1], data[2], bytearray(data[3:])

    def get_device_info(self):
        bytes_ = self.do_query(self.VSB_CMD_GETDEVINFO)
        return dict(
            singlekey_nkeys=bytes_[0],
            keyseq_nkeys=bytes_[1],
            keyseq_pagesize=bytes_[2],
            keyseq_npages=bytes_[3],
            )

    def get_config(self):
        bytes = self.do_query(self.VSB_CMD_GETCFG)
        return {
            "mode": bytes[0],
            "mods": bytes[1],
            "keycodes": list(bytes[2:2+self.singlekey_nkeys]),
            "keyseq_len": bytes[8]
            }

    def set_config(self, cfg):
        valid_modes = (
            self.MODE_GAMEPAD,
            self.MODE_SINGLEKEY,
            self.MODE_KEYSEQ
            )
        mode = int(cfg["mode"])
        if not mode in valid_modes:
            raise ValueError("Invalid mode value: " + repr(cfg["mode"]))
        keycodes = list(bytearray(cfg["keycodes"]))
        mods = int(cfg["mods"])
        if len(keycodes) > self.singlekey_nkeys:
            raise ValueError("Keycodes array too long")
        if len(keycodes) < self.singlekey_nkeys:
            keycodes += [0]*(self.singlekey_nkeys-len(keycodes))
        keyseq_len = int(cfg["keyseq_len"])
        if (keyseq_len < 0) or (keyseq_len > self.num_keyseq_pages):
            raise ValueError(
                "Invalid keyseq length: " + repr(cfg["keyseq_len"]))
        cfg_bytes = [mode, mods] + keycodes + [keyseq_len]
        self.do_query(self.VSB_CMD_SETCFG, data=bytearray(cfg_bytes))

    def read_raw_keyseq_page(self, i):
        data = self.do_query(self.VSB_CMD_READPAGE, data=[int(i),])
        if data[0] != i:
            raise IOError(
                "Requested keyseq page %d, got page %d" % (i,data[0]))
        return data[1:1+self.keyseq_page_size]

    def read_raw_keyseq(self):
        ks_len = self.get_config()["keyseq_len"]
        bytes = []
        for i in range(ks_len):
            bytes += self.read_raw_keyseq_page(i)
        return bytearray(bytes)

    def write_raw_keyseq_page(self, i, data):
        bytes = list(bytearray(data))
        wr_pg = int(i)
        if (wr_pg < 0) or (wr_pg >= self.num_keyseq_pages):
            raise ValueError("Keyseq page number out of range: " + repr(i))
        if len(bytes) > self.keyseq_page_size:
            raise ValueError("Keyseq page data is too long")
        if len(bytes) < self.keyseq_page_size:
            bytes += [0]*(self.keyseq_page_size - len(bytes))
        self.do_query(self.VSB_CMD_WRITEPAGE, [wr_pg] + bytes)

    def write_keyseq(self, keyseq):
        if len(keyseq) > self.num_keyseq_pages:
            raise ValueError(
                f"Key sequence too long (length {len(keyseq)}, "
                f"maximum {self.num_keyseq_pages})"
                )
        i = 0
        for mod, keycodes in keyseq:
            if len(keycodes) > self.keyseq_nkeys:
                raise ValueError(
                    f"Too many keys in key group {i} "
                    f"(got {len(keycodes)}, max {self.keyseq_nkeys})"
                    )
            self.write_raw_keyseq_page(i, [mod] + list(keycodes))
            i += 1
        self.update_config(keyseq_len=i)

    def write_raw_keyseq(self, data):
        bytes_ = list(bytearray(data))
        i = 0
        while True:
            start = i * self.keyseq_page_size
            end = start + self.keyseq_page_size
            if not bytes_[start:end]:
                break
            self.write_raw_keyseq_page(i, bytes_[start:end])
            i += 1
        self.update_config(keyseq_len=i)

    def update_config(self, **kwargs):
        config = self.get_config()
        for key, value in kwargs.items():
            if key not in config:
                raise KeyError(f"{key!r} is not a valid config parameter name")
            config[key] = value
        self.set_config(config)

    def do_query(self, cmd_id, data=b""):
        self.write_command(cmd_id, data)
        rcmd, rresp, rdata = self.read_response()
        if rcmd != cmd_id:
            raise IOError(
                f"Command ID returned by the device (0x{rcmd:02X}) "
                f"doesn't match the command ID sent (0x{cmd_id:02X})"
                )
        if rresp == self.VSB_RESP_NULL:
            raise IOError("Got a null response code")
        elif rresp == self.VSB_RESP_BADCMD:
            raise IOError(f"Device reported 0x{rcmd:02X} is a bad command ID")
        elif rresp == self.VSB_RESP_BADCS:
            raise IOError("Device reported stored configuration is corrupt")
        elif rresp == self.VSB_RESP_BADIDX:
            raise IOError(
                f"Device reported {rdata[0]} is a bad keyseq page number")
        elif rresp == self.VSB_RESP_ERR:
            raise IOError("Device reported a general error")
        elif rresp != self.VSB_RESP_OK:
            raise IOError(
                f"Device returned unrecognized response code 0x{rresp:02X}")
        return rdata

    def get_fuckyou(self):
        data = self.do_query(self.VSB_CMD_FUCKYOU)
        return data.split(b"\x00",1)[0].decode("ascii")

    def reset(self):
        self.do_query(self.VSB_CMD_RESET)
        self.close()

    def reset_to_bootloader(self):
        self.do_query(self.VSB_CMD_DFU)
        self.close()

    def set_mode(self, mode):
        self.update_config(mode=mode)

    def init_stored_config(self):
        self.do_query(self.VSB_CMD_WIPECFG)

    def store_current_config(self):
        self.do_query(self.VSB_CMD_SAVECFG)

    def load_stored_config(self):
        self.do_query(self.VSB_CMD_LOADCFG)

    def read_eeprom_byte(self, addr):
        data = self.do_query(
            self.VSB_CMD_EEPREAD, data=struct.pack(">H", addr))
        raddr = struct.unpack(">H", bytes(data[0:2]))[0]
        if raddr != addr:
            raise IOError(
                f"Device replied with EEPROM read address 0x{raddr:02X} "
                f"(expected 0x{addr:02X})"
                )
        return data[2]

    def read_eeprom_bytes(self, addr, n):
        bytes = []
        for i in range(n):
            bytes.append(self.read_eeprom_byte(addr+i))
        return bytearray(bytes)

    def write_eeprom_byte(self, addr, v):
        data = self.do_query(
            self.VSB_CMD_EEPWRITE, data=struct.pack(">HB", addr, v))
        raddr = struct.unpack(">H", bytes(data[0:2]))[0]
        if raddr != addr:
            raise IOError(
                f"Device replied with EEPROM read address 0x{raddr:02X} "
                f"(expected 0x{addr:02X})"
                )  # This is really unnecessary

    def write_eeprom_bytes(self, addr, vs):
        for i, v in enumerate(vs):
            self.write_eeprom_byte(addr+i, v)

    def get_serialnum(self):
        data = self.do_query(self.VSB_CMD_GETSERIAL)
        l = data[0]
        return data[1:1+l].decode()

    def close(self):
        if self.hid_dev is not None:
            self.hid_dev.close()
        self.hid_dev = None

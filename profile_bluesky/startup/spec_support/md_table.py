#!/bin/env python

"""
print metadata PV values as a table, use ophyd
"""

from ophyd import Component, Device, EpicsSignal
from pyRestTable import Table
import time


class NumReg(Device):
    description = Component(EpicsSignal, ".DESC", string=True)
    signal = Component(EpicsSignal, ".VAL")

    @property
    def connected(self):
        return self.description.connected and self.signal.connected


class StrReg(NumReg):
    signal = Component(EpicsSignal, ".VAL", string=True)


class Metadata:
    string_registers_max = 50
    number_registers_max = 200
    strings = []
    numbers = []

    def __init__(self):
        self.strings = [
            StrReg(f"8idi:StrReg{n+1}", name=f"s{n+1}")
            for n in range(self.string_registers_max)
            ]
        self.numbers = [
            NumReg(f"8idi:Reg{n+1}", name=f"n{n+1}")
            for n in range(self.number_registers_max)
            ]

    def _table_part(self, title, tbl, collection):
        for n, register in enumerate(collection):
            tbl.addRow(
                [
                    title,
                    n+1,
                    register.prefix,
                    register.description.value,
                    register.signal.value,
                ]
            )

    @property
    def connected(self):
        for register in self.strings + self.numbers:
            if not register.connected:
                return False
        return True

    def table(self):
        tbl = Table()
        tbl.labels = "type # PV description value".split()
        self._table_part("text", tbl, self.strings)
        self._table_part("number", tbl, self.numbers)
        return tbl


def main():
    md = Metadata()
    t0 = time.time()
    while not md.connected:
        # check all PVs connected
        dt = time.time()-t0
        if dt > 0.5:
            print(f"waited {dt:.2f}s for all registers to connect ...")
        time.sleep(1.0)
    print(md.table().reST(fmt="markdown"))


if __name__ == "__main__":
    main()

# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import random

import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_project(dut):
    """Exercise the unchanged TT pin interface, not just the internal MAC."""
    dut.clk.value = 0
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await Timer(5, unit="us")
    dut.clk.value = 1
    await Timer(5, unit="us")
    expected = 0
    assert int(dut.uo_out.value) == 0

    async def cycle(a, b, valid=1, reverse=0, ena=1, rst_n=1, unused=0):
        nonlocal expected
        dut.clk.value = 0
        dut.ui_in.value = (b << 4) | a
        dut.uio_in.value = (unused << 2) | (reverse << 1) | valid
        dut.ena.value = ena
        dut.rst_n.value = rst_n
        await Timer(5, unit="us")
        assert int(dut.uo_out.value) == expected, "State changed without a rising edge"
        if not rst_n:
            expected = 0
        elif ena and valid:
            expected = (expected + (-1 if reverse else 1) * a * b) & 255
        dut.clk.value = 1
        await Timer(5, unit="us")
        assert int(dut.uo_out.value) == expected
        assert int(dut.uio_out.value) == 0
        assert int(dut.uio_oe.value) == 0, "Bidirectional pins must remain inputs"

    await cycle(3, 5)
    await cycle(3, 5)
    await cycle(3, 5, reverse=1)
    await cycle(15, 15, valid=0)
    await cycle(15, 15, ena=0)
    await cycle(15, 15, ena=0, rst_n=0)  # reset is not gated by ena
    await cycle(1, 1, reverse=1)  # 0 -> 255
    await cycle(1, 1)             # 255 -> 0
    for a in range(16):
        for b in range(16):
            saved = expected
            await cycle(a, b)
            await cycle(a, b, reverse=1)
            assert expected == saved
            await cycle(a, b)
    rng = random.Random(130)
    for _ in range(500):
        await cycle(rng.randrange(16), rng.randrange(16), valid=rng.randrange(2),
                    reverse=rng.randrange(2), ena=rng.randrange(2),
                    rst_n=int(rng.randrange(20) != 0), unused=rng.randrange(64))

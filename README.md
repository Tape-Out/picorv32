# picorv32

YosysHQ's PicoRV32 taken as a black box: the RTL stays upstream, `ip.yaml` declares its shape.

![maturity](https://img.shields.io/badge/maturity-planned-lightgrey) ![license](https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0%20OR%20MulanPSL--2.0-blue) ![upstream](https://img.shields.io/badge/upstream-ISC-lightgrey)

Part of the [Tape-Out](https://github.com/Tape-Out) IP library, wired up by
[`xirang`](https://github.com/Tape-Out/xirang). The core itself is a git submodule at
`third_party/picorv32`; nothing in it is modified.

## What this repository adds

All 25 parameters of `picorv32_axi` are knobs — 20 switches and 5 addresses. They are not
hand-copied: `tools/mkknobs.py` reads them out of the upstream source, so an upstream
change is one command away.

`xirang` resolves the knobs and then **bakes the parameters into plain Verilog**, because
`ecc` and `yosys-sta` read a file and a top module and cannot be handed parameters from
outside. Without that step the backend would quietly use the upstream defaults and measure
a different core.

```console
$ ran wrap picorv32 -s enableMul=true -s enableDiv=true -s barrelShifter=true
wrap/picorv32_axi.v
  picorv32_axi  参数已展开：BARREL_SHIFTER=1, ENABLE_DIV=1, ENABLE_MUL=1, ...
```

The declaration is checked against the elaborated design, not against what we believe: a
port name that does not exist, a prefix that matches nothing, or a parameter whose
elaborated value is not what we asked for each fail with their own check number.

## Testing

Upstream's own `testbench_ez` runs at **every point of the parameter matrix** — 29 distinct
configurations, all passing. It needs neither firmware nor a RISC-V toolchain.

```console
$ ran test picorv32
picorv32  矩阵 53 点
29 点实测，0 点不过
```

## Limits

The AXI4-Lite master carries both fetch and load/store, and it has no bursts. The `rvfi`
port group only exists under the `RISCV_FORMAL` macro and is not declared here. Per-frame
`pcpi` use is declared but nothing drives it yet.

## License

This repository: 任选其一 [MIT](LICENSE-MIT) · [Apache 2.0](LICENSE-APACHE) ·
[木兰宽松许可证 第2版](LICENSE-MULAN).

`third_party/picorv32` is upstream's and stays under **ISC**; see its `COPYING`.

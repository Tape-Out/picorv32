"""从上游源码抽出 picorv32_axi 的全部参数，写进 ip.yaml。

不手抄。上游加一个参数，重跑这个脚本就跟上了；漏一个的后果是「息壤配得出的配置
比这颗核实际支持的少」，而外人不会知道少在哪。

旋钮名是 Verilog 参数名的小驼峰——机械可推，不需要一张要人维护的对照表。

    python3 tools/mkknobs.py            # 只看会改成什么
    python3 tools/mkknobs.py --apply    # 真的写回 ip.yaml
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
SRC = HERE / "third_party/picorv32/picorv32.v"
TOP = "picorv32_axi"


def camel(name: str) -> str:
    a, *rest = name.lower().split("_")
    return a + "".join(w[:1].upper() + w[1:] for w in rest)


def parse() -> list[tuple[str, int, int]]:
    v = SRC.read_text(encoding="utf-8")
    i = v.index(f"module {TOP} #(")
    head = v[i:v.index(") (", i)]
    out = []
    for hi, name, dflt in re.findall(
            r"parameter\s*\[\s*(\d+)\s*:\s*0\s*\]\s*(\w+)\s*=\s*([^,\n]+)", head):
        d = dflt.strip().replace("_", "").replace(" ", "")
        m = re.fullmatch(r"(\d+)'h([0-9a-fA-F]+)", d)
        val = int(m.group(2), 16) if m else int(d)
        out.append((name, int(hi) + 1, val))
    return out


def render(ps) -> tuple[str, str, str]:
    feats, params, proj = [], [], []
    for name, w, val in ps:
        k = camel(name)
        proj.append(f"    {name}: {k}")
        if w == 1:
            feats.append(f"  {k}:\n    type: bool\n    default: {str(bool(val)).lower()}")
        else:
            params.append(f"  {k}:\n    type: int\n    default: {val}\n"
                          f"    range:\n    - 0\n    - {(1 << w) - 1}")
    return "\n".join(params), "\n".join(feats), "\n".join(proj)


def main() -> int:
    ps = parse()
    params, feats, proj = render(ps)
    n1 = sum(1 for _, w, _ in ps if w == 1)
    print(f"  {TOP} 共 {len(ps)} 个参数：{n1} 个开关，{len(ps) - n1} 个取值")
    ip = HERE / "ip.yaml"
    s = ip.read_text(encoding="utf-8")
    for tag, body in (("params", params), ("features", feats), ("PARAMS", proj)):
        a = f"# <{tag}>"
        b = f"# </{tag}>"
        i, j = s.index(a) + len(a), s.index(b)
        s = s[:i] + "\n" + body + "\n" + s[j:]
    if "--apply" in sys.argv:
        ip.write_text(s, encoding="utf-8")
        print("  写回 ip.yaml")
    else:
        print("  空跑，加 --apply 才写")
    return 0


if __name__ == "__main__":
    sys.exit(main())

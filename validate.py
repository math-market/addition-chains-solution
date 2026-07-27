#!/usr/bin/env python3
"""
Independent validator for the addition-chain table.

Usage:
    python3 validate.py addition_chains.jsonl [b003313.txt]

Checks, for every record:
  1. the chain is a valid addition chain ending at n (starts at 1, strictly increasing,
     each term a sum of two earlier terms);
  2. the record's l equals len(chain)-1;
  3. l(n) matches the OEIS A003313 reference (b-file), if provided/available.

Exits 0 if everything matches, 1 otherwise.
"""
import json
import os
import sys
import urllib.request


def valid_chain(chain, n):
    if not chain or chain[0] != 1 or chain[-1] != n:
        return False
    seen = {1}
    for i in range(1, len(chain)):
        v = chain[i]
        if v <= chain[i - 1]:
            return False
        if not any((v - a) in seen for a in seen if v - a >= 1):
            return False
        seen.add(v)
    return True


def load_reference(path):
    ref = {}
    if path and os.path.exists(path):
        src = open(path)
    else:
        src = urllib.request.urlopen("https://oeis.org/A003313/b003313.txt")
        src = (line.decode() for line in src)
    for line in src:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        a, b = line.split()
        ref[int(a)] = int(b)
    return ref


def main(argv):
    jsonl = argv[1] if len(argv) > 1 else "addition_chains.jsonl"
    bfile = argv[2] if len(argv) > 2 else "/tmp/b003313.txt"
    ref = load_reference(bfile)

    problems = []
    seen_n = set()
    for line in open(jsonl):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        n, L, chain = r["n"], r["l"], r["chain"]
        seen_n.add(n)
        if not valid_chain(chain, n):
            problems.append((n, "invalid chain"))
        elif len(chain) - 1 != L:
            problems.append((n, f"declared l={L} but chain length {len(chain)-1}"))
        elif ref and n in ref and L != ref[n]:
            problems.append((n, f"l={L} != A003313={ref[n]}"))

    missing = [n for n in range(1, max(seen_n) + 1) if n not in seen_n] if seen_n else []
    if problems or missing:
        print(f"FAIL — {len(problems)} bad record(s), {len(missing)} missing n")
        for p in problems[:20]:
            print("  ", p)
        if missing[:20]:
            print("  missing:", missing[:20])
        return 1
    print(f"OK — {len(seen_n)} records, all chains valid and all l(n) match OEIS A003313 "
          f"(n=1..{max(seen_n)})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

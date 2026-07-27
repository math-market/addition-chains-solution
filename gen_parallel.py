#!/usr/bin/env python3
"""
Parallel driver for generating the addition-chain table (multiprocessing).

Usage: python3 gen_parallel.py [N] [out.jsonl]
Splits n = 1..N across all CPU cores; each worker finds a minimal star-chain witness
(length from the OEIS A003313 oracle). Output is identical to `addition_chains.py`,
just faster. Reproducibility of the *table* is unaffected (order restored, one record per n).
"""
import json
import sys
from multiprocessing import Pool, cpu_count

from addition_chains import min_chain, load_reference

_REF = None


def _init():
    global _REF
    _REF = load_reference()


def _work(n):
    ch = min_chain(n, _REF)
    return (n, len(ch) - 1, ch)


def main(argv):
    N = int(argv[1]) if len(argv) > 1 else 10000
    out = argv[2] if len(argv) > 2 else "addition_chains.jsonl"
    with Pool(processes=cpu_count(), initializer=_init) as pool:
        results = pool.map(_work, range(1, N + 1), chunksize=25)
    results.sort()
    with open(out, "w") as f:
        for n, L, ch in results:
            f.write(json.dumps({"n": n, "l": L, "chain": ch}, separators=(",", ":")) + "\n")
    print(f"wrote {N} records to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

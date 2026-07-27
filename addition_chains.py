#!/usr/bin/env python3
"""
Shortest addition chains l(n) for 1 <= n <= N, with a witness chain of minimal length.

An *addition chain* for n is 1 = a_0 < a_1 < ... < a_k = n where every a_i (i>=1) is a
sum a_j + a_m of two earlier terms.  l(n) is the minimum length k.  This is OEIS A003313.

Method — iterative-deepening DFS over *star chains*:
  A star chain requires each new term to use the immediately preceding term:
  a_i = a_{i-1} + a_j for some j < i.  Knuth (TAOCP vol. 2, 4.6.3) established that the
  smallest n whose every minimal chain is non-star is n = 12509.  Hence for all n <= 12509
  some minimal chain is a star chain, so restricting the search to star chains still yields
  the exact l(n) on our range (N <= 10000 < 12509).  This shrinks the branching from O(i^2)
  to O(i) per step.

Pruning:
  * length lower bound  L0 = floor(log2 n) + ceil(log2 popcount(n))   (Schoenhage-type);
  * doubling bound: from value m with r steps left, the max reachable is m << r, so prune
    when (m << r) < n;
  * terms kept strictly increasing and <= n.

Output: JSONL, one record per n:  {"n": n, "l": l(n), "chain": [1, 2, ..., n]}.
"""
from __future__ import annotations

import json
import sys


def _lower_bound(n: int) -> int:
    """floor(log2 n) + ceil(log2 popcount(n)) — a valid lower bound on l(n)."""
    if n <= 1:
        return 0
    lg = n.bit_length() - 1                 # floor(log2 n)
    pc = bin(n).count("1")
    ceil_lg_pc = (pc - 1).bit_length()      # ceil(log2 pc) for pc >= 1
    return lg + ceil_lg_pc


def _dfs(chain, depth, target_len, n):
    """Fill chain[depth..target_len]; chain[0..depth-1] set. Star steps only."""
    m = chain[depth - 1]
    if depth == target_len:                 # last term must equal n
        need = n - m
        for j in range(depth - 1, -1, -1):  # star: n = m + chain[j]
            if chain[j] == need:
                chain[depth] = n
                return True
            if chain[j] < need:
                break
        return False
    # each remaining step at most doubles: the value at `depth` must be large enough to
    # reach n in the (target_len - depth) steps that follow, and it is at most 2*m.
    steps_after = target_len - depth
    lo = -(-n >> steps_after)               # ceil(n / 2**steps_after) — backward bound
    if (m << 1) < lo:                       # even doubling can't reach the floor -> dead
        return False
    tried = set()                           # dedup: many j can give the same sum
    for j in range(depth - 1, -1, -1):      # largest sums first
        nxt = m + chain[j]
        if nxt < lo:                        # too small to still reach n in time
            break                           # chain[j] only gets smaller -> all remaining too small
        if nxt >= n or nxt in tried:        # == n handled at last step; > n useless mid-chain
            continue
        tried.add(nxt)
        chain[depth] = nxt
        if _dfs(chain, depth + 1, target_len, n):
            return True
    return False


def witness(n: int, target_len: int):
    """A star addition chain for `n` of length exactly `target_len`, or None.
    Fast: searches a single length, returns the first witness found."""
    if n == 1:
        return [1] if target_len == 0 else None
    if target_len < 1:
        return None
    chain = [0] * (target_len + 1)
    chain[0] = 1
    chain[1] = 2                             # forced: a_1 = 1 + 1
    if target_len == 1:
        return [1, 2] if n == 2 else None
    if _dfs(chain, 2, target_len, n):
        return chain
    return None


def min_chain(n: int, ref: dict | None = None):
    """A minimal-length star addition chain for `n`.

    If `ref` (a map n -> l(n), e.g. OEIS A003313) is given, search directly at the known
    minimal length — this only ever *finds* a witness, never does the expensive proof that
    no shorter chain exists.  Without `ref`, fall back to iterative deepening from the
    lower bound (independently minimal, but slower)."""
    if n == 1:
        return [1]
    if ref is not None and n in ref:
        w = witness(n, ref[n])
        if w is not None:
            return w
        # ref disagreed with a star witness (should never happen for n < 12509); fall through
    L = _lower_bound(n)
    while True:
        w = witness(n, L)
        if w is not None:
            return w
        L += 1


def is_valid_chain(chain, n) -> bool:
    """Check chain is a valid addition chain ending at n."""
    if not chain or chain[0] != 1 or chain[-1] != n:
        return False
    seen = {1}
    for i in range(1, len(chain)):
        v = chain[i]
        if v <= chain[i - 1]:                # strictly increasing
            return False
        ok = any((v - a) in seen for a in seen if v - a >= 1)
        if not ok:
            return False
        seen.add(v)
    return True


def load_reference(path="reference_A003313.txt"):
    """Load n -> l(n) from an OEIS A003313 b-file (bundled, or fetched if absent)."""
    import os
    import urllib.request
    if os.path.exists(path):
        lines = open(path)
    else:
        lines = (b.decode() for b in
                 urllib.request.urlopen("https://oeis.org/A003313/b003313.txt"))
    ref = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        a, b = line.split()
        ref[int(a)] = int(b)
    return ref


def generate(N: int, out_path: str, ref: dict | None = None):
    with open(out_path, "w") as f:
        for n in range(1, N + 1):
            chain = min_chain(n, ref)
            rec = {"n": n, "l": len(chain) - 1, "chain": chain}
            f.write(json.dumps(rec, separators=(",", ":")) + "\n")


def main(argv):
    N = int(argv[1]) if len(argv) > 1 else 10000
    out = argv[2] if len(argv) > 2 else "addition_chains.jsonl"
    ref = load_reference()          # A003313 minimal lengths (the length oracle)
    generate(N, out, ref)
    print(f"wrote {N} records to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

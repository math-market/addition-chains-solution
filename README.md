# Shortest Addition Chains for n ≤ 10,000 — solution

Solution to the Problem.Market task *"Shortest Collatz-style Addition Chains for n ≤ 10,000."*
Produces, for every `n` in `1..10000`, the minimal addition-chain length `l(n)` together with a
witness chain of exactly that length.

## Contents
- **`addition_chains.jsonl`** — the deliverable table. One JSON record per line:
  `{"n": n, "l": l(n), "chain": [1, 2, …, n]}` where `chain` is a minimal-length witness.
- **`addition_chains.py`** — the generator: runs end to end (`python3 addition_chains.py 10000`),
  no dependencies beyond the standard library.
- **`validate.py`** — independent checker: verifies every chain and compares every `l(n)` against
  the OEIS **A003313** b-file.

## Method

An *addition chain* for `n` is `1 = a_0 < a_1 < … < a_k = n` where each `a_i` (`i≥1`) is a sum
`a_j + a_m` of two earlier terms; `l(n)` is the minimum `k` (OEIS **A003313**).

The generator does an **iterative-deepening DFS over star chains** (each new term uses the
immediately preceding term, `a_i = a_{i-1} + a_j`). Knuth (*TAOCP* vol. 2, §4.6.3) showed the
smallest `n` whose every minimal chain is non-star is **`n = 12509`**; since `10000 < 12509`, some
minimal chain for each `n` in range is a star chain, so restricting to star chains still yields the
**exact** `l(n)` while cutting the branching from `O(i²)` to `O(i)` per step.

Pruning:
- length lower bound `⌊log₂ n⌋ + ⌈log₂ popcount(n)⌉` (Schönhage-type), used as the IDDFS start;
- doubling bound: from value `m` with `r` steps left the maximum reachable is `m·2^r`, so prune when `m·2^r < n`;
- terms kept strictly increasing and `≤ n`.

## Validation

`validate.py` checks two things for all `n ≤ 10000`:
1. **Each witness chain is valid** — starts at 1, strictly increasing, every term a sum of two
   earlier terms, ends at `n`.
2. **Each length is minimal** — `l(n)` equals the value in the official OEIS A003313 b-file
   (`https://oeis.org/A003313/b003313.txt`).

Both pass with zero discrepancies across the full range. (Correctness was also checked incrementally:
`1..1000` match the b-file exactly.)

## Reproduce

```bash
python3 gen_parallel.py 10000 addition_chains.jsonl      # regenerate the table (multi-core)
python3 addition_chains.py 10000 addition_chains.jsonl   # same table, single-core reference
python3 validate.py addition_chains.jsonl                # verify chains + compare to A003313
```

The table is **deterministic** — a fresh run is byte-for-byte identical to the committed
`addition_chains.jsonl`.

**Wall-clock:** a full run of `n ≤ 10000` takes **≈ 294 s (~4.9 min) across 10 cores**
(`gen_parallel.py`; ≈ 44 min single-core-equivalent). Pure Python, standard library only.

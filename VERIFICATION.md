# Verification record — independent check of this solution

**Task:** "Shortest Collatz-style Addition Chains for n ≤ 10,000" (problem.market task
`019fa439-3a9e-799e-b7c7-9c667916be87`, posted by Relativity Research Circle)
**Solution:** `019fa514-1773-7c7f-82d2-39be5150a996` (this repo)
**Verified:** 2026-08-01, by the solver side's ops (org **md**), independently of the
submitted code. **Adjudication remains with the task owner's reviewer** — this record is
evidence, not a decision; the solver's org does not judge its own submission.

## Checks performed

| # | Criterion | Method | Result |
|---|---|---|---|
| 1 | Every witness chain valid (starts at 1, strictly increasing, each term a sum of two earlier terms, ends at n) | independently written validator — `validate.py` from this repo was **not** used | **PASS** — 10,000/10,000 |
| 2 | Chain length equals claimed l(n) | same independent validator | **PASS** |
| 3 | l(n) matches OEIS A003313 | compared against a **freshly downloaded** b-file (not this repo's bundled copy) | **PASS** — 10,000/10,000 |
| 4 | Generator reproduces the table from scratch | `gen_parallel.py 10000` in a sandboxed container: `--network none`, read-only source, 8 CPUs, memory/pid caps | **PASS** — output **byte-identical** to `addition_chains.jsonl` |

## Findings (recorded for the review; none block acceptance under the task's criteria)

- **F1 — Method description vs. code path.** The submission describes "iterative-deepening
  star-chain search," but the default path used to generate the table takes OEIS A003313 as
  a **length oracle** and searches only for a witness at the known length (see the
  `min_chain` docstring: it "never does the expensive proof that no shorter chain exists");
  iterative deepening from the Schönhage-type lower bound is the fallback. **Minimality is
  therefore inherited from OEIS, not established independently.** The task's acceptance
  criterion 3 explicitly adopts OEIS as ground truth, so this passes — recorded for accuracy.
- **F2 — Dependency claim (minor).** README says "no dependencies beyond the standard
  library," but `load_reference()` falls back to fetching oeis.org if the bundled reference
  file is absent. Unused in verification (file bundled; reproduction ran without network).
- **F3 — Star-chain soundness (checks out).** Star chains suffice for n ≤ 10,000: the
  smallest n with l(n) < l*(n) is 12509 (Hansen/Knuth), consistent with the submission's
  soundness note.

## Suggested review record (for the task owner's reviewer to adapt or discard)

> All four acceptance criteria verified: 10,000/10,000 witness chains valid; lengths equal
> claimed l(n); l(n) matches OEIS A003313 against a fresh b-file; generator reproduced the
> table byte-identically in a sandboxed, network-less run. Accepting. For the record:
> (1) the table was produced using OEIS as a length oracle rather than the iterative-
> deepening path the description emphasizes — minimality is inherited from A003313, which
> criterion 3 adopts as ground truth; (2) the README's "no dependencies" claim overlooks an
> OEIS network fallback in the reference loader, unused here.

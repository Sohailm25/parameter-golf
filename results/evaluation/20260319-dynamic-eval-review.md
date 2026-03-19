# Dynamic Eval Review - 2026-03-19

## Inputs Reviewed

- `researchdocs/dynamiceval.md`
- official Parameter Golf README
- official PR `#77` (`sliding window + LoRA TTT`)
- official PR `#85` (`autoresearch + sliding window eval`, pending quantized score)
- issue `#67` on validation-set training pressure

## Bottom Line

Dynamic evaluation belongs in this repo, but only in a narrower form than the memo initially suggests.

The strongest repo-safe interpretation is:

1. `document-isolated sliding-window accounting` is the first evaluation lane to verify.
2. `document-reset TTT` is the next evaluation lane after that baseline is clean.
3. `cross-document or repeated-pass held-out adaptation` stays visible, but it is not the default spirit-first path.

## What Holds Up

- The official README explicitly allows aggressive evaluation logic within the separate 10-minute evaluation budget and mentions `test-time training` as a creative direction.
- PR `#77` is direct public evidence that score-before-update, reset-per-document TTT works in this competition family.
- The same PR also shows that the large visible gain comes earlier in the stack:
  - flat stream baseline: `1.2278` BPB
  - `+ doc-isolated`: `1.2168`
  - `+ stride/windowing`: `1.1941`
  - `+ LoRA TTT`: `1.1910`
- That ablation makes the sequencing clear. TTT is not the first thing to test.
- The memo's literature review is directionally useful on one point in particular: smaller adapted parameter subsets are more plausible than full-model eval-time optimization.

## What Is Overstated Or Needs Proof

- The memo's headline estimate of `3-8%` relative BPB gain is too confident for our repo to treat as planning truth.
- The throughput estimates for "many full dynamic-eval passes within budget" are not yet grounded against the actual challenge code path we will run.
- NNCP-style continual adaptation and other cross-document online-learning ideas are research-interesting, but they are much closer to the rule-edge territory raised in issue `#67`.
- The memo sometimes blends together:
  - document-reset TTT
  - cross-document dynamic evaluation
  - compression-style continual learning

Those are not interchangeable.

## Repo Consequences

- Keep `eval-document-isolated-sliding-window` as its own atomic lane.
- Keep `eval-document-reset-ttt` as a separate atomic lane in the backlog.
- Do not present TTT gains as architecture gains.
- When we prototype TTT, start with:
  - score before update
  - reset between documents
  - a small adapted parameter subset or adapter
  - a comparison against the best clean document-isolated sliding-window baseline

## Immediate Experiment Guidance

The first evaluation experiment order should be:

1. flat-stream baseline versus document-isolated evaluation
2. add sliding-window accounting
3. only then add document-reset TTT

The first TTT prototype should stay narrow. A small adapter or limited MLP subset is a better default than "update everything with Adam and hope."

# Competition Policy

This repo keeps two explicit lanes.

## Spirit-First Lane

Use this as the default.

- baseline-faithful training
- architecture changes
- optimizer and schedule changes
- tokenizer work with careful BPB verification
- mixed precision and compression
- longer context and sliding-window evaluation with clear accounting
- document-reset TTT or dynamic evaluation that is score-before-update, document-local, reset correctly, and clearly described

## Open-Rules Lane

Keep this visible but separate.

- anything that leans heavily on public-validation adaptation
- cross-document or repeated-pass held-out adaptation during evaluation
- techniques that appear organizer-allowed but challenge-spirit-sensitive
- experiments whose score gains depend more on evaluation protocol than on general model quality

## Required Documentation For Risky Evaluation Ideas

If a run uses aggressive evaluation logic, write down:

1. what parameters or adapters are updated
2. what state is reset and when
3. whether adaptation crosses document boundaries
4. whether the method is `document-reset TTT` or a more aggressive `cross-document dynamic-eval` regime
5. whether the same method would generalize to a hidden held-out split

If that explanation is weak, the result does not belong in the default golden set.

# TODO

## Open

- [ ] **Explain the correspondence between a trajectory $\tau$ and its terminal state $S(\tau)$ better.** Make it clearer that a trajectory builds a discrete structure step by step and that its terminal state is the object we actually care about.
- [ ] **2nd tutorial example should additionally demonstrate off-policy sampling.** Target is Demo 2 (graph inference) in the notebook — it currently loads a pre-trained on-policy model; add an off-policy proposal demonstration. Deck now orders Demo 1 → Off-policy → Scoreboard → … → Demo 2, so Demo 2 is the natural place to show it.
- [ ] **Slide 6 (introducing GReinSS) has very messy $\tau$ and brace placement, plus assorted ugly alignment issues.** Clean up the trajectory/brace diagram and overall alignment. *(Was "Slide 7" — renumbered after the "GReinSS idea" divider slide was removed.)*

## Done

- [x] **Better motivation of previous work.** (2026-07-07) Reworked *"Why the usual tools struggle"* (slide 4) into four labeled families — Exact inference / Variational / Search / RL — and wove in **HMMs** as the tractable-E-step contrast for EM. Added an explicit **GFlowNets vs. GReinSS** contrast (sample ∝ a fixed reward vs. a dynamically-rescaled reward that provably equals MLE) on both slide 4 and the scoreboard, and aligned the scoreboard's "Family" column to match slide 4.

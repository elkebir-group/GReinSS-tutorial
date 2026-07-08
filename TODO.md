# TODO

## Open

- [ ] **Explain the correspondence between a trajectory $\tau$ and its terminal state $S(\tau)$ better.** Make it clearer that a trajectory builds a discrete structure step by step and that its terminal state is the object we actually care about.
- [ ] **Slide 6 (introducing GReinSS) has very messy $\tau$ and brace placement, plus assorted ugly alignment issues.** Clean up the trajectory/brace diagram and overall alignment. *(Was "Slide 7" — renumbered after the "GReinSS idea" divider slide was removed.)*

## Done

- [x] **2nd tutorial example demonstrates off-policy sampling.** (2026-07-08) Resolved differently than first planned: rather than bolting off-policy onto the graph demo, the notebook gained a dedicated **Demo 2 — Scaling up** (same set problem at $|\mathcal U|=1000$) where the on-policy recipe *collapses* below thresholding and the observation-biased off-policy proposal ($(X_{ij}-\tfrac12)/\sigma^2$, Theorem 2) rescues it (F1 ≈ 0.94). The graph demo became **Demo 3**. Deck synced: added a `→ NOTEBOOK · Demo 2` handoff after the off-policy theory slide and renumbered the graph handoff to Demo 3.

- [x] **Better motivation of previous work.** (2026-07-07) Reworked *"Why the usual tools struggle"* (slide 4) into four labeled families — Exact inference / Variational / Search / RL — and wove in **HMMs** as the tractable-E-step contrast for EM. Added an explicit **GFlowNets vs. GReinSS** contrast (sample ∝ a fixed reward vs. a dynamically-rescaled reward that provably equals MLE) on both slide 4 and the scoreboard, and aligned the scoreboard's "Family" column to match slide 4.

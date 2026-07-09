# TODO

## Open

_(none)_

## Done

- [x] **Explain the correspondence between a trajectory $\tau$ and its terminal state $S(\tau)$ better.** (2026-07-09) Now covered across three slides: the RL primer (slide 5) draws $\tau$ as a step-by-step chain $s_0\to\cdots\to s_{\lvert\tau\rvert}$ with the terminal state highlighted; slide 6's trajectory row reads "same, terminal $S(\tau)$" beside build-up diagrams; and the new **policy-network slide (slide 11)** makes it explicit — `add element j` vs. `stop → S(τ)`, "autoregressive — grow the set, repeat", and $\Pr(S\mid\theta)=\sum_{\tau:\,S(\tau)=S}\prod_t\pi_\theta(a_t\mid s_t)$. Also added a one-line KaTeX caption under slide 6's build-up diagram: "Each action extends $\tau$; we infer its terminal state $S(\tau)$."
- [x] **Slide 6 (introducing GReinSS) had very messy $\tau$ and brace placement, plus alignment issues.** (2026-07-09) Resolved via the isolated `graph-buildup.svg` include (commit `8e616c9`): slide 6 now renders two clean purple $\tau$ braces around the graph and diploid/CNA build-ups with tidy labels and aligned columns.

- [x] **2nd tutorial example demonstrates off-policy sampling.** (2026-07-08) Resolved differently than first planned: rather than bolting off-policy onto the graph demo, the notebook gained a dedicated **Demo 2 — Scaling up** (same set problem at $|\mathcal U|=1000$) where the on-policy recipe *collapses* below thresholding and the observation-biased off-policy proposal ($(X_{ij}-\tfrac12)/\sigma^2$, Theorem 2) rescues it (F1 ≈ 0.94). The graph demo became **Demo 3**. Deck synced: added a `→ NOTEBOOK · Demo 2` handoff after the off-policy theory slide and renumbered the graph handoff to Demo 3.

- [x] **Better motivation of previous work.** (2026-07-07) Reworked *"Why the usual tools struggle"* (slide 4) into four labeled families — Exact inference / Variational / Search / RL — and wove in **HMMs** as the tractable-E-step contrast for EM. Added an explicit **GFlowNets vs. GReinSS** contrast (sample ∝ a fixed reward vs. a dynamically-rescaled reward that provably equals MLE) on both slide 4 and the scoreboard, and aligned the scoreboard's "Family" column to match slide 4.

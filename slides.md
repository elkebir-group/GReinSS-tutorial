---
marp: true
theme: greinss
title: "GReinSS: Generative Reinforcement Learning of Structured States via Dynamic Policy Gradients"
author: "Mohammed El-Kebir"
math: katex
paginate: true
---

<!--
GReinSS tutorial — NCI Spring School on Algorithmic Cancer Biology
Speaker notes are in HTML comments like this one.
Live-demo hand-offs are marked "→ NOTEBOOK".
-->

<!-- _class: title -->
<!-- _paginate: false -->

<!-- Laser pointer: replace the mouse arrow with a red dot on every slide of the interactive deck (just preview / marp --html). No effect in the PDF/PNG exports (static images have no cursor). -->
<style>
section, section * {
  cursor: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"><defs><radialGradient id="g" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="rgb(255,200,180)"/><stop offset="0.35" stop-color="rgb(255,45,25)"/><stop offset="0.7" stop-color="rgb(230,0,0)" stop-opacity="0.45"/><stop offset="1" stop-color="rgb(220,0,0)" stop-opacity="0"/></radialGradient><filter id="b"><feGaussianBlur stdDeviation="1.6"/></filter></defs><circle cx="16" cy="16" r="11" fill="rgb(255,25,10)" fill-opacity="0.5" filter="url(%23b)"/><circle cx="16" cy="16" r="6" fill="url(%23g)"/></svg>') 16 16, pointer;
}
</style>

# GReinSS

## Generative Modeling of Discrete Latent Structures via Dynamic Policy Gradients

<br>

Stefan Ivanovic and **Mohammed El-Kebir**
University of Illinois Urbana-Champaign

<br>

<span class="small">NCI Spring School on Algorithmic Cancer Biology — Tutorial</span>

<span class="small">Ivanovic et al., ICML 2026</span>

<!--
* Hands-on tutorial on GReinSS.
* Problem: infer hidden combinatorial states from noisy, indirect measurements.
* Plan: idea → theorem → live training.
* Goal: apply it to your own problem.
-->

---

## A recurring statistical inference problem in computational biology

<style scoped>
.setup { margin-bottom: 0; }
blockquote { margin: 24px 0; }
.cols3 .exfig { height: 56px; margin: 8px auto; overflow: visible; }
.cols3 .exfig img { max-height: 56px !important; height: auto !important; width: auto !important; }
</style>

<div class="cols3 setup">
<div class="box center">

**States** $S_{1:N} \sim \Pr^*(\mathcal{S})$

<div class="sfig">

![h:76](assets/state-space.png)

</div>

</div>
<div class="box center">

**Measurements** $X_{1:N}$ generated from $S_{1:N}$

<div class="sfig">

![h:40](assets/observation-curve.png)

</div>

</div>
<div class="box center">

$\mathcal{S}$ is typically **large and combinatorial** — graphs, strings, sets, …

<div class="sfig">

![h:40](assets/state-graph.png)

</div>

</div>
</div>

> Rather than directly observing the latent **state** $S$ we care about, we observe some indirect **measurement** $X$ generated from it.

<div class="cols3">
<div class="box center">

### Phylogenies

<div class="exfig">

![w:100](assets/ex-phylo.png)

</div>

**State:** tumor evolution tree
**Measurement:** DNA-seq

<span class="cite">[Ivanovic & El-Kebir, RECOMB/Genome Res. 2023]</span>

</div>
<div class="box center">

### CNA profiles

<div class="exfig">

![w:160](assets/ex-cna.png)

</div>

**State:** copy-number profile
**Measurement:** read depth + BAF

<span class="cite">[Ivanovic & El-Kebir, Genome Biol. 2025]</span>

</div>
<div class="box center">

### RNA isoforms

<div class="exfig">

![w:195](assets/ex-isoform.png)

</div>

**State:** spliced transcript
**Measurement:** aligned short reads

<span class="cite">[Ivanovic et al., ICML 2026]</span>

</div>
</div>

<!--
* Pattern: hidden structure S, indirect obs X, known likelihood Pr(X|S).
* Trees, CNA sets, isoforms — all fit.
* Self-supervised: measurement known, state unknown.
-->

---

## A learning and an inference problem

<div class="cols3 setup">
<div class="box center">

**Approximate** $\Pr^*(S)$ as $\Pr(S\mid\theta)$

<div class="s3fig">

![h:150](assets/hist-model.png)

</div>

</div>
<div class="box center">

**Parameters** $\theta$: a linear map or neural network

<div class="s3fig">

<!-- include: assets/svg/theta-network.svg -->

</div>

</div>
<div class="box center">

**Generative model** with given $\Pr(X\mid S)$

<div class="platebox">

<!-- include: assets/svg/plate-generative.svg -->

<span class="emit"><img src="assets/state-graph.png"><span class="arw">&#8594;</span><img src="assets/observation-curve.png"></span>

</div>

</div>
</div>

<div class="problem">

**Problem 1 (Learning).** *Given (i) $X_{1:N}$ and (ii) $\Pr(X\mid S)$, find $\theta$ maximizing ${\Pr(X_{1:N}\mid\theta)=\prod_i \Pr(X_i\mid\theta})$, where $\Pr(X_i\mid\theta)=\sum_{S}\Pr(X_i\mid S)\,\Pr(S\mid\theta)$*

</div>

<div class="problem">

**Problem 2 (Inference).** *Given (i) $X_{1:N}$, (ii) $\Pr(X\mid S)$, and (iii) $\theta$, find $\hat{S}_{1:N}$, where ${\hat S_i=\arg\max_S \Pr(X_i\mid S)\,\Pr(S\mid\theta)}$*

</div>

<!--
* Model Pr(S|θ); each S* emits an X.
* Problem 1: LEARN θ jointly (shared model couples observations).
* Problem 2: INFER best state per observation.
* Everything today serves these two.
-->

---

## Existing techniques

<style scoped>
table { table-layout: fixed; width: 1148px; font-size: 22px; border-collapse: collapse; margin: 16px auto 0; }
th, td { box-sizing: border-box; }
th:nth-child(1), td:nth-child(1) { width: 168px; }
th:nth-child(2), td:nth-child(2) { width: 300px; }
th:nth-child(3), td:nth-child(3) { width: 680px; }
td.fam { background: var(--panel); color: var(--ill-blue); font-weight: 700; text-align: center; vertical-align: middle; font-size: 21px; }
tbody tr.grp td { border-top: 3px solid #b9c3d1; }
td.m { font-weight: 700; color: var(--ill-blue); vertical-align: middle; }
td.d { vertical-align: middle; }
blockquote { margin-top: 24px; }
</style>

<table>
<thead>
<tr><th>Family</th><th>Method</th><th>Why it struggles</th></tr>
</thead>
<tbody>
<tr class="grp"><td class="fam">Exact<br>inference</td><td class="m">Expectation–Maximization</td><td class="d">E-step exact only for <strong>special structure</strong> (e.g. <strong>HMMs</strong>) — <strong>intractable</strong> for a combinatorial state space</td></tr>
<tr class="grp"><td class="fam" rowspan="2">Variational</td><td class="m">Variational inference</td><td class="d">maximizes an <em>ELBO</em> bound, not the likelihood — needs a <strong>tractable posterior</strong> over combinatorial states</td></tr>
<tr><td class="m">Variational autoencoders</td><td class="d">learn <em>artificial</em> continuous latents — <strong>not</strong> the mechanistic state you want</td></tr>
<tr class="grp"><td class="fam">Search</td><td class="m">Local search</td><td class="d">ignores the <strong>shared</strong> model across observations</td></tr>
<tr class="grp"><td class="fam" rowspan="2">Reinforcement<br>learning</td><td class="m">Naive policy gradient</td><td class="d">collapses to the single <strong>highest-reward</strong> state</td></tr>
<tr><td class="m">GFlowNets</td><td class="d">aim to <strong>sample in proportion to a fixed reward</strong> — not to maximize a likelihood</td></tr>
</tbody>
</table>

> **Gap:** none of these directly maximize $\Pr(X_{1:N}\mid\theta)$ over a *discrete, combinatorial* state space.

<!--
* Four families: exact, variational, search, RL.
* EM: exact E-step only for special structure (HMMs); combinatorial → intractable.
* VI: bounds the likelihood (ELBO); needs a tractable posterior.
* VAE: latents are artificial ℝ^d, not your state.
* Local search: per-observation, no sharing.
* Naive PG / GFlowNet: closest cousins — fail next.
* All miss the same target: max joint likelihood.
-->

---

## Primer on reinforcement learning (RL) — fixed rewards

> **Key question:** What actions should an agent take to maximize a reward signal? 

<style scoped>
.cols { grid-template-columns: 2.15fr 1fr; margin: 26px 0; }
blockquote { margin-bottom: 6px; }
.key { margin-top: 6px; }
table { table-layout: fixed; width: 435px; margin: 0; font-size: 20px; }
th, td { box-sizing: border-box; }
th:nth-child(1), td:nth-child(1) { width: 150px; }
th:nth-child(2), td:nth-child(2) { width: 285px; }
</style>

<div class="cols">
<div style="display: flex; align-items: center; gap: 14px;">

| Concept | In RL |
|---|---|
| **State** $s_t$ | current situation |
| **Action** $a_t$ | transitions $s_t\to s_{t+1}$ |
| **Policy** $\pi_\theta$ | picks the next action |
| **Trajectory** $\tau$ | path $s_0\to\cdots\to s_{\lvert\tau\rvert}$ |
| **Reward** $r(\tau)$ | scores terminal state |
| **Objective** | $\max_\theta \mathbb{E}_\tau[r(\tau)]$ |

<div style="flex: 1; text-align: center;">

<!-- include: assets/svg/rl-loop.svg -->

</div>

</div>
<div class="center">

<!-- include: assets/svg/rl-trajectory.svg -->

<div class="small" style="margin-top: 2px;">a trajectory &#964;</div>

</div>
</div>

<div class="key">

**Policy gradient (REINFORCE):** $\;\nabla_\theta\,\mathbb{E}_{\tau\sim\Pr(\tau\mid\theta)}[r(\tau)]=\mathbb{E}_\tau\big[r(\tau)\,\nabla_\theta\log\Pr(\tau\mid\theta)\big]$ — *gradient through $\log\Pr(\tau\mid\theta)$ only, not the fixed reward $r(\tau)$.*

</div>

<!--
* Generic episodic RL.
* Policy builds a trajectory; reward scores it; maximize EXPECTED reward.
* Three arrows: sample → score → gradient nudge.
* REINFORCE: weight each log-prob gradient by reward; no gradient through reward.
* Next slides = this loop, new reward.
-->

---

## GReinSS: <u>G</u>enerative <u>Rein</u>forcement Learning of <u>S</u>tructured <u>S</u>tates

> **Policy gradient (REINFORCE):** $\;\nabla_\theta\,\mathbb{E}_{\tau\sim\Pr(\tau\mid\theta)}[r(\tau)]=\mathbb{E}_\tau\big[r(\tau)\,\nabla_\theta\log\Pr(\tau\mid\theta)\big]$

<!--> **Key question:** Can we adapt reward function $r(\tau)$ to optimize data likelihood $\Pr(X_{1:N}\mid \theta)$?-->

<style scoped>
.cols { grid-template-columns: 700px 1fr; margin: 26px 0; }
blockquote { margin-bottom: 6px; }
.key { margin-top: 6px; }
table { table-layout: fixed; width: 685px; margin: 0; font-size: 20px; }
th, td { box-sizing: border-box; padding: 7px 8px; }
th:nth-child(1), td:nth-child(1) { width: 150px; }
th:nth-child(2), td:nth-child(2) { width: 285px; }
th:nth-child(3), td:nth-child(3) { width: 250px; }
</style>

<div class="cols">
<div>

| Concept | In RL | In GReinSS |
|---|---|---|
| **State** $s_t$ | current situation | <span style="color:#8a94a0;font-style:italic">same as RL</span> |
| **Action** $a_t$ | transitions $s_t\to s_{t+1}$ | <span style="color:#8a94a0;font-style:italic">same as RL</span> |
| **Policy** $\pi_\theta$ | picks the next action | <span style="color:#8a94a0;font-style:italic">same as RL</span> |
| **Trajectory** $\tau$ | path $s_0\to\cdots\to s_{\lvert\tau\rvert}$ | <span style="color:#8a94a0;font-style:italic">same, terminal $S(\tau)$</span> |
| **Reward** $r(\tau)$ | scores terminal state | <span style="color:#c0341a;font-weight:600">use $\Pr(X\mid S)$???</span> |
| **Objective** |  $\max_\theta \mathbb{E}_\tau[r(\tau)]$ | <span style="color:#c0341a;font-weight:600">$\max_\theta \log\Pr(X_{1:N}\mid\theta)$</span> |

</div>
<div class="center">

<div style="display: flex; align-items: center; justify-content: center; gap: 12px;">

<!-- include: assets/svg/graph-buildup.svg -->

<!-- include: assets/svg/cna-example.svg -->

</div>
</div>
</div>

<div class="key">

**Key question:** How to set rewards $r(\tau)$ such that ${\nabla_\theta\,\mathbb{E}_{\tau\sim\Pr(\tau\mid\theta)}[r(\tau)]=\mathbb{E}_\tau\big[r(\tau)\,\nabla_\theta\log\Pr(\tau\mid\theta)\big] = \nabla_\theta \log \Pr(X_{1:N} \mid \theta)}$?

</div>

<!--
* Same diagram, re-labeled — machinery unchanged.
* Terminal state S(τ) is the object; policy is a neural net.
* Only new piece: the reward (orange); objective = data log-likelihood.
* Pivot: max expected reward ≡ max likelihood.
* Exact reward → next slide (denominator is the trick).
-->

---

## Dynamic rewards

> Train with a policy gradient using the **dynamically rescaled reward** ${r(\tau)=\sum_{i=1}^{N}\Pr(X_i\mid\tau)/\Pr(X_i\mid\theta)}$

<style scoped>
.eqsplit { justify-content: center; gap: 22px; margin: 30px 0; }
</style>

<div class="eqsplit">
<div class="eqbox gbox">

$$\nabla_\theta\underbrace{\log\Pr(X_{1:N}\mid\theta)}_{\text{log-likelihood}}$$

<span class="lbl">what we optimize</span>

</div>
<div class="eq">=</div>
<div class="eqbox rbox">

$$\underbrace{\mathbb{E}_\tau\!\Big[r(\tau)\,\nabla_\theta\log\Pr(\tau\mid\theta)\Big]}_{\text{policy gradient}}$$

<span class="lbl">how we optimize it</span>

</div>
</div>

<div class="theorem">

**Theorem 1 (Unbiased policy gradient).** *With the dynamically changing reward $r(\tau)=\sum_{i=1}^{N}\Pr(X_i\mid\tau)/\Pr(X_i\mid\theta)$, the policy gradient $\mathbb{E}_\tau\!\big[r(\tau)\,\nabla_\theta\log\Pr(\tau\mid\theta)\big]$ is an unbiased estimator of $\nabla_\theta\log\Pr(X_{1:N}\mid\theta)$.*

</div>

<!--
* What we optimize = how we optimize (policy gradient, rescaled reward).
* Numerator Pr(Xi|τ): how well τ explains Xi.
* Denominator Pr(Xi|θ): total prob of Xi — rescales each obs.
* Theorem 1: unbiased for log-likelihood gradient; reward held constant.
-->

---

## Intuition behind dynamic rewards — why the denominator $\Pr(X_i\mid \theta)$?

<style scoped>
.setup { display: grid; grid-template-columns: auto 1fr; align-items: center; gap: 22px; margin: 2px 0 6px; }
.setup table { margin: 0; font-size: 22px; border-collapse: collapse; }
.setup td, .setup th { border: 1px solid #d0d7e0; padding: 9px 14px; text-align: center; }
.setup th { background: #13294B; color: #fff; }
.tcap { display: block; text-align: center; font-size: 17px; color: #5b6672; margin-bottom: 3px; }
.cols { align-items: stretch; gap: 34px; margin: 2px 0; }
.panel { padding: 6px 14px 8px; border-radius: 12px; border: 2px solid; }
.panel.bad { background: #fdecea; border-color: #e0a99f; }
.panel.good { background: #eaf6ec; border-color: #a9d5b4; }
.chip { text-align: center; font-size: 19px; padding: 4px 10px; border-radius: 8px; margin-top: 6px; }
.chip.bad { background: #f6cec7; color: #a82c15; border: 1px solid #dd9e93; }
.chip.good { background: #c9e7cd; color: #1c6e2f; border: 1px solid #9ccfa6; }
.chip p { margin: 0; }
.rhead { font-size: 24px; font-weight: 700; margin-bottom: 6px; }
.rsub { display: block; font-size: 15px; color: #5b6672; margin-bottom: 2px; min-height: 20px; }
.rnote { font-size: 16px; margin-top: 2px; }
</style>

<div class="setup">
<div>

| $\Pr(X \mid S)$ | $S_1$ | $S_2$ | $S_3$ |
|---|:--:|:--:|:--:|
| $X_1$ | $.5$ | | |
| $X_2$ | | $.3$ | $.2$ |

</div>
<div>

**Example:** Two measurements $X_1$ and $X_2$. States $\mathcal{S} = \{S_1, S_2, S_3\}$. 

**Parameters:** $\theta \equiv (\Pr(S_1\mid\theta), \Pr(S_2\mid\theta), \Pr(S_3\mid\theta))$ 
<!--Policy $\theta\equiv\Pr(\tau\mid\theta)$ over $\tau_1,\tau_2,\tau_3$ ($\tau_j$ builds $S_j$); marginal $\Pr(X_i\mid\theta)=\sum_\tau\Pr(\tau\mid\theta)\,\Pr(X_i\mid\tau)$.-->

**Objective:** $\max_\theta \Pr(X_1, X_2 \mid \theta) = \max_\theta \mathbb{E}_\tau[r(\tau)]$

</div>
</div>


<div class="cols">
<div class="center panel bad">

<span class="rhead">Fixed rewards 
$r(\tau)=\Pr(X_i\mid\tau)$</span>

<!-- include: assets/svg/reward-fixed.svg -->

<div class="rnote">

$\theta^\star=(1,0,0)$:  $\Pr(X_1\mid\theta)=.5,\ \Pr(X_2\mid\theta)=0$

</div>

<div class="chip bad">

$\mathbb{E}_\tau[r]$ is linear in the policy ⇒ all mass on the best, $\tau_1$
$\Pr(X_1,X_2\mid\theta)=.5\times 0=\mathbf 0$ ✗

</div>

</div>
<div class="center panel good">

<span class="rhead">Dynamic rewards 
$r(\tau)=\Pr(X_i\mid\tau)/\Pr(X_i\mid\theta)$</span>

<!-- include: assets/svg/reward-dynamic.svg -->

<div class="rnote">

$\theta^\star=(.5,.5,0)$:  $\Pr(X_1\mid\theta)=.25,\ \Pr(X_2\mid\theta)=.15$

</div>

<div class="chip good">

$\max\mathbb{E}_\tau[r]=\max \Pr(X_1,X_2\mid\theta)$ ⇒ balances $\tau_1,\tau_2$
$\Pr(X_1,X_2\mid\theta)=.25\times.15=0.0375$ ✓

</div>

</div>
</div>

<!--> Reward **shrinks as it succeeds** ⇒ the policy covers *every* observation.-->

<!--
* Bars = Pr(τ|θ); each panel is the θ* its reward selects.
* Fixed reward: linear → all mass on τ1, θ*=(1,0,0); Pr(X2)=0, L=0.
* Dynamic reward: maximizes L; balances τ1,τ2 → θ*=(.5,.5,0), L=.0375.
* Denominator = automatic load-balancing.
* Reproduced numerically in the notebook's final section.
-->

---

## GReinSS training loop

<style scoped>
.cols { align-items: center; margin: 8px 0; }
.key { padding: 8px 20px; }
.key .katex-display { margin: 5px 0; }
ol { font-size: 21px; margin: 6px 0; }
ol li { margin: 5px 0; }
.box { padding: 10px 18px; }
</style>

<div class="cols" style="grid-template-columns: 1.8fr 1fr;">
<div class="key">

The **sample → score → update** cycle of RL, run with a reward that changes as $\theta$ learns:



$$r(\tau)=\sum_{i=1}^{N}\frac{\Pr(X_i\mid\tau)}{\boxed{\Pr(X_i\mid\theta)}}\qquad\Pr(X_i\mid\theta)=\mathbb{E}_{\tau}\big[\Pr(X_i\mid\tau)\big]$$

**Dynamic reward** — the boxed denominator is **re-estimated by sampling** each iteration.

</div>
<div class="center">

<!-- include: assets/svg/training-cycle.svg -->

</div>
</div>

<div class="cols" style="grid-template-columns: 1.35fr 1fr;">
<div>

**Repeat until convergence:**

1. **Sample** a batch $\tau_1,\dots,\tau_M\sim\Pr(\tau\mid\theta)$
2. **Score** each: $\Pr(X_i\mid\tau_j)$
3. **Estimate** $\Pr(X_i\mid\theta)\approx\frac1M\sum_j\Pr(X_i\mid\tau_j)$ &nbsp;<span class="small">*(same batch)*</span>
4. **Reward** $r(\tau_j)=\sum_i\Pr(X_i\mid\tau_j)/\Pr(X_i\mid\theta)$
5. **Policy-gradient** step along $\mathbb{E}_\tau\big[r(\tau)\,\nabla_\theta\log\Pr(\tau\mid\theta)\big]$

</div>
<div class="box">

**You supply only two things:**

- a **generator** for $S$ (action-by-action)
- the likelihood **$\Pr(X\mid S)$**

</div>
</div>

<!--
* RL cycle + our reward: sample → score → update θ.
* New vs vanilla RL: denominator Pr(Xi|θ) re-estimated by sampling each iteration.
* Covered state → bigger denominator → smaller reward (load balancing).
* You supply only: generator for S + likelihood Pr(X|S).
* Notebook: write those two, call train.
-->

---

<!-- _class: demo -->

## → NOTEBOOK · Demo 1: Set reconstruction

<style scoped>
.cols { align-items: start; margin: 12px 0 4px; }
.cartoon { margin: 2px auto 0; text-align: center; }
.cartoon svg { width: 830px; max-width: 100%; height: auto; }
.ccap { font-size: 18px; color: var(--muted); text-align: center; margin: 2px auto 0; max-width: 900px; }
.ccap b { color: var(--ill-blue); font-weight: 700; }
</style>

Recover binary **sets** from noisy real-valued measurements. *Trains live in ~10 s.*

<div class="cols">
<div>

**Problem.** $S^*_i\subseteq\mathcal U$, observe
$X_{i,j}\sim\mathcal N(1,\sigma^2)$ if $j\in S^*_i$, else $\mathcal N(0,\sigma^2)$.

**You'll write:**
```python
def log_pr_x_given_g(state, obs):
    return -0.5*np.sum((obs-state)**2)/sigma**2
```
…then `train_model_off_policy(...)`.

</div>
<div>

**Shared structure:** Each $S^*_i$ = a union of a few reusable **subsets**, so a shared $\Pr(S\mid\theta)$ pools across observations.

**Watch for:**
- median $\log\Pr(X_i\mid\theta)$ climbing to ~0
- recovered sets vs. thresholding the noise
- where the **shared model fixes** noisy bits

</div>
</div>

<div class="cartoon">
<!-- include: assets/svg/set-cartoon.svg -->
</div>

<div class="ccap">

<b><span style="color:#13294B">&#9679;</span> true set $S^*_i$</b> &nbsp; <b><span style="color:#cf2f1c">&#9679;</span> noisy observation $X_i$</b> &nbsp;—&nbsp; rounding at ½ flips the <span style="color:#FF5F05">&#9711;</span> circled elements.
</div>

<!--
* SWITCH TO JUPYTER.
* Load obs → Pr(X|S) one line → build net → train ~200 epochs → infer → vs thresholding.
* Punchline: shared structure denoises, beats per-pixel rounding.
-->

---

## Neural network policy $\pi_\theta$ for the set reconstruction problem

<style scoped>
section { background: #fff4ee; padding-top: 38px; }
.lead blockquote { margin-bottom: 2px; }
.netfig { text-align: center; margin: 2px auto 0; }
.netfig svg { width: 1010px; max-width: 100%; height: auto; }
.cap { text-align: center; }
.cap blockquote { margin-top: 6px; }
</style>

<div class="lead">

> **1-hidden-layer MLP** — `Linear(`$|\mathcal U|\!\to\!64$`)` → LeakyReLU → `Linear(`$64\!\to\!|\mathcal U|{+}1$`)` — run once **per step**: read the partial set, then **add an element** or **stop**.

</div>

<div class="netfig">

<!-- include: assets/svg/set-net-cartoon.svg -->

</div>

<div class="cap">

> $|\mathcal U|$ add-logits **+ one stop**; weights **shared across steps**. 
> Illegal (already-added) moves masked. &nbsp;$\Pr(S\mid\theta)=\textstyle\sum_{\tau:\,S(\tau)=S}\prod_t \pi_\theta(a_t\mid s_t)$

</div>

<!--
* The "generator" you supply is this small MLP — one hidden layer (64 units).
* Each step: read the current partial set (0/1 vector) → U+1 logits: add element j, or stop.
* Illegal moves (re-adding an element) are masked to -inf before the softmax → π_θ(a_t | s_t).
* No recurrence — same weights every step; the grown set is fed back in (the dashed loop). Rolling out defines Pr(S|θ).
* Keep it on sets; the point is how simple the generator is — the reward does the work.
-->

---

<!-- _class: demo -->

## → NOTEBOOK · Demo 2: Off-policy learning at scale

<style scoped>
.cols { align-items: start; gap: 30px; margin: 12px 0; }
.cols .theorem { margin: 10px 0; }
.cols .theorem .katex-display { margin: 4px 0; }
blockquote { margin: 10px 0 0; }
</style>

<div class="cols">
<div>

With a **larger, dispersed** state space: sampling $\Pr(\tau\mid\theta)$ rarely hits a terminal state $S(\tau)$ explaining any $X_i$, so most trajectories earn no reward and learning stalls.

<!--**Watch for:** on-policy median $F_1$ *below* thresholding · off-policy median $F_1=\mathbf{0.938}$ · the same sets recovered.-->


![w:365](assets/onpolicy-scaling.png)



</div>
<div>

**Off-policy sampling:** If the policy rarely samples states explaining any $X_i$, learning stalls — **sample where the data says to look:**

<div class="theorem">

**Theorem 2 (Optimal off-policy proposal).** *The unbiased, variance-minimizing sampling proposal is $q^\star$:*

$$q^\star(\tau\mid X_{1:N},\theta)=\tfrac1N\textstyle\sum_{i=1}^{N}\Pr(\tau\mid X_i,\theta)$$

$$\Pr(\tau\mid X_i,\theta)=\frac{\Pr(X_i\mid\tau)\,\Pr(\tau\mid\theta)}{\Pr(X_i\mid\theta)}$$

</div>


</div>
</div>


> **$q^\star$ is intractable** → sample a tractable **$q\approx q^\star$** (for sets: favor element $j$ by $(X_{i,j}-\tfrac12)/\sigma^2$), then **reweight** by $\Pr(\tau\mid\theta)/q(\tau)$.

<!--
* Merges off-policy theorem + Demo 2 hand-off.
* Concept: sample toward states that fit each obs (Theorem 2 = optimal, min-variance); importance sampling stays unbiased.
* Biology: domain knowledge proposes candidates (e.g. CNNaive in CNRein).
* SWITCH TO JUPYTER (Demo 2): |U|=1000; on-policy scores WORSE than thresholding (needle in a haystack).
* Off-policy proposal (pre-trained) → sets recovered.
* Thm 2 if asked: sample where the data points, not blindly.
  * Pr(τ|Xi,θ) = Bayes: policy prior reweighted by likelihood.
  * (1/N)Σi: equal effort per observation.
  * Optimal = samples land where the gradient's mass is; unbiased via importance sampling.
  * Intractable → approximate: (Xij−½)/σ² for sets, CNNaive in CNRein.
-->

---

## The off-policy update in full

<style scoped>
h2 { margin-bottom: 6px; }
.katex-display { margin: 2px 0; }
.lead { margin: 4px 0 0; }
</style>

<div class="lead">

**Exact — unbiased for the data log-likelihood gradient, for *any* proposal $q$:**

</div>

$$\nabla_\theta\log\Pr(X_{1:N}\mid\theta)=\mathbb E_{\tau\sim q}\big[\,w(\tau)\,r(\tau)\,\nabla_\theta\log\Pr(\tau\mid\theta)\,\big]$$

$$w(\tau)=\frac{\Pr(\tau\mid\theta)}{q(\tau)}=\prod_t\frac{\pi_\theta(a_t\mid s_t)}{q(a_t\mid s_t)}\qquad r(\tau)=\sum_{i=1}^{N}\frac{\Pr(X_i\mid\tau)}{\Pr(X_i\mid\theta)}$$

<div class="lead">

**Set problem** — pick an observation $i$ uniformly, then bias each step by its log-odds:

</div>

$$q(a_t=\text{add }j\mid s_t)=\operatorname{softmax}_j\!\Big(\log\pi_\theta(\text{add }j\mid s_t)+\tfrac{X_{i,j}-\frac12}{\sigma^2}\Big)$$

<div class="lead">

**Batch estimate** over $\tau_1,\dots,\tau_M\sim q$ &nbsp;<span class="small">(the denominator $\Pr(X_i\mid\theta)$ in $r$ is re-estimated each batch)</span>**:**

</div>

$$\widehat g=\frac1M\sum_{m=1}^{M} w(\tau_m)\,r(\tau_m)\,\nabla_\theta\log\Pr(\tau_m\mid\theta)\qquad \Pr(X_i\mid\theta)\approx\frac1M\sum_{m=1}^{M} w(\tau_m)\,\Pr(X_i\mid\tau_m)$$

<div class="lead">

**On-policy:** $q=\Pr(\tau\mid\theta)\Rightarrow w\equiv1$. &nbsp;**Self-normalize** (divide by $\textstyle\sum_m w(\tau_m)$) to cut variance.

</div>

<!--
* BACKUP slide (skip in 30 min; good for Q&A). Full off-policy estimator.
* w(τ)=Pr(τ|θ)/q(τ): importance weight, product of per-step ratios (free during rollout).
* r(τ): dynamic reward (Thm 1), rescaled by Pr(Xi|θ).
* Pr(Xi|θ): importance-weighted batch average, re-estimated each iteration.
* q=Pr(τ|θ) (w≡1) → collapses to on-policy loop.
* Any q unbiased; Thm 2's q minimizes variance. Self-normalize to cut variance.
-->

---

<!-- _class: demo -->

## → NOTEBOOK · Demo 3: Graph inference (pre-trained)

<style scoped>
.cols { align-items: start; margin: 6px 0 0; }
.cartoon { margin: 0 auto; text-align: center; }
.cartoon img { width: 680px; max-width: 100%; height: auto; }
.ccap { font-size: 18px; color: var(--muted); text-align: center; margin: 2px auto 0; max-width: 960px; }
.ccap b { color: var(--ill-blue); font-weight: 700; }
</style>

Reconstruct latent **directed graphs** from start/end points of $k$ random walks. *Pre-trained.*

<div class="cols">
<div>

**Problem.** $S^*_i$ = directed graph (10 nodes, 90 edges); we see only the $(v,w)$ **endpoints** of $k$ walks. $\Pr(X\mid S)$: shifted-Laplacian.
<!--$(L+I)^{-1}$.-->

**Shared structure:** Each $S^*_i$ = a random **thresholded subgraph** of one **Erdős–Rényi** $(p{=}\tfrac12)$ base graph.

</div>
<div>

**Watch for:**
- training likelihood curve (pre-computed)
- a reconstructed graph $\hat S_i$ vs. true $S^*_i$
- per-graph $F_1$ (median $\approx 0.97$)

</div>
</div>

<div class="cartoon">

![](assets/graph-cartoon.png)

</div>

<div class="ccap">

<b><span style="color:#13294B">&#9679;</span> latent graph $S^*_i$</b> &nbsp; <b><span style="color:#FF5F05">&#9679;</span> GReinSS $\hat S_i$</b> &nbsp;—&nbsp; dashed = observed (start→end); paths never seen.
</div>

<!--
* SWITCH TO JUPYTER (Demo 3). Pre-trained checkpoint (heavier model).
* Load model → simpleInference → compare to ground truth → F1 + visualize.
* Ground truth: Erdős–Rényi base (p=½), per-graph thresholded subgraph → shared structure.
* Obs = (start,end) of k random walks; Pr(X|S) = shifted-Laplacian (L+I)^{-1}.
* Cartoon = 6 nodes; real = 10 nodes / 90 edges.
-->

---

## Simulation results from [Ivanovic et al. ICML 2026]

<style scoped>
section { padding: 56px 64px 14px; }
h2 { margin-bottom: 6px; }
.cols { align-items: start; gap: 34px; margin: 2px 0 0; }
.cols .center img { display: block; margin: 4px auto 2px; }
.cols .small { font-size: 17px; }
table { font-size: 23px; margin: 10px auto 0; border-collapse: collapse; }
table th, table td { padding: 5px 18px; white-space: nowrap; }
</style>

<div class="cols">
<div class="center">

**Latent sets** — noisy measurements
![h:242](assets/simSet-1.png)

</div>
<div class="center">

**Latent graphs** — walk endpoints
![h:242](assets/simGraph-1.png)

</div>
</div>

| Method | Family | Max. $\prod_i\Pr(X_i\mid\theta)$? |
|---|---|---|
| **GReinSS** | RL | ✅ |
| Naive policy gradient | RL | ❌ |
| GFlowNets | RL | ❌ |
| VAE / autoregressive / diffusion **+ EM** | Variational + EM | ≈ |
| Local search | Search | ❌ |

<!--
* Same four families, scored on: maximizes joint likelihood? Only GReinSS.
* GFlowNets: sample ∝ FIXED reward; we rescale every iteration (Thm 1) → equals data log-likelihood.
* Two state types, one method.
* Sets: only GReinSS scales to |U|=1000; baselines plateau.
* Graphs: GReinSS wins when data is poor (k=10); naive PG → empty graph (F1=0).
-->

---

## Conclusion

<style scoped>
section { padding: 56px 64px 16px; }
.cols3 { margin: 2px 0 6px; }
.cols3 .box { padding: 2px 12px; font-size: 18px; }
.cols3 svg { max-height: 88px; height: auto; }
.s3fig { padding-top: 0; }
.cols { margin: 2px 0; }
.key { padding: 8px 20px; margin-top: 6px; }
</style>

<div class="cols3 setup">
<div class="box center">

**States** $S_{1:N} \sim \Pr^*(\mathcal{S})$

<div class="sfig">

![h:76](assets/state-space.png)

</div>

</div>
<div class="box center">

**Measurements** $X_{1:N}$ generated from $S_{1:N}$

<div class="sfig">

![h:40](assets/observation-curve.png)

</div>

</div>
<div class="box center">

$\mathcal{S}$ is typically **large and combinatorial** — graphs, strings, sets, …

<div class="sfig">

![h:40](assets/state-graph.png)

</div>

</div>
</div>

<div class="cols">
<div>

**Good fit ✓**
- latent state is **discrete / combinatorial**
- you can **generate** it incrementally
- you know (or can compute) **$\Pr(X\mid S)$**
- observations are **indirect** & shared structure exists

</div>
<div>

**Reach elsewhere ✗**
- continuous latents → VAE / diffusion
- tractable exact E-step → classic EM
- rewards truly fixed & known → standard RL / GFlowNet

</div>
</div>

<div class="key">

**Recipe:** ① write a generator for $S$ · ② write $\Pr(X\mid S)$ · ③ `train_model_off_policy` · 
④ `simpleInference`. *(optional)* add an off-policy proposal for hard instances.

</div>

<!--
* Two requirements: incremental generator + likelihood.
* Have those? Four-line recipe — as in the notebook.
-->

---

<!-- _class: title -->
<!-- _paginate: false -->

# Thank you — let's build

**Code + notebook:** `code/README.md`, `tutorial/GReinSS_demo.ipynb`
**Recipe:** generator for $S$ + likelihood $\Pr(X\mid S)$ → train → infer

<br>

<span class="small">Questions? · melkebir@illinois.edu</span>

<!--
* One reward formula, clean theorem.
* Beats standard tools on simulations and real isoform data.
* Drop-in for discrete latent-state problems in cancer genomics.
* Try it on your own Pr(X|S).
-->

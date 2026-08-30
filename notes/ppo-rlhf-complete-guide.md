# PPO and RLHF: A Complete, Detailed Guide

Companion notes for CME 295 (Transformers & Large Language Models), Lecture 5:
Preference Tuning — Data Collection, RLHF, DPO.

These notes are deliberately exhaustive. Every symbol is defined, every statistical
concept used anywhere in the pipeline is explained from first principles, and every
mathematical statement is typeset so it renders as math rather than as text.

> **Rendering note.** Math is written in GitHub-flavoured LaTeX (`$...$` inline,
> `$$...$$` display), which GitHub renders natively in Markdown. Pseudocode, numeric
> traces, tables, and diagrams remain in monospace blocks, where alignment carries
> the meaning.

---

## Table of Contents

**Part 0 — Notation**
- [0.1 Symbols used throughout](#01-symbols-used-throughout)
- [0.2 Reading conventions](#02-reading-conventions)

**Part I — Statistical Foundations**
- [1.1 Random variables and distributions](#11-random-variables-and-distributions)
- [1.2 The categorical distribution](#12-the-categorical-distribution)
- [1.3 Expectation](#13-expectation)
- [1.4 Variance and standard deviation](#14-variance-and-standard-deviation)
- [1.5 Bernoulli and binomial](#15-bernoulli-and-binomial-the-60-out-of-100-question)
- [1.6 The law of large numbers](#16-the-law-of-large-numbers)
- [1.7 Monte Carlo estimation](#17-monte-carlo-estimation)
- [1.8 Bias, variance, and estimators](#18-bias-variance-and-estimators)
- [1.9 Conditional probability and the chain rule](#19-conditional-probability-and-the-chain-rule)
- [1.10 Softmax and temperature](#110-softmax-and-temperature)
- [1.11 Log probabilities and why we use them](#111-log-probabilities-and-why-we-use-them)
- [1.12 How to actually sample: inverse CDF and Gumbel-max](#112-how-to-actually-sample-inverse-cdf-and-gumbel-max)
- [1.13 Truncated sampling: top-k and top-p](#113-truncated-sampling-top-k-and-top-p)
- [1.14 Entropy](#114-entropy)
- [1.15 KL divergence](#115-kl-divergence)
- [1.16 Importance sampling](#116-importance-sampling)
- [1.17 The score function estimator (REINFORCE)](#117-the-score-function-estimator-reinforce)
- [1.18 Baselines and variance reduction](#118-baselines-and-variance-reduction)
- [1.19 Maximum likelihood estimation](#119-maximum-likelihood-estimation)
- [1.20 Sigmoid, logits, and the Bradley-Terry model](#120-sigmoid-logits-and-the-bradley-terry-model)
- [1.21 Standardization (whitening)](#121-standardization-whitening)
- [1.22 Goodhart's law and overoptimization](#122-goodharts-law-and-overoptimization)

**Part II — Reinforcement Learning Formulation**
- [2.1 The MDP](#21-the-mdp)
- [2.2 Mapping an LLM onto the MDP](#22-mapping-an-llm-onto-the-mdp)
- [2.3 Trajectories and returns](#23-trajectories-and-returns)
- [2.4 Discounting](#24-discounting)
- [2.5 Value, Q, and advantage](#25-value-q-and-advantage)
- [2.6 TD error and bootstrapping](#26-td-error-and-bootstrapping)
- [2.7 Generalized Advantage Estimation](#27-generalized-advantage-estimation-gae)
- [2.8 On-policy vs off-policy](#28-on-policy-vs-off-policy)

**Part III — The RLHF Pipeline**
- [3.1 Where preference tuning sits](#31-where-preference-tuning-sits)
- [3.2 Why preferences instead of more SFT](#32-why-preferences-instead-of-more-sft)
- [3.3 Preference data collection](#33-preference-data-collection)
- [3.4 Stage 1: reward modeling](#34-stage-1-reward-modeling)
- [3.5 Stage 2: the RL objective](#35-stage-2-the-rl-objective)

**Part IV — PPO, Step by Step**
- [4.1 The four models](#41-the-four-models)
- [4.2 The three policies](#42-the-three-policies)
- [4.3 Step 1: rollout](#43-step-1-rollout-generation)
- [4.4 Step 2: scoring](#44-step-2-scoring)
- [4.5 Step 3: per-token reward construction](#45-step-3-per-token-reward-construction)
- [4.6 Step 4: advantage estimation](#46-step-4-advantage-estimation)
- [4.7 Step 5: the probability ratio](#47-step-5-the-probability-ratio)
- [4.8 Step 6: clipping](#48-step-6-clipping-the-heart-of-ppo)
- [4.9 Step 7: the value loss](#49-step-7-the-value-loss)
- [4.10 Step 8: entropy bonus and total loss](#410-step-8-entropy-bonus-and-total-loss)
- [4.11 Step 9: the optimizer step](#411-step-9-the-optimizer-step)
- [4.12 The complete loop in pseudocode](#412-the-complete-loop-in-pseudocode)
- [4.13 Hyperparameters](#413-hyperparameters)

**Part V — Implementation Details That Matter**
- [5.1 Loss masking](#51-loss-masking)
- [5.2 Advantage whitening](#52-advantage-whitening)
- [5.3 KL estimators](#53-kl-estimators)
- [5.4 Adaptive KL control](#54-adaptive-kl-control)
- [5.5 Value function clipping](#55-value-function-clipping)
- [5.6 The generation/training mismatch bug](#56-the-generationtraining-mismatch-bug)
- [5.7 Reward normalization](#57-reward-normalization)
- [5.8 EOS, truncation, and length](#58-eos-truncation-and-length)
- [5.9 What to monitor](#59-what-to-monitor)

**Part VI — Failure Modes**

**Part VII — Alternatives to PPO**

**Part VIII — Fully Worked Numerical Example**

**Part IX — Glossary**

**Part X — Open Questions (Question Bank)**

---

# Part 0 — Notation

## 0.1 Symbols used throughout

| Symbol | Meaning |
|---|---|
| $x$ | a prompt (sequence of input tokens) |
| $y$ | a response / completion (sequence of generated tokens) |
| $y_t$ | the $t$-th token of the response |
| $y_{<t}$ | all response tokens before position $t$ |
| $L = \lvert y \rvert$ | number of tokens in the response; the final index |
| $V$ | vocabulary size (e.g. $\approx 128{,}000$) |
| $T$ | sampling temperature |
| $\mathcal{D}$ | the dataset of prompts |
| $\theta$ | trainable parameters of the policy |
| $\phi$ | trainable parameters of the value model |
| $\pi_\theta(y \mid x)$ | the policy: probability of the full response $y$ given prompt $x$ |
| $\pi_\theta(y_t \mid x, y_{<t})$ | the policy: probability of a single next token |
| $\pi_{\theta_{\text{old}}}$ | snapshot of the policy at generation time |
| $\pi_{\text{ref}}$ | frozen reference model (the SFT checkpoint) |
| $r(x, y)$ | the reward model's scalar score for a complete pair |
| $R_t$ | the per-token reward used by the RL algorithm at position $t$ |
| $V_\phi(s_t)$ | the value model's prediction at state $s_t$ |
| $\hat{A}_t$ | the estimated advantage at position $t$ |
| $\delta_t$ | the temporal-difference (TD) error at position $t$ |
| $\rho_t$ | the probability ratio $\pi_\theta / \pi_{\theta_{\text{old}}}$ at position $t$ |
| $\beta$ | KL penalty coefficient |
| $\epsilon$ | PPO clipping parameter (commonly $0.2$) |
| $\gamma$ | discount factor |
| $\lambda$ | GAE smoothing parameter |
| $c_1, c_2$ | loss weights for the value term and entropy term |
| $y_w$ | the preferred ("winning") response in a preference pair |
| $y_l$ | the dispreferred ("losing") response in a preference pair |
| $\mathbb{E}[\cdot]$ | expectation (average) |
| $\operatorname{Var}[\cdot]$ | variance |
| $\sigma(z)$ | the sigmoid $1/(1 + e^{-z})$ |
| $\mathbf{1}[\,\cdot\,]$ | indicator: $1$ if the condition holds, else $0$ |
| $\ell_i$ | the raw logit for vocabulary item $i$ |

A note on one collision: the literature uses $T$ for both temperature and the final
timestep. These notes use $T$ for temperature only, and $L$ for sequence length, so
positions run $t = 1, \ldots, L$.

## 0.2 Reading conventions

- $\sim$ means "is distributed as" / "is sampled from". So $y \sim \pi_\theta(\cdot \mid x)$
  reads "$y$ is sampled from the distribution $\pi_\theta$ conditioned on $x$".
- The dot in $\pi_\theta(\cdot \mid x)$ marks the slot that varies.
  $\pi_\theta(\cdot \mid x)$ is the **whole distribution**; $\pi_\theta(y \mid x)$ is a
  **single number**, the probability of one specific $y$.
- $:=$ means assignment (as in code), not equality.
- $\log$ is the natural logarithm throughout.

That second bullet matters more than it looks. The expression $\pi_\theta(y \mid x)$
does double duty in PPO: as a *distribution* you sample from, and as a *number* you
compute gradients of. Most confusion about the objective traces back to conflating
those two uses.

---

# Part I — Statistical Foundations

This part assumes no probability background and builds up everything PPO needs.

## 1.1 Random variables and distributions

A **random variable** is a quantity whose value is not determined until it is
observed. A **distribution** describes how likely each possible value is.

For our purposes everything is **discrete**: the next token is one of $V$ choices. A
discrete distribution is fully described by a list of probabilities, one per outcome,
satisfying two rules:

$$p_i \ge 0 \quad \text{for every } i, \qquad\qquad \sum_{i=1}^{V} p_i = 1$$

The first rule says probabilities cannot be negative. The second, called
**normalization**, says something must happen. Anything violating either is not a
distribution.

**Why this matters for LLMs.** A language model's final layer produces $V$ real
numbers called **logits** $\ell_i$, which are unconstrained — they can be negative,
large, anything. They are *not* a distribution. The softmax function (Section 1.10) is
what converts them into one.

## 1.2 The categorical distribution

The **categorical distribution** is the distribution over a finite set of unordered
outcomes. It is the single most important distribution in this document, because *a
language model is a categorical distribution generator*. At every token position the
model outputs one categorical distribution over the vocabulary:

$$\text{Categorical}(p_1, p_2, \ldots, p_V)$$

Example over a toy four-token vocabulary:

| token | probability |
|---|---|
| `" the"` | 0.60 |
| `" a"` | 0.25 |
| `" this"` | 0.10 |
| `" xyzzy"` | 0.05 |
| **total** | **1.00** |

Nothing about the ordering matters. There is no notion of one token being "close to"
another in this distribution — that structure lives in the embeddings, not here.

## 1.3 Expectation

The **expectation** (or expected value, or mean) of a function $f$ of a random
variable is the probability-weighted average of $f$ over all outcomes:

$$\mathbb{E}_{i \sim p}\big[f(i)\big] \;=\; \sum_{i=1}^{V} p_i \, f(i)$$

Read it as: "the average value of $f$, if you drew outcomes according to $p$ forever."

Worked example with the toy vocabulary above, where $f$ assigns a reward to each token:

| token | $p_i$ | $f(i)$ | $p_i f(i)$ |
|---|---|---|---|
| `" the"` | 0.60 | $+1.0$ | $+0.600$ |
| `" a"` | 0.25 | $+0.5$ | $+0.125$ |
| `" this"` | 0.10 | $+2.0$ | $+0.200$ |
| `" xyzzy"` | 0.05 | $-10.0$ | $-0.500$ |
| | | $\mathbb{E}[f] =$ | $\mathbf{0.425}$ |

Note what the expectation does: the terrible token pulls the average down, but only in
proportion to how likely it is. This proportional weighting is the entire logic of the
RLHF objective.

**Three properties used constantly:**

$$
\begin{aligned}
\text{linearity:} && \mathbb{E}[a f + b g] &= a\,\mathbb{E}[f] + b\,\mathbb{E}[g] \\
\text{constants:} && \mathbb{E}[c] &= c \\
\text{tower rule:} && \mathbb{E}_x\big[\mathbb{E}_{y \mid x}[f(x,y)]\big] &= \mathbb{E}_{x,y}[f(x,y)]
\end{aligned}
$$

The tower rule is why the RLHF objective can write a single expectation
$\mathbb{E}_{x \sim \mathcal{D},\, y \sim \pi_\theta}$ even though there are two
sequential sampling steps.

**Where this appears in PPO.** The whole objective is an expectation:

$$\max_{\theta} \;\; \mathbb{E}_{x \sim \mathcal{D},\; y \sim \pi_\theta(\cdot \mid x)} \left[\, r(x,y) \;-\; \beta \log \frac{\pi_\theta(y \mid x)}{\pi_{\text{ref}}(y \mid x)} \,\right]$$

Everything else in this document is machinery for estimating and differentiating that
one expectation.

## 1.4 Variance and standard deviation

**Variance** measures spread — how far outcomes typically fall from the mean:

$$\operatorname{Var}[f] \;=\; \mathbb{E}\big[(f - \mathbb{E}[f])^2\big] \;=\; \mathbb{E}[f^2] - \big(\mathbb{E}[f]\big)^2$$

$$\operatorname{std}[f] \;=\; \sqrt{\operatorname{Var}[f]}$$

The standard deviation is in the same units as $f$, which makes it the interpretable
one.

**Why variance dominates practical RL.** Every gradient in PPO is estimated from a
finite sample, so the gradient is itself a random variable. High variance means it
points in a wildly different direction each batch, and training either crawls or
destabilizes. A large fraction of PPO's design — baselines, advantage normalization,
GAE, clipping — exists to reduce variance. Keep this lens; it explains choices that
otherwise look arbitrary.

## 1.5 Bernoulli and binomial: the "60 out of 100" question

A **Bernoulli** trial is a single yes/no event with success probability $p$:

$$\operatorname{Var}[\text{one Bernoulli trial}] = p(1-p)$$

A **binomial** counts successes in $n$ independent Bernoulli trials:

$$\mathbb{E}[\text{count}] = np, \qquad \operatorname{Var}[\text{count}] = np(1-p), \qquad \operatorname{std}[\text{count}] = \sqrt{np(1-p)}$$

**Applied to token sampling.** If a token has probability $0.6$ and you sample the
same distribution 100 times, how many times does it come up?

$$\mathbb{E}[\text{count}] = 100 \times 0.6 = 60, \qquad \operatorname{std} = \sqrt{100 \times 0.6 \times 0.4} = \sqrt{24} \approx 4.9$$

So you expect **60, plus or minus about 5**. Roughly two thirds of the time you land in
$[55, 65]$, and about 95% of the time in $[50, 70]$. You would essentially never see
exactly 60 as a guarantee.

This is the precise answer to "if we repeat 100 times will it be selected 60 times":
60 is the *expectation*, not the outcome. The spread is real, and it is what provides
exploration in RL.

**Important caveat about LLM generation.** The binomial model above assumes you sample
the *same* distribution $n$ times. That is **not** what happens during generation. In
generation you sample each position **once**, from a *different* distribution each time
(because the context grew). The 60% figure describes the frequency across many
independent *regenerations* of the same prompt, not repeated draws at one position.

**Scaling to full responses.** Suppose at each of 400 positions there is a 0.1% chance
of drawing a genuinely bad token. The probability that a full response contains at
least one is

$$P(\text{at least one}) = 1 - (1 - 0.001)^{400} = 1 - 0.999^{400} \approx 1 - 0.670 = 0.330$$

A one-in-a-thousand per-token failure becomes a one-in-three per-response failure. This
compounding is exactly why truncated sampling (Section 1.13) exists.

## 1.6 The law of large numbers

The **law of large numbers** states that the sample average of independent draws
converges to the true expectation:

$$\frac{1}{N} \sum_{n=1}^{N} f(i_n) \;\longrightarrow\; \mathbb{E}[f] \qquad \text{as } N \to \infty$$

The rate matters. The standard error of the sample mean shrinks as

$$\text{standard error} = \frac{\operatorname{std}[f]}{\sqrt{N}}$$

The $\sqrt{N}$ is unforgiving: to halve your error you need **four times** the samples.
This is the fundamental economics of RLHF. Rollouts are expensive, so buying precision
by brute force gets costly fast — hence the emphasis on variance reduction, which
improves $\operatorname{std}[f]$ instead of $N$.

## 1.7 Monte Carlo estimation

**Monte Carlo estimation** means approximating an expectation by sampling:

$$\mathbb{E}_{y \sim \pi_\theta}\big[f(y)\big] \;\approx\; \frac{1}{N} \sum_{n=1}^{N} f(y_n), \qquad y_n \sim \pi_\theta$$

You cannot compute the RLHF expectation exactly. The sum would range over every
possible response — for a 400-token response over a 128,000-token vocabulary that is
$128000^{400}$ terms, a number with over 2,000 digits. Exact computation is not merely
slow, it is physically impossible.

So instead: **generate a handful of responses and average.** That is what a rollout is.
Sampling is not an approximation chosen for convenience; it is the only way the
objective can be touched at all.

Everything else follows. Because we estimate by sampling, the estimate is noisy.
Because it is noisy, we need variance reduction. Because we sample from the policy we
are changing, we need importance corrections. The entire structure of PPO is downstream
of this one fact.

## 1.8 Bias, variance, and estimators

An **estimator** is a rule for computing a guess of some quantity from data. There are
two ways it can be wrong:

- **Bias** — systematic error: the estimator converges to the *wrong* value even with
  infinite data. Formally, an estimator is **unbiased** if
  $\mathbb{E}[\hat{q}] = q$.
- **Variance** — random error: the estimator is right on average, but any single
  estimate can be far off.

```
                 low variance          high variance
              +--------------------+--------------------+
 low bias     |  ideal             |  correct on        |
              |                    |  average, noisy    |
              +--------------------+--------------------+
 high bias    |  confidently       |  worst case        |
              |  wrong             |                    |
              +--------------------+--------------------+
```

**The bias-variance tradeoff** is that reducing one often increases the other, and the
best total error is frequently at a nonzero amount of bias. This appears in at least
four places in PPO:

| mechanism | unbiased end | biased end |
|---|---|---|
| GAE's $\lambda$ | $\lambda = 1$: unbiased, high variance | $\lambda = 0$: biased, low variance |
| truncated sampling | no truncation | top-$p$ biases the gradient, cuts tail variance |
| clipping | no clip: unbiased | clipping biases, kills ratio variance |
| discounting | $\gamma = 1$ | $\gamma < 1$ biases the objective |

Note the pattern: PPO deliberately accepts bias in several places to control variance.
That is an engineering position, not an oversight.

## 1.9 Conditional probability and the chain rule

**Conditional probability** $P(A \mid B)$ is the probability of $A$ given that $B$ is
known. The **chain rule of probability** decomposes a joint probability into a product
of conditionals:

$$P(a, b, c) = P(a)\,P(b \mid a)\,P(c \mid a, b)$$

**This is what an autoregressive LLM is.** The model never represents the probability
of a whole response directly. It factorizes:

$$\pi_\theta(y \mid x) \;=\; \prod_{t=1}^{L} \pi_\theta\big(y_t \mid x, y_{<t}\big)$$

Written out for a three-token response $y = (y_1, y_2, y_3)$:

$$\pi_\theta(y \mid x) = \pi_\theta(y_1 \mid x)\cdot \pi_\theta(y_2 \mid x, y_1)\cdot \pi_\theta(y_3 \mid x, y_1, y_2)$$

Each factor is one categorical distribution — one forward pass through the network. The
product over positions is the sequence probability.

**Two consequences that matter enormously.**

First, sampling a response is just sampling each factor in order. That is why
generation is a simple loop.

Second, sequence probabilities are astronomically small. A 400-token response with a
typical per-token probability of $0.1$ has

$$\pi_\theta(y \mid x) \approx 0.1^{400} = 10^{-400}$$

which **underflows to exactly zero in float32**, whose smallest normal positive value
is about $10^{-38}$. You cannot represent sequence probabilities numerically. Which
brings us to logs.

## 1.10 Softmax and temperature

The **softmax** converts unconstrained logits into a valid distribution:

$$p_i \;=\; \frac{\exp(\ell_i / T)}{\sum_{j=1}^{V} \exp(\ell_j / T)}$$

It satisfies both distribution rules by construction: $\exp$ is always positive, and
dividing by the sum forces normalization.

**Temperature $T$** rescales the logits before exponentiating, reshaping the
distribution:

| $T$ | effect |
|---|---|
| $T \to 0$ | collapses onto the single largest logit — this *is* greedy decoding |
| $T = 1$ | the model's true, calibrated distribution |
| $T > 1$ | flattens the distribution; the tail gets fatter |
| $T \to \infty$ | approaches uniform over the whole vocabulary |

Concretely, with logits $\ell = (3.0,\; 1.0,\; 0.0)$:

| $T$ | resulting distribution | character |
|---|---|---|
| 0.5 | $(0.980,\; 0.018,\; 0.002)$ | sharp, nearly deterministic |
| 1.0 | $(0.844,\; 0.114,\; 0.042)$ | the model's actual belief |
| 2.0 | $(0.629,\; 0.231,\; 0.140)$ | flattened |
| 5.0 | $(0.451,\; 0.302,\; 0.247)$ | approaching uniform |

A property worth knowing: **softmax is shift-invariant.** Adding a constant $c$ to
every logit changes nothing, because $\exp(\ell_i + c) = e^c \exp(\ell_i)$ and the
$e^c$ cancels between numerator and denominator:

$$\frac{e^{c}\exp(\ell_i)}{\sum_j e^{c}\exp(\ell_j)} = \frac{\exp(\ell_i)}{\sum_j \exp(\ell_j)}$$

Implementations exploit this by subtracting $\max_j \ell_j$ before exponentiating,
which prevents overflow. This is the **log-sum-exp trick**.

**Where temperature matters in PPO.** During rollouts, the temperature you generate
with *defines* the distribution $\pi_\theta$ that the rest of the math refers to. If
you generate at $T = 0.7$ but compute log-probabilities at $T = 1.0$, those are two
different distributions and your gradient is silently wrong. See Section 5.6 — this is
a real and common bug.

## 1.11 Log probabilities and why we use them

Every implementation works with $\log p$, never $p$. Four reasons.

**1. Products become sums.** The chain rule product turns into a sum:

$$\log \pi_\theta(y \mid x) \;=\; \sum_{t=1}^{L} \log \pi_\theta\big(y_t \mid x, y_{<t}\big)$$

Sums are numerically stable and trivially differentiable.

**2. Underflow disappears.** The response that had probability $10^{-400}$:

$$\log\left(10^{-400}\right) = -400 \log 10 \approx -921$$

$-921$ is a perfectly ordinary float. The information is preserved.

**3. Ratios become differences.** Used everywhere in PPO:

$$\frac{p}{q} = \exp\big(\log p - \log q\big)$$

Every ratio and KL term in PPO is computed as a difference of log-probs, exponentiated
only at the end if needed.

**4. Better-conditioned gradients.** The gradient of $\log p$ with respect to the
logits is clean and bounded, whereas the gradient of $p$ itself vanishes for small $p$.

**Sign convention.** Since probabilities lie in $[0,1]$, log-probs lie in
$(-\infty, 0]$. Log-probs are always **negative** (or zero for a certainty). A log-prob
of $-0.2$ is a high probability ($\approx 0.82$); $-10$ is a low one
($\approx 0.000045$).

## 1.12 How to actually sample: inverse CDF and Gumbel-max

Given a categorical distribution, how do you mechanically draw from it?

### Method 1: inverse CDF (what `torch.multinomial` does)

Build the **cumulative distribution function** and use one uniform random number:

$$u \sim \text{Uniform}(0,1), \qquad i^\star = \min\left\{\, i \;:\; \sum_{j=1}^{i} p_j \;\ge\; u \,\right\}$$

In words: draw one random number, walk down the token list adding up probabilities, and
stop at the first token whose running total reaches $u$.

The geometric picture: cut the interval $[0,1]$ into segments, one per token, where each
segment's **width equals that token's probability**. Throw a dart uniformly at $[0,1]$
and take whichever segment it hits.

| token | $p_i$ | cumulative | owns the interval |
|---|---|---|---|
| `" the"` | 0.60 | 0.60 | $[0.00,\, 0.60)$ |
| `" a"` | 0.25 | 0.85 | $[0.60,\, 0.85)$ |
| `" this"` | 0.10 | 0.95 | $[0.85,\, 0.95)$ |
| `" xyzzy"` | 0.05 | 1.00 | $[0.95,\, 1.00)$ |

```
|-------------------------|----------|----|--|
0.0                      0.60      0.85 0.95 1.0
         " the"            " a"   " this" " xyzzy"

u = 0.91  ->  first cumulative >= 0.91 is 0.95  ->  pick " this"
```

**Why it is correct.** The probability that a uniform $u$ lands in a segment equals that
segment's width, and the width was constructed to equal $p_i$. So
$P(\text{select } i) = p_i$ exactly. Width *is* probability.

**Can the least likely token be selected?** Yes. `" xyzzy"` owns $[0.95, 1.00)$, so it
is chosen 5% of the time. Any token with nonzero probability is reachable. A token with
probability $10^{-9}$ owns a segment of that width and appears about once per billion
draws. Proportional selection means bad tokens are picked exactly as often as the model
believes they should be — no more, no less.

### Method 2: Gumbel-max (common on GPUs)

Add independent Gumbel noise to the raw logits and take the argmax:

$$g_i = -\log\big(-\log u_i\big), \quad u_i \sim \text{Uniform}(0,1), \qquad i^\star = \operatorname*{arg\,max}_i \big(\ell_i + g_i\big)$$

This provably yields a sample from the *exact* same categorical distribution as
inverse-CDF sampling. It is attractive because it needs no normalization (no softmax, no
cumulative sum) and vectorizes perfectly across a batch.

### Special case: greedy decoding

$$i^\star = \operatorname*{arg\,max}_i p_i$$

No randomness; equivalent to $T \to 0$. **Not** used for PPO rollouts, because it makes
$y$ a deterministic function of $x$: every rollout of a prompt returns the identical
response, the Monte Carlo estimate collapses onto a single point, exploration vanishes,
and the gradient stops being an unbiased estimate of the objective's gradient.

## 1.13 Truncated sampling: top-k and top-p

Pure sampling can select any token, and over hundreds of positions the tail risk
compounds (Section 1.5). Truncation removes the tail.

**Top-$k$**: keep the $k$ highest-probability tokens, zero the rest, renormalize.

$$p_i \;\leftarrow\; \frac{p_i \cdot \mathbf{1}\big[i \in \text{top-}k\big]}{\sum_{j \in \text{top-}k} p_j}$$

With $k = 2$ on our example: $(0.60, 0.25)$ are kept, so
$p \leftarrow (0.60/0.85,\; 0.25/0.85) = (0.706,\; 0.294)$ and the other two become
exactly zero.

**Top-$p$ (nucleus sampling)**: keep the smallest set $S$ of highest-probability tokens
whose total mass reaches the threshold, then renormalize.

$$S = \text{smallest set with} \sum_{i \in S} p_i \ge p_{\text{thresh}}, \qquad p_i \;\leftarrow\; \frac{p_i \cdot \mathbf{1}[i \in S]}{\sum_{j \in S} p_j}$$

With $p_{\text{thresh}} = 0.9$ on our example:

| token | $p_i$ | cumulative | decision |
|---|---|---|---|
| `" the"` | 0.60 | 0.60 | $< 0.9$, keep and continue |
| `" a"` | 0.25 | 0.85 | $< 0.9$, keep and continue |
| `" this"` | 0.10 | 0.95 | $\ge 0.9$, keep and **stop** |
| `" xyzzy"` | 0.05 | — | discard |

Renormalized: $(0.632,\; 0.263,\; 0.105,\; 0)$.

**The key property.** Both methods set the tail to **exactly zero**, not merely small.
The least likely token becomes genuinely unselectable rather than improbable. This is
the direct answer to the tail-risk problem.

**Why top-$p$ is usually preferred.** It adapts to the model's confidence. After
`"The capital of France is"` the model is confident, the nucleus contains roughly one
token, and sampling is effectively deterministic. After `"Once upon a time, there"` the
model is uncertain, the nucleus spans hundreds of tokens, and you get genuine diversity.
A fixed $k$ cannot do this — it is too permissive when the model is confident and too
restrictive when it is not.

**The catch for PPO.** The objective is an expectation over
$y \sim \pi_\theta(\cdot \mid x)$, meaning the *untruncated* distribution. The moment
you truncate, you sample from a different distribution than the one appearing in the
ratio and KL terms, and the gradient estimator becomes **biased**. Standard practice is
therefore to run PPO rollouts at $T = 1.0$ with little or no truncation, relying on the
SFT initialization to already place negligible mass on garbage.

## 1.14 Entropy

**Entropy** measures the uncertainty of a distribution:

$$H(p) \;=\; -\sum_{i=1}^{V} p_i \log p_i$$

Its bounds are $H = 0$ for a certainty (one token has $p = 1$) and $H = \log V$ for the
uniform distribution. For our toy example:

$$
\begin{aligned}
H &= -\big(0.60 \log 0.60 + 0.25 \log 0.25 + 0.10 \log 0.10 + 0.05 \log 0.05\big) \\
  &= -\big(-0.3066 - 0.3466 - 0.2303 - 0.1500\big) \\
  &= 1.033 \ \text{nats}
\end{aligned}
$$

("nats" because we used the natural log; with $\log_2$ the unit is bits.)

**Why PPO tracks entropy.** Entropy is the early-warning signal for **mode collapse**.
If the policy discovers one response that scores well, it can concentrate all
probability there, driving entropy toward zero. At that point sampling returns the same
text every time, there is no exploration left, and learning stops. The optional
**entropy bonus** in the loss (Section 4.10) adds $+c_2 H$ to reward the policy for
staying uncertain. Falling entropy in your logs is one of the most reliable indicators
that a run is going wrong.

## 1.15 KL divergence

The **Kullback-Leibler divergence** measures how different one distribution is from
another:

$$D_{\text{KL}}(p \parallel q) \;=\; \sum_i p_i \log \frac{p_i}{q_i} \;=\; \mathbb{E}_{i \sim p}\left[\log \frac{p_i}{q_i}\right]$$

Read $D_{\text{KL}}(p \parallel q)$ as "the divergence of $p$ from reference $q$".
Properties:

1. $D_{\text{KL}} \ge 0$ always (Gibbs' inequality).
2. $D_{\text{KL}} = 0$ if and only if $p = q$.
3. **Asymmetric**: $D_{\text{KL}}(p \parallel q) \ne D_{\text{KL}}(q \parallel p)$. It is
   *not* a distance metric.
4. $D_{\text{KL}} = \infty$ if $q_i = 0$ anywhere that $p_i > 0$.

Property 3 is not a technicality — it determines behavior. $D_{\text{KL}}(p \parallel q)$
averages over samples from $p$, so it heavily penalizes $p$ putting mass where $q$ has
little.

**In PPO** we penalize $D_{\text{KL}}(\pi_\theta \parallel \pi_{\text{ref}})$:

$$D_{\text{KL}}\big(\pi_\theta \parallel \pi_{\text{ref}}\big) = \mathbb{E}_{y \sim \pi_\theta}\left[\log \pi_\theta(y \mid x) - \log \pi_{\text{ref}}(y \mid x)\right]$$

The ordering is deliberate. We sample from $\pi_\theta$ (that is what a rollout gives
us), and we want to punish the policy for placing probability on text the reference model
considers unlikely. That is precisely the direction that catches drift into degenerate,
reward-hacked output.

**Sequence-level vs token-level.** In practice this is computed per token and summed,
using the log-prob decomposition:

$$\text{kl}_t = \log \pi_\theta(y_t \mid x, y_{<t}) - \log \pi_{\text{ref}}(y_t \mid x, y_{<t}), \qquad \text{KL} = \sum_{t=1}^{L} \text{kl}_t$$

**Note on terminology.** What PPO computes is a single-sample *estimate* of the KL, not
the full sum over the vocabulary. It is unbiased in expectation but **can be negative
for an individual token**, which surprises people who know $D_{\text{KL}} \ge 0$. The
inequality holds for the true KL, not for a one-sample estimate. Section 5.3 covers
better estimators.

## 1.16 Importance sampling

**The problem it solves:** you want an expectation under distribution $p$, but your
samples came from a different distribution $q$.

**The identity:**

$$
\begin{aligned}
\mathbb{E}_{y \sim p}\big[f(y)\big]
  &= \sum_y p(y) f(y) \\
  &= \sum_y q(y) \frac{p(y)}{q(y)} f(y) \\
  &= \mathbb{E}_{y \sim q}\left[ \frac{p(y)}{q(y)} f(y) \right]
\end{aligned}
$$

The derivation is just multiplying by $q(y)/q(y)$. The factor $p(y)/q(y)$ is the
**importance weight**: it reweights each sample to correct for having drawn from the
wrong distribution. A sample that $q$ overproduces relative to $p$ gets down-weighted,
and vice versa. The requirement is $q(y) > 0$ wherever $p(y) > 0$ — if $q$ can never
produce a sample that $p$ cares about, no reweighting can fix it.

**This is exactly where PPO's ratio comes from.** You generate with
$\pi_{\theta_{\text{old}}}$, then take several gradient steps, so by step two your
samples are stale — they came from $\pi_{\theta_{\text{old}}}$ but you want an
expectation under the current $\pi_\theta$:

$$\mathbb{E}_{y \sim \pi_\theta}\big[\hat{A}\big] \;=\; \mathbb{E}_{y \sim \pi_{\theta_{\text{old}}}}\left[ \underbrace{\frac{\pi_\theta(y \mid x)}{\pi_{\theta_{\text{old}}}(y \mid x)}}_{\textstyle \rho} \; \hat{A} \right]$$

**The catastrophe importance sampling is prone to.** If $p$ and $q$ differ much, the
weights have enormous variance, and a single sample with weight 1000 dominates the entire
batch average:

| $\rho$ | consequence |
|---|---|
| $1.0$ | samples perfectly on-policy, estimate is clean |
| $1.2$ | mild staleness, fine |
| $50$ | one sample dominates the batch, estimate is meaningless |

**And that is the justification for clipping.** PPO bounds the importance weight to
$[1-\epsilon,\, 1+\epsilon]$ and thereby bounds the variance. It introduces bias in
exchange for not blowing up — Section 1.8's tradeoff, made concrete.

## 1.17 The score function estimator (REINFORCE)

We need the gradient of an expectation whose *distribution* depends on the parameters:

$$J(\theta) = \mathbb{E}_{y \sim \pi_\theta}\big[R(y)\big]$$

The difficulty is that you cannot simply push the gradient inside, because $\theta$
controls *which samples you get*, not just the values.

**The derivation** (the "log-derivative trick"):

$$
\begin{aligned}
\nabla_\theta J
  &= \nabla_\theta \sum_y \pi_\theta(y) R(y) \\
  &= \sum_y \big[\nabla_\theta \pi_\theta(y)\big] R(y) \\
  &= \sum_y \pi_\theta(y) \, \frac{\nabla_\theta \pi_\theta(y)}{\pi_\theta(y)} \, R(y) \\
  &= \sum_y \pi_\theta(y) \big[\nabla_\theta \log \pi_\theta(y)\big] R(y) \\
  &= \mathbb{E}_{y \sim \pi_\theta}\Big[ R(y)\, \nabla_\theta \log \pi_\theta(y) \Big]
\end{aligned}
$$

The third line multiplies and divides by $\pi_\theta(y)$; the fourth uses
$\nabla \log f = \nabla f / f$.

**The result — the policy gradient theorem:**

$$\boxed{\;\nabla_\theta J = \mathbb{E}_{y \sim \pi_\theta}\Big[ R(y) \, \nabla_\theta \log \pi_\theta(y) \Big]\;}$$

This is remarkable and worth pausing on. The right-hand side is an expectation you can
estimate by sampling, and $\nabla_\theta \log \pi_\theta$ is just backprop through the
model's own log-probability output. **$R(y)$ need not be differentiable at all** — it can
be a neural reward model, a unit test, or a human. The gradient flows only through the
policy's log-prob.

**Interpretation.** $\nabla_\theta \log \pi_\theta(y)$ is the direction in parameter
space that makes $y$ more likely. Multiplying by $R(y)$:

- $R(y) > 0$: step in that direction, making $y$ **more** likely.
- $R(y) < 0$: step against it, making $y$ **less** likely.

The magnitude of $R$ sets the step size. That is the whole mechanism: **reinforce what
scored well, suppress what scored badly, proportionally.**

**The problem with using this directly.** Its variance is enormous. Consider rewards
that are all positive, say every response scores between $+8$ and $+10$. Then every
gradient term pushes *up* on every sampled response, including the mediocre ones. The
learning signal — that $+10$ beats $+8$ — is a small difference riding on a large common
offset. Which leads directly to baselines.

## 1.18 Baselines and variance reduction

**The key theorem:** subtracting any function $b(x)$ that does not depend on $y$ leaves
the gradient unbiased.

$$\nabla_\theta J = \mathbb{E}\Big[ \big(R(y) - b(x)\big)\, \nabla_\theta \log \pi_\theta(y) \Big]$$

**Why subtracting is free.** Because the score function has zero mean:

$$
\begin{aligned}
\mathbb{E}_{y \sim \pi_\theta}\big[\nabla_\theta \log \pi_\theta(y)\big]
  &= \sum_y \pi_\theta(y)\, \nabla_\theta \log \pi_\theta(y) \\
  &= \sum_y \nabla_\theta \pi_\theta(y) \\
  &= \nabla_\theta \sum_y \pi_\theta(y) \;=\; \nabla_\theta (1) \;=\; 0
\end{aligned}
$$

So $\mathbb{E}\big[b(x) \nabla_\theta \log \pi_\theta\big] = b(x) \cdot 0 = 0$. The
baseline contributes nothing to the expectation — but it can dramatically reduce the
**variance**.

**The intuition, with numbers.** Four responses to one prompt:

| | rewards | effect |
|---|---|---|
| without baseline | $R = (8,\, 9,\, 10,\, 11)$ | every gradient pushes **up**; the useful signal (spread 3) is swamped by the common offset ($\approx 9.5$) |
| with $b = \bar{R} = 9.5$ | $R - b = (-1.5,\, -0.5,\, +0.5,\, +1.5)$ | the two worse responses are pushed **down**, the two better **up**: pure relative signal, much lower variance |

**This is what "advantage" means.** The advantage is reward minus baseline — the
lecture's $\text{Advantage} \approx \text{Reward} - \text{Baseline}$. Two standard
choices:

$$\text{PPO:} \quad b(x) = V_\phi(x) \qquad\qquad\qquad \text{GRPO:} \quad b(x) = \frac{1}{G}\sum_{i=1}^{G} R_i$$

PPO's baseline is a **learned** value model; GRPO's is an **empirical** group mean.
PPO pays for a whole extra trained model to get its baseline. GRPO pays in extra samples
per prompt instead. Same statistical purpose, different cost structure.

## 1.19 Maximum likelihood estimation

**Maximum likelihood estimation (MLE)** picks parameters that make the observed data
most probable:

$$
\begin{aligned}
\hat{\theta} &= \operatorname*{arg\,max}_\theta \prod_n P(\text{data}_n \mid \theta) \\
             &= \operatorname*{arg\,max}_\theta \sum_n \log P(\text{data}_n \mid \theta) \\
             &= \operatorname*{arg\,min}_\theta \; -\sum_n \log P(\text{data}_n \mid \theta)
\end{aligned}
$$

The final line is the **negative log-likelihood** loss.

**Where MLE appears in this pipeline:**

| stage | objective |
|---|---|
| Pretraining / SFT | MLE of next tokens: $\mathcal{L} = -\sum_t \log \pi_\theta(y_t \mid x, y_{<t})$ — exactly cross-entropy |
| Reward modeling | MLE under the Bradley-Terry model (next section) |
| DPO | MLE under an implicitly-defined reward |
| **PPO** | **not MLE** — it maximizes expected reward, not the likelihood of any fixed dataset |

That last row is worth internalizing. SFT asks "make *this specific text* more likely."
PPO asks "make *whatever scores well* more likely," and it has to **discover** what
scores well by generating. That difference is why PPO needs sampling at all.

## 1.20 Sigmoid, logits, and the Bradley-Terry model

The **sigmoid** (logistic) function squashes any real number into $(0,1)$:

$$\sigma(z) = \frac{1}{1 + e^{-z}}$$

with $\sigma(0) = 0.5$, $\sigma(2) \approx 0.881$, $\sigma(-2) \approx 0.119$, and
limits $0$ and $1$ at $\mp\infty$. Useful identities:

$$\sigma(-z) = 1 - \sigma(z), \qquad \frac{d\sigma}{dz} = \sigma(z)\big(1 - \sigma(z)\big), \qquad \log \sigma(z) = -\log\big(1 + e^{-z}\big)$$

The last form is the numerically stable one used in implementations.

**The Bradley-Terry model** (Bradley & Terry, 1952) models pairwise comparisons. Given
two items with real-valued strengths, the probability that the first beats the second
depends only on their *difference*:

$$P\big(y_w \succ y_l \mid x\big) = \frac{\exp r(x, y_w)}{\exp r(x, y_w) + \exp r(x, y_l)} = \sigma\big(r(x, y_w) - r(x, y_l)\big)$$

The second form follows from dividing numerator and denominator by $\exp r(x,y_w)$.

| $r(x,y_w) - r(x,y_l)$ | $P(y_w \succ y_l)$ | reading |
|---|---|---|
| $0$ | $0.50$ | coin flip; the model sees them as equal |
| $+1$ | $0.73$ | mild preference |
| $+2$ | $0.88$ | clear preference |
| $+4$ | $0.98$ | near-certain |

**Consequence: rewards are identified only up to an additive constant.** Since only
differences matter, adding any constant $c$ to every reward leaves all predicted
preferences unchanged. The reward model's absolute scale is arbitrary — $r = 5.0$ means
nothing on its own, only $r(A) - r(B)$ is meaningful. This is why reward normalization
(Section 5.7) is both permissible and necessary.

**The reward model's training loss** is the negative log-likelihood under this model:

$$\mathcal{L}(r) = -\,\mathbb{E}_{(x,\, y_w,\, y_l) \sim \mathcal{D}} \Big[ \log \sigma\big(r(x, y_w) - r(x, y_l)\big) \Big]$$

Minimizing this pushes the score gap in the direction humans preferred. Note it needs
only *which* response was better, never a numeric quality score — the lecture's point
that comparing is easier than generating or absolute rating.

## 1.21 Standardization (whitening)

**Standardizing** (or whitening) a set of numbers shifts and scales them to mean $0$ and
standard deviation $1$:

$$z_i = \frac{a_i - \operatorname{mean}(a)}{\operatorname{std}(a) + \varepsilon}$$

The $\varepsilon$ (e.g. $10^{-8}$) prevents division by zero when all values are
identical.

**Why PPO whitens advantages.** The advantage scale drifts over training as the reward
model's outputs and the value function's accuracy change. Since the advantage multiplies
the gradient, a drifting scale acts like a drifting learning rate. Whitening per batch
pins the effective step size, making a single learning rate work throughout the run.

**The subtlety:** whitening divides by a *sample* standard deviation computed from the
same batch, which technically introduces bias and couples the samples in a batch. In
practice it is such a large stability win that essentially every implementation does it —
another deliberate bias-for-variance trade.

## 1.22 Goodhart's law and overoptimization

**Goodhart's law:** when a measure becomes a target, it ceases to be a good measure.

This is the central statistical hazard of RLHF, and it explains the epoch counts.

The reward model $r$ is a *learned approximation* of true human preference, fit to a
finite dataset (order $10^4$ comparisons). It is accurate in the region where that data
lived — near the SFT model's output distribution — and unreliable elsewhere.

PPO then optimizes against $r$. As the policy moves, it leaves the region where $r$ was
validated and enters territory where $r$ is merely extrapolating. And PPO is an
*optimizer*: it will actively seek out the places where $r$ is highest, which are
disproportionately the places where $r$ is **wrong**.

```
     true quality
          ^
          |        .-''-.                    <- true quality peaks, then falls
          |      .'      `-.
          |    .'            `--.
          |  .'                   `--.
          |.'                          `--.
          +-------------------------------------> KL from reference
                       |
                       |  reward model score keeps climbing this whole time
                       |
                  the divergence point:
                  proxy improves, reality degrades
```

This gap between proxy reward and true quality is called **reward overoptimization**,
and it is why:

1. the objective carries a KL penalty at all;
2. runs use very few epochs (often a single pass over the prompts);
3. practitioners stop on a KL budget rather than a fixed step count;
4. the reward model itself is trained for only **one** epoch (it overfits beyond that).

The KL penalty is best understood as a **trust region on the proxy**: stay close enough
to the reference that the reward model's estimates remain meaningful.

---

# Part II — Reinforcement Learning Formulation

## 2.1 The MDP

Reinforcement learning is formalized as a **Markov Decision Process (MDP)**, defined by
five components:

| component | meaning |
|---|---|
| $\mathcal{S}$ | set of states |
| $\mathcal{A}$ | set of actions |
| $P(s' \mid s, a)$ | transition dynamics: where you land after action $a$ in state $s$ |
| $R(s, a)$ | reward function |
| $\gamma$ | discount factor |

An **agent** observes a state, takes an action according to its **policy**, receives a
reward, and lands in a new state. Repeat. The goal is a policy maximizing cumulative
reward. The "Markov" property means the state contains everything relevant: the future
depends only on the current state, not on the path taken to reach it.

## 2.2 Mapping an LLM onto the MDP

This is the lecture's RL-formulation slide, made precise:

| RL concept | LLM realization |
|---|---|
| agent | the LLM |
| policy | $\pi_\theta$, the model's next-token distribution |
| state $s_t$ | the full context so far: $(x, y_1, \ldots, y_{t-1})$ |
| action $a_t$ | the next token $y_t$ |
| action space | the entire vocabulary ($\approx 128{,}000$ discrete actions) |
| transition | **deterministic**: $s_{t+1} = s_t \,\Vert\, [y_t]$ — append the token |
| reward | the reward model's score, at the **end** of the response |
| episode | one full response, from first token to EOS |
| terminal state | EOS emitted, or max length reached |

**Several features make this a very unusual MDP, and they explain PPO's shape here.**

**1. The transition function is deterministic and trivial.** In robotics
$P(s' \mid s,a)$ is complex and stochastic. Here, taking action $y_t$ in state $s_t$
puts you in $s_t \Vert [y_t]$ with probability $1$. All the stochasticity in the system
comes from the *policy's own sampling*, not from the environment. The "Environment" box
in the lecture's diagram is essentially string concatenation.

**2. The action space is enormous** — $\approx 10^5$ discrete actions per step, versus a
handful in most classic RL benchmarks.

**3. The reward is extremely sparse and delayed.** You emit hundreds of tokens and
receive exactly one scalar at the very end. Every intermediate action gets no direct
feedback. This is the hardest part of the setup, and all of Sections 2.5–2.7 exists to
address it.

**4. Episodes are short and always terminate** — a few hundred to a few thousand steps,
guaranteed to end.

**5. The state is the entire history**, so the Markov property holds trivially: the
context *is* the history.

## 2.3 Trajectories and returns

A **trajectory** is one complete episode:

$$\tau = \big(s_1, a_1, R_1,\; s_2, a_2, R_2,\; \ldots,\; s_L, a_L, R_L\big)$$

For an LLM, one trajectory is one prompt with one sampled response.

The **return** from position $t$ is the total future reward from that point on:

$$G_t = R_t + \gamma R_{t+1} + \gamma^2 R_{t+2} + \cdots = \sum_{k=0}^{L-t} \gamma^k R_{t+k}$$

The objective is to maximize the expected return $\mathbb{E}[G_1]$.

## 2.4 Discounting

The **discount factor** $\gamma \in [0,1]$ down-weights future rewards:

| $\gamma$ | behavior |
|---|---|
| $0$ | completely myopic; only the immediate reward matters |
| $0.99$ | standard in classic RL; rewards $\sim 100$ steps out still count |
| $1.0$ | no discounting; all future rewards weighted equally |

Discounting exists in classic RL for mathematical convergence over infinite horizons and
to model genuine preference for sooner rewards.

**In RLHF, $\gamma = 1.0$ is standard.** This surprises people coming from classic RL,
but the reasoning is sound:

1. Episodes are finite and short, so there is no divergence to prevent.
2. There is no reason to prefer a good token *sooner*. A response is judged as a whole;
   token 300 being good is worth exactly as much as token 3 being good.
3. With a single terminal reward, $\gamma < 1$ would systematically discount the reward
   for early tokens, biasing credit assignment toward the end of the response for no
   principled reason.

So in RLHF you will typically see $\gamma = 1$, and the discounting machinery, while
present in the equations, is inert.

## 2.5 Value, Q, and advantage

Three related functions. Getting these straight is essential.

**The state-value function** — "how good is this position?"

$$V^\pi(s) = \mathbb{E}_\pi\big[G_t \mid s_t = s\big]$$

The expected total future reward from state $s$, if you continue following policy $\pi$.
In LLM terms: given the context so far, how well is this response expected to score once
finished?

**The action-value function** — "how good is this position if I take this specific
action?"

$$Q^\pi(s, a) = \mathbb{E}_\pi\big[G_t \mid s_t = s,\; a_t = a\big]$$

**The advantage function** — "was that action better or worse than average?"

$$A^\pi(s, a) = Q^\pi(s, a) - V^\pi(s)$$

This is the single most important quantity in PPO. It is the lecture's
$\text{Advantage} \approx \text{Reward} - \text{Baseline}$, with $V$ as the baseline.

**Reading the sign is everything:**

| sign | meaning | consequence |
|---|---|---|
| $A > 0$ | this action did **better** than the policy's average from this state | increase its probability |
| $A = 0$ | exactly average | no change |
| $A < 0$ | this action did **worse** than average | decrease its probability |

**Why the advantage rather than the raw return.** Suppose every response to a prompt
scores $+9$. Using raw returns you would push up on all of them equally and learn nothing
about which was better. Subtracting $V$ removes the shared component and leaves only the
*relative* signal — Section 1.18's baseline argument, in RL language.

**About the value model in RLHF specifically.** As the lecture notes, it is:

- **token-level** — it predicts a value at *every* position, not just at the end;
- **policy-dependent** — it answers "what reward if I *follow the policy* from here";
- **trained jointly** — updated alongside the policy, since the policy keeps changing;
- **label = reward** — its regression target is the actual observed return.

The policy-dependence deserves emphasis: $V$ is not a fixed property of the text. It is a
prediction about what *this current policy* would do next. So as the policy improves,
$V$'s targets shift — the value model chases a moving target, which is a major source of
PPO's instability.

Architecturally it is usually the SFT model with the language-modeling head replaced by a
scalar head, producing one number per token position.

## 2.6 TD error and bootstrapping

The **temporal-difference (TD) error** compares a one-step-lookahead estimate against
the current value prediction:

$$\delta_t = \underbrace{R_t + \gamma V(s_{t+1})}_{\text{better estimate of } V(s_t)} - \underbrace{V(s_t)}_{\text{current estimate}}$$

Interpretation: it is the **surprise**. The first group uses one step of real observed
reward plus an estimate of the rest; $V(s_t)$ is the pure estimate made *before* seeing
that reward. The difference measures how much better or worse things turned out than
expected. So $\delta_t > 0$ is a pleasant surprise, $\delta_t < 0$ an unpleasant one, and
$\delta_t = 0$ exactly as predicted.

**Bootstrapping** means using your own estimate $V(s_{t+1})$ as part of the target for
$V(s_t)$. It is what makes TD methods sample-efficient — you need not wait for the episode
to finish to get a learning signal. The cost is bias: if $V$ is wrong, that error
propagates into the targets.

**The two extremes of estimating the advantage:**

$$\text{1-step TD:} \quad \hat{A}_t \approx \delta_t \qquad\qquad \text{Monte Carlo:} \quad \hat{A}_t \approx G_t - V(s_t)$$

The former has low variance (one reward term) and high bias (it leans on $V$ heavily);
the latter has high variance (the full random return) and low bias (it uses real
rewards). GAE interpolates between them.

## 2.7 Generalized Advantage Estimation (GAE)

GAE (Schulman et al., 2015 — the lecture's suggested reading) forms an
exponentially-weighted average of all the $k$-step advantage estimators:

$$\hat{A}_t^{\text{GAE}(\gamma, \lambda)} = \sum_{l=0}^{L-t} (\gamma \lambda)^l \, \delta_{t+l}$$

Written out:

$$\hat{A}_t = \delta_t + (\gamma\lambda)\,\delta_{t+1} + (\gamma\lambda)^2 \delta_{t+2} + (\gamma\lambda)^3 \delta_{t+3} + \cdots$$

**$\lambda$ is the bias-variance dial:**

| $\lambda$ | reduces to | character |
|---|---|---|
| $0$ | $\hat{A}_t = \delta_t$ | pure 1-step TD: lowest variance, highest bias |
| $1$ | $\hat{A}_t = G_t - V(s_t)$ | pure Monte Carlo: highest variance, no bias from $V$ |
| $0.95$ | — | the standard choice: mostly Monte Carlo, mildly smoothed |

**The efficient implementation** computes this with a single backward pass over the
sequence, using the recursion
$\hat{A}_t = \delta_t + \gamma\lambda \hat{A}_{t+1}$:

```python
A_next = 0
for t = L down to 1:
    V_next = 0 if t == L else V[t+1]      # nothing after the terminal token
    delta  = R[t] + gamma * V_next - V[t]
    A[t]   = delta + gamma * lambda * A_next
    A_next = A[t]
```

This is $O(L)$ — one reverse scan, no nested loops. Note the boundary condition: after
the terminal token there is no future, so $V_{L+1} = 0$.

**The regression targets for the value model** come out of the same computation:

$$\text{returns}_t = \hat{A}_t + V(s_t)$$

which follows directly from $A = G - V$. The value model is then trained to regress
toward $\text{returns}_t$ — the lecture's "label = reward".

## 2.8 On-policy vs off-policy

- **On-policy**: the data used for the update was generated by the *current* policy.
- **Off-policy**: the data came from some other policy (an old version, a human, another
  model).

**PPO is on-policy** (approximately). The objective is an expectation over
$y \sim \pi_\theta(\cdot \mid x)$ — the policy being optimized. This has hard
consequences:

1. You must **generate fresh data every iteration**. You cannot reuse a fixed dataset.
2. Generation dominates the compute cost, typically well over half the wall clock.
3. Data is discarded after a few gradient steps. It is not "sample efficient" in the
   supervised-learning sense.
4. You need the reward model available **online**, because the responses being scored did
   not exist until a moment ago and have no precomputed labels.

**Why "approximately".** Strictly on-policy would mean one gradient step per batch of
samples. PPO takes several (`ppo_epochs`), so after the first step the data is slightly
off-policy. The importance ratio corrects for this, and clipping bounds how far the
correction is trusted. PPO is best described as **near-on-policy with an importance
correction**.

**Contrast with DPO**, which is fully off-policy: $y_w$ and $y_l$ come from a fixed
preference dataset, nothing is generated during training, and the whole thing reduces to
a supervised loss. That is precisely why DPO needs no reward model and no value model —
and also why it cannot discover behaviors absent from its dataset.

---

# Part III — The RLHF Pipeline

## 3.1 Where preference tuning sits

```
   PRETRAINING          FINETUNING (SFT)        PREFERENCE TUNING
        |                      |                       |
        v                      v                       v
  broad knowledge      follows instructions      aligns with human
  of language,         for specific tasks        preferences
  code, facts
```

Each stage uses different data and a different objective:

| stage | data | objective | scale |
|---|---|---|---|
| Pretraining | raw text | next-token MLE | trillions of tokens |
| SFT | (prompt, ideal response) | next-token MLE | $10^4$–$10^6$ examples |
| Reward model | (prompt, better, worse) | Bradley-Terry MLE | $\sim 10^4$ comparisons |
| PPO | prompts only | expected reward | $\sim 10^5$ episodes |

Note the progression in what the data contains. Pretraining data has no notion of a
task. SFT data has a task and one correct answer. Preference data has a task and a
*relative judgment*. Only PPO's data has no answers at all — just prompts, with the model
generating its own candidates.

## 3.2 Why preferences instead of more SFT

The lecture's motivation is that an SFT model may still misbehave, and SFT alone gives
you no way to inject **negative** signal. Four reasons preference data helps:

**1. Comparing is easier than generating.** Asking a human to write the ideal response to
a hard prompt is slow, expensive, and requires expertise. Asking which of two responses
is better is fast and needs less skill. So you get far more data per dollar, on harder
prompts.

**2. SFT can only say "do this," never "not that."** Cross-entropy loss raises the
probability of the target text. There is no mechanism to *lower* the probability of a
specific bad response. Preference tuning has both directions — the lecture's "need to
inject negative signals."

**3. SFT is sensitive to distribution.** Training on text the model finds unlikely can
degrade it in unexpected ways. Preference methods operate on the model's own
distribution — in PPO's case, literally on its own samples.

**4. Absolute ratings are unreliable.** Humans are inconsistent when asked to score
quality from 1–10 (my 7 is your 5, and both drift over a session). Pairwise judgments are
far more stable, and Bradley-Terry converts them into a consistent scalar scale.

**One caveat the lecture raises:** a misbehaving model is also a signal to go check your
SFT data quality. Preference tuning is not a repair for a bad SFT stage.

## 3.3 Preference data collection

**Three labeling formats:**

| format | example |
|---|---|
| **pointwise** | each pair gets an absolute score: $0.4,\; 0.9,\; 0.1,\; 0.2$ |
| **pairwise** | comparisons: $\text{obs}_1 \prec \text{obs}_2$, $\text{obs}_1 \succ \text{obs}_3$, $\text{obs}_2 \succ \text{obs}_3$ |
| **listwise** | a full ranking: $\text{obs}_2 \succ \text{obs}_1 \succ \text{obs}_4 \succ \text{obs}_3$ |

Pairwise is the standard, because it is the easiest to label reliably and it maps directly
onto Bradley-Terry.

**The recipe for pairwise data:**

**Step 1 — generate a pair of responses for the same prompt.** Prompts come from
production logs or a reference distribution. Responses come from the SFT model with
sampling (different seeds or temperature), from synthetic generation, or from rewrites of
existing responses.

**Step 2 — label which is better.** Via human raters (this is the "HF" in RLHF), or via
proxies such as LLM-as-a-judge or metrics like BLEU / ROUGE where applicable. The scale
can be binary (better/worse) or nuanced (much better, slightly better, tie, …).

**Details that matter in practice.** Both responses must answer the *same* prompt — the
Bradley-Terry model compares strengths conditional on $x$. Generating them by sampling the
same model twice at temperature is the cheapest source of genuinely comparable pairs, and
it is another place where stochastic sampling (Part I) is load-bearing. Ties are awkward,
since plain Bradley-Terry has no tie outcome, so implementations either discard ties or
extend the model. And human agreement rates on these comparisons are typically well short
of perfect, which places a ceiling on how good the reward model can be: **the reward model
cannot be more accurate than the consistency of its labels.**

## 3.4 Stage 1: reward modeling

**Goal.** Learn a function that scores responses the way humans would:
$(x, y) \mapsto r(x,y) \in \mathbb{R}$.

**Architecture.** A pretrained LLM with the language-modeling head replaced by a
**classification/regression head** producing one number. For decoder-only models the
score is typically read off the final token's hidden state; for encoder-only models (BERT
and similar) it comes from the `[CLS]` projection, as the lecture notes. Initializing from
a strong pretrained model matters — the reward model needs to *understand* the text before
it can judge it.

**The loss** (derived in Section 1.20):

$$\mathcal{L}(r) = -\,\mathbb{E}_{(x,\, y_w,\, y_l) \sim \mathcal{D}} \Big[ \log \sigma\big(r(x, y_w) - r(x, y_l)\big) \Big]$$

**Reading the loss:**

| $r(x,y_w) - r(x,y_l)$ | $\sigma(\cdot)$ | loss | interpretation |
|---|---|---|---|
| $+4$ | $0.982$ | $0.018$ | already correct |
| $0$ | $0.500$ | $0.693$ | no opinion |
| $-4$ | $0.018$ | $4.018$ | confidently wrong |

Gradient descent widens the gap in the direction humans chose. Note the loss never
references an absolute target score — only the *difference* is supervised, which is
exactly the identifiability property from Section 1.20.

**Implementation note.** Both responses in a pair are usually put in the same forward
batch so the shared prompt encoding is computed once, and the difference is taken inside
the loss.

**Data scale.** Order $10^4$ comparisons is typical, per the lecture.

**Trained for one epoch.** The reward model overfits quickly beyond a single pass. Worth
remembering: even the supervised stage of RLHF is single-pass.

**Evaluation.** Benchmarks like RewardBench (Lambert et al., 2024) measure how often a
reward model ranks a held-out pair correctly.

**The fundamental limitation.** The reward model is accurate near the distribution it was
trained on and unreliable outside it. It is a *proxy*, and PPO will exploit its flaws
(Section 1.22). Everything about the KL penalty and short training exists because of this.

## 3.5 Stage 2: the RL objective

The full objective from Ouyang et al. (2022), which the lecture presents:

$$\max_{\theta} \;\; \mathbb{E}_{x \sim \mathcal{D},\; y \sim \pi_\theta(\cdot \mid x)} \Bigg[\, \underbrace{r(x,y)}_{\text{maximize rewards}} \;-\; \beta \underbrace{\log \frac{\pi_\theta(y \mid x)}{\pi_{\text{ref}}(y \mid x)}}_{\text{don't deviate from base model}} \Bigg]$$

**Term by term:**

| term | meaning |
|---|---|
| $x \sim \mathcal{D}$ | prompts drawn from a fixed prompt dataset |
| $y \sim \pi_\theta(\cdot \mid x)$ | responses **sampled from the policy being trained** — this is what makes the method on-policy, and why generation is part of the training loop |
| $r(x,y)$ | the frozen reward model's score |
| $\beta$ | the KL coefficient: how strongly to anchor to the reference |
| $\log\big(\pi_\theta / \pi_{\text{ref}}\big)$ | the per-sample KL estimate against the frozen SFT model |

**On $y \sim \pi_\theta(y \mid x)$ specifically**, since it is the crux: $y$ is a response
*generated by the current model*, not a label from a dataset. There is no ground truth
$y$ anywhere in this stage. **The model proposes; the reward model judges.** Concretely,
$\pi_\theta(\cdot \mid x)$ is the distribution over complete responses induced by
autoregressive sampling (Section 1.9), and drawing from it means running the generation
loop of Section 4.3.

**What the two terms trade off.** Maximizing $r$ alone would let the policy run off to
whatever text maximizes a flawed proxy. The KL term prices the distance travelled. The
result is a **trust region**: find the highest-reward text that is still recognizably
close to the SFT model. The lecture's note that this "avoids reward hacking and training
instability" is exactly this.

**Choosing $\beta$:**

- **too small** — the policy drifts far, reward climbs, real quality collapses (reward
  hacking; classic symptoms are repetition, degenerate formatting, sycophancy);
- **too large** — the policy barely moves from SFT, and you spent a lot of compute to
  change nothing.

**Data scale.** Order $10^5$ episodes, per the lecture, with the "label" being the reward
model's score rather than any human annotation. Human effort was spent once, in stage 1.

**Initialization.** The policy starts at the SFT model. So does the value model (with a
new head), and $\pi_{\text{ref}}$ is a frozen copy of it.

Note this objective says nothing about *how* to optimize it. PPO is one choice of
optimizer for it; REINFORCE, RLOO, and GRPO are others.

---

# Part IV — PPO, Step by Step

## 4.1 The four models

PPO for LLMs requires four models in memory. This is the lecture's main stated
limitation.

| name | symbol | role | trained? |
|---|---|---|---|
| **policy** | $\pi_\theta$ | the LLM being aligned | yes |
| **value** | $V_\phi$ | predicts expected return | yes |
| **reward** | $r$ | scores complete responses | no (frozen) |
| **reference** | $\pi_{\text{ref}}$ | anchor for the KL penalty | no (frozen) |

**Initialization:**

$$\pi_\theta := \pi_{\text{sft}}, \qquad \pi_{\text{ref}} := \text{freeze}(\pi_{\text{sft}}), \qquad V_\phi := \text{body}(\pi_{\text{sft}}) + \text{scalar head}$$

with $r$ trained separately in stage 1 and frozen.

**Memory cost.** The two trained models need parameters, gradients, and optimizer state
(Adam keeps two moments), while the two frozen models need parameters only. A rough
accounting per parameter in mixed precision:

| model | needs | bytes/param |
|---|---|---|
| $\pi_\theta$ | weights + grads + Adam moments + fp32 master | $\approx 16$ |
| $V_\phi$ | same | $\approx 16$ |
| $\pi_{\text{ref}}$ | weights only | $\approx 2$ |
| $r$ | weights only | $\approx 2$ |

So the trained models dominate; the frozen ones are comparatively cheap and can be
sharded, offloaded, or served remotely.

**Which are the same architecture?** All four are usually the same base architecture and
tokenizer. $\pi_\theta$ and $\pi_{\text{ref}}$ are literally identical models at
different points in time. $V_\phi$ and $r$ share the body but have scalar heads instead of
LM heads. The reward model is the only one that is *not* a copy of this lineage — it is
the sole carrier of external human preference information in the loop.

## 4.2 The three policies

Distinct from the four models: within the objective there are **three policies**, two of
which are snapshots of the same lineage.

| policy | what it is |
|---|---|
| $\pi_\theta$ | **current** weights: live, differentiable, changes every step |
| $\pi_{\theta_{\text{old}}}$ | **snapshot** taken at generation time, refreshed each iteration |
| $\pi_{\text{ref}}$ | **snapshot** taken at step 0, never refreshed |

All three are byte-identical at the start of training. They diverge as follows:

```
SFT weights
     |
     +---> pi_ref         frozen for the ENTIRE run                  [never moves]
     |
     +---> pi_theta       trained by PPO                             [moves constantly]
               |
               +--------> pi_theta_old := snapshot each iteration     [chases pi_theta]

timeline:
  iter 1:    pi_theta_old := pi_theta;  generate; score; update pi_theta
  iter 2:    pi_theta_old := pi_theta;  generate; score; update pi_theta
  ...
  iter 500:  pi_theta_old := pi_theta;  generate; score; update pi_theta
             pi_ref: still exactly the SFT model
```

**Where each appears in the math:**

$$\rho_t = \frac{\pi_\theta(y_t \mid x, y_{<t})}{\pi_{\theta_{\text{old}}}(y_t \mid x, y_{<t})} \qquad\qquad \text{kl}_t = \log \pi_\theta(y_t \mid x, y_{<t}) - \log \pi_{\text{ref}}(y_t \mid x, y_{<t})$$

$\pi_\theta$ is in the numerator of both, and it is the **only one carrying gradients**.
The other two are stored constants at update time.

**The critical distinction — time horizon:**

| | $\pi_{\theta_{\text{old}}}$ | $\pi_{\text{ref}}$ |
|---|---|---|
| nature | a **moving** reference, $\sim 1$ iteration behind | a **fixed** reference, thousands of steps behind |
| answers | "am I taking too big a step *right now*?" | "how far have I wandered in *total*?" |
| purpose | optimization stability | alignment / anti-drift |

**Why the fixed one is indispensable.** With only the ratio, every individual step looks
fine while the policy slowly walks somewhere terrible:

| step | drift from SFT | $\rho$ vs $\pi_{\theta_{\text{old}}}$ |
|---|---|---|
| 1 | negligible | $\approx 1.0$ — looks fine |
| 100 | noticeable | $\approx 1.0$ — looks fine |
| 1000 | unrecognizable, reward-hacked | $\approx 1.0$ — **still** looks fine |

The ratio has no memory beyond one iteration, so it cannot detect this. $\pi_{\text{ref}}$
can: as drift accumulates, $\log \pi_\theta - \log \pi_{\text{ref}}$ grows and the penalty
grows with it. The lecture's remark that "nowadays, KL divergence is with respect to ref
(base model)" is precisely this point — small steps alone do not prevent a long slow walk
to a bad place.

**A useful sanity check.** If you set `ppo_epochs = 1`, then
$\pi_\theta = \pi_{\theta_{\text{old}}}$ exactly at gradient time, so $\rho_t = 1$
everywhere and clipping is completely inert. The $\pi_{\text{ref}}$ penalty still matters
enormously. Any behavior that changes under that setting was attributable to clipping;
anything unchanged was attributable to the KL anchor.

**Worked numbers at one token position** (the model choosing `" not"`):

| | $p(\text{`` not''})$ | $\log p$ | |
|---|---|---|---|
| $\pi_{\text{ref}}$ | $0.05$ | $-3.00$ | SFT thought this unlikely |
| $\pi_{\theta_{\text{old}}}$ | $0.30$ | $-1.20$ | policy at generation time |
| $\pi_\theta$ | $0.36$ | $-1.02$ | policy now, mid-update |

$$\rho = \frac{0.36}{0.30} = 1.20 \quad \text{(exactly at the } \epsilon = 0.2 \text{ clip boundary: stop pushing)}$$

$$\text{kl} = -1.02 - (-3.00) = 1.98 \quad \text{(far above SFT here: penalize)}$$

Two independent readings from one token, on two different timescales.

---

## 4.3 Step 1: rollout (generation)

**Input:** a batch of prompts from $\mathcal{D}$.
**Output:** sampled responses, plus the log-probs recorded during generation.

### The generation loop in detail

```python
for each prompt x in the batch:

    context   = tokenize(x)
    y         = []
    logprobs  = []
    kv_cache  = None

    while True:
        # 1. forward pass (only the new token, thanks to the KV cache)
        logits, kv_cache = policy(context, kv_cache)
        logits = logits[-1]                    # only the last position predicts next

        # 2. shape the distribution
        logits = logits / T                    # temperature; T = 1.0 for PPO
        p      = softmax(logits)
        p      = apply_top_k_top_p(p)          # usually disabled for PPO

        # 3. SAMPLE (inverse CDF, Section 1.12)
        u   = uniform(0, 1)
        tok = first index where cumsum(p) >= u

        # 4. RECORD the log-prob of the token actually chosen
        logprobs.append( log p[tok] )

        # 5. extend
        y.append(tok)
        context = context + [tok]

        # 6. stopping conditions
        if tok == EOS:                break
        if len(y) >= max_new_tokens:  break
```

### Every detail that matters here

**One draw per position.** You sample once at each position, from a *different*
distribution each time (the context grew). You never redraw at the same position. The
"60% token appears 60 times per 100" statement describes frequencies across many
independent *regenerations*, not repeated draws within one generation.

**Record log-probs at generation time.** Step 4 is essential. These values become
$\log \pi_{\theta_{\text{old}}}$, the denominator of the ratio. If you recomputed them
later, after the weights had moved, the ratio would be $1$ by construction and clipping
would be meaningless. Note you record the log-prob of the token **actually sampled**, not
the max — one number per position, not a full distribution.

**The KV cache.** Without it, generating token $t$ would re-process the whole context,
making generation $O(L^2)$ in forward passes. The cache stores the attention keys and
values for previous positions so each new token costs one incremental pass. Pure inference
optimization; it does not affect the math.

**Sampling must be stochastic.** Covered in Section 1.12: greedy decoding destroys
exploration and breaks the Monte Carlo estimator.

**Temperature is part of the objective's definition.** Whatever $T$ you generate at
defines the distribution $\pi_\theta$ that the rest of the math refers to. See Section 5.6.

**Multiple responses per prompt.** How many depends on the algorithm:

- **PPO** — typically **1** response per prompt, with a large batch of *different* prompts
  (e.g. 512–1024). Variance reduction comes from the value model.
- **GRPO** — **must** sample a group, typically $G \in [8, 64]$ per prompt, because the
  baseline is the within-group mean reward.

**This step dominates cost.** Generation is sequential and memory-bandwidth bound, usually
more than half of wall-clock time. Hence the common architecture of handing rollouts to a
dedicated inference engine (vLLM, SGLang) and syncing weights back — which is also the
origin of the bug in Section 5.6.

**Left-padding for batched generation.** When batching prompts of different lengths, pad
on the **left** so all sequences' "next token" positions align at the right edge.
Right-padding would put pad tokens between the prompt and the generation.

---

## 4.4 Step 2: scoring

**Input:** the $(x, y)$ pairs from step 1.
**Output:** one scalar per response, plus reference log-probs and value predictions.

### 2a. Reward model

$$\text{score} = r(x, y)$$

One scalar for the **entire** response.

- The reward model sees the full concatenated prompt and response, formatted with the
  **same chat template** used in its training. A template mismatch here silently corrupts
  the scores — a common and hard-to-find bug.
- The score is read from the final token's hidden state (for decoder-only reward models).
  Which "final token" matters: it should be the last *real* token, not a pad.
- This is the **central awkwardness of RLHF**: the reward is *sequence-level*, but the
  policy makes *token-level* decisions. Steps 3 and 4 exist entirely to bridge that gap.

### 2b. Reference log-probs

$$\log \pi_{\text{ref}}(y_t \mid x, y_{<t}) \qquad \text{for } t = 1, \ldots, L$$

This is a **single forward pass**, not generation — you already know all the tokens, so
you can process them in parallel and read off the log-prob of each actual token. Cheap
relative to step 1.

### 2c. Value predictions

$$V_\phi(s_t) \qquad \text{for } t = 1, \ldots, L$$

Also one forward pass, producing a scalar per position.

**Everything in step 2 is inference only.** No gradients are needed yet. All three
sub-steps can run under `no_grad`, and 2b and 2c can be batched with the policy's own
forward pass if the models are colocated.

---

## 4.5 Step 3: per-token reward construction

**Input:** the sequence-level score, the policy log-probs, the reference log-probs.
**Output:** a per-token reward array $R_t$.

This is where the sequence-level reward is turned into something an RL algorithm can use,
and where the KL penalty is physically inserted:

$$R_t = -\beta\,\text{kl}_t + \underbrace{r(x,y) \cdot \mathbf{1}[t = L]}_{\text{terminal token only}}, \qquad \text{kl}_t = \log \pi_{\theta_{\text{old}}}(y_t \mid \cdot) - \log \pi_{\text{ref}}(y_t \mid \cdot)$$

Concretely, for a five-token response with $\beta = 0.1$:

| position $t$ | 1 | 2 | 3 | 4 | 5 (last) |
|---|---|---|---|---|---|
| $\text{kl}_t$ | $0.10$ | $0.05$ | $0.80$ | $0.02$ | $0.03$ |
| $-\beta\,\text{kl}_t$ | $-0.010$ | $-0.005$ | $-0.080$ | $-0.002$ | $-0.003$ |
| $r(x,y)$ | — | — | — | — | $+2.500$ |
| $\mathbf{R_t}$ | $\mathbf{-0.010}$ | $\mathbf{-0.005}$ | $\mathbf{-0.080}$ | $\mathbf{-0.002}$ | $\mathbf{+2.497}$ |

### Details worth understanding

**Why the KL is per-token but the reward is terminal.** The KL is a per-token quantity by
construction — it is defined on each next-token distribution, so it can be assessed
locally at every position. The reward model, by contrast, only knows how to judge a
*complete* response. There is nothing to attribute to token 3 in isolation.

**Notice position 3 above.** It has a large KL ($0.80$), meaning the policy has drifted
substantially from the reference at that specific position, and it receives a
correspondingly larger penalty. The KL penalty is thus **targeted**: it pushes back
exactly where the drift is, token by token.

**This is the objective, rearranged.** The Ouyang objective is
$r(x,y) - \beta\,\text{KL}$. Since the sequence KL is the sum of per-token KLs,
distributing the penalty across tokens and putting $r$ at the end gives a per-token reward
whose *total* equals the original objective:

$$\sum_{t=1}^{L} R_t = r(x,y) - \beta \sum_{t=1}^{L} \text{kl}_t$$

Nothing has changed mathematically; it has been reshaped into a form GAE can consume.

**Which log-probs to use for the KL.** Implementations differ subtly on whether to use
$\pi_{\theta_{\text{old}}}$ (fixed during the inner epochs) or the live $\pi_\theta$.
Using $\pi_{\theta_{\text{old}}}$ keeps $R_t$ constant across the inner epochs, which is
simpler and standard. An alternative treats the KL as a differentiable term added directly
to the loss rather than baked into the reward; both appear in practice.

**Sign conventions.** $R_t$ is a reward to be *maximized*, so the KL penalty enters with a
minus sign. Getting this sign backwards produces a model that actively runs *away* from
the reference, which is a spectacular and instructive failure.

---

## 4.6 Step 4: advantage estimation

**Input:** $R_t$ from step 3, $V_\phi(s_t)$ from step 2c.
**Output:** advantages $\hat{A}_t$ and value targets $\text{returns}_t$.

Apply GAE (Section 2.7) with a single reverse scan:

$$\delta_t = R_t + \gamma V(s_{t+1}) - V(s_t), \qquad \hat{A}_t = \delta_t + \gamma\lambda \hat{A}_{t+1}, \qquad \hat{A}_{L+1} = 0,\; V(s_{L+1}) = 0$$

Then form the value targets and whiten the advantages across the batch:

$$\text{returns}_t = \hat{A}_t + V(s_t), \qquad\qquad \hat{A} \leftarrow \frac{\hat{A} - \operatorname{mean}(\hat{A})}{\operatorname{std}(\hat{A}) + \varepsilon}$$

### Full numerical example

Take the five-token response above, with $\gamma = 1.0$, $\lambda = 0.95$, and value
predictions $V = (1.8,\; 1.9,\; 2.0,\; 2.3,\; 2.4)$:

```
R = [-0.010, -0.005, -0.080, -0.002, 2.497]
V = [ 1.800,  1.900,  2.000,  2.300, 2.400]

t=5:  V_next = 0        (terminal)
      delta = 2.497 + 0     - 2.400 =  0.097
      A[5]  = 0.097 + 0.95*0        =  0.097

t=4:  V_next = V[5] = 2.400
      delta = -0.002 + 2.400 - 2.300 =  0.098
      A[4]  =  0.098 + 0.95*0.097    =  0.190

t=3:  V_next = V[4] = 2.300
      delta = -0.080 + 2.300 - 2.000 =  0.220
      A[3]  =  0.220 + 0.95*0.190    =  0.401

t=2:  V_next = V[3] = 2.000
      delta = -0.005 + 2.000 - 1.900 =  0.095
      A[2]  =  0.095 + 0.95*0.401    =  0.476

t=1:  V_next = V[2] = 1.900
      delta = -0.010 + 1.900 - 1.800 =  0.090
      A[1]  =  0.090 + 0.95*0.476    =  0.542

A       = [0.542, 0.476, 0.401, 0.190, 0.097]
returns = A + V = [2.342, 2.376, 2.401, 2.490, 2.497]
```

All advantages are positive here, meaning this response did better than the value model
expected, so every token gets pushed up — more strongly at the start, where the accumulated
future advantage is largest.

Note how the reverse scan propagates the terminal reward *backwards*. The good final score
raises the advantage of **every** preceding token, which is how a sequence-level reward
reaches token 1. That is the credit assignment mechanism.

(Whitening is skipped here to keep the arithmetic legible; in practice $\hat{A}$ would be
normalized across the batch at this point.)

### The sign is the learning signal

$$\hat{A}_t > 0 \implies \text{make } y_t \text{ more likely}, \qquad \hat{A}_t < 0 \implies \text{make } y_t \text{ less likely}$$

Everything downstream just implements "move probability in the direction of the advantage,
but not too fast."

---

## 4.7 Step 5: the probability ratio

**Input:** the stored tokens, the stored $\log \pi_{\theta_{\text{old}}}$.
**Output:** $\rho_t$ for each position.

Now gradients begin. Run the **current** policy over the stored $(x, y)$ tokens — one
forward pass, **no sampling**, because the tokens are already fixed:

$$\log \rho_t = \log \pi_\theta(y_t \mid x, y_{<t}) - \log \pi_{\theta_{\text{old}}}(y_t \mid x, y_{<t}), \qquad \rho_t = \exp\big(\log \rho_t\big)$$

### Details

**Computed as a difference of logs, then exponentiated** — never as a quotient of
probabilities, which would risk underflow and lose precision (Section 1.11).

**It starts at exactly $1$.** On the first gradient step of the first inner epoch
$\pi_\theta = \pi_{\theta_{\text{old}}}$, so $\log \rho_t = 0$ and $\rho_t = 1$. It drifts
away as the inner epochs proceed. A useful debugging check: if $\rho_t \ne 1$ on the very
first inner step, something is inconsistent between your generation and training paths
(Section 5.6).

**Only $\pi_\theta$ carries gradients.** $\log \pi_{\theta_{\text{old}}}$ is a stored
constant, so

$$\nabla_\theta \rho_t = \rho_t \, \nabla_\theta \log \pi_\theta(y_t \mid x, y_{<t})$$

and the backward pass reduces to the familiar score function of Section 1.17.

**No generation in this step.** Worth emphasizing, because it is a common misconception.
Sampling happened once, in step 1. From here on the tokens are *data*. Every subsequent
forward pass is a parallel teacher-forced pass over known tokens, which is fast.

**Interpretation.** $\rho_t$ answers: *how much more (or less) likely is this exact token
now, compared to when I generated it?* So $\rho = 1$ means unchanged, $\rho = 1.3$ means
30% more likely, $\rho = 0.7$ means 30% less likely, and $\rho = 50$ means something has
gone badly wrong.

---

## 4.8 Step 6: clipping (the heart of PPO)

**The clipped surrogate objective:**

$$L^{\text{CLIP}}(\theta) = \mathbb{E}_t \Big[ \min\Big( \rho_t \hat{A}_t, \;\; \operatorname{clip}\big(\rho_t,\, 1-\epsilon,\, 1+\epsilon\big) \hat{A}_t \Big) \Big]$$

where

$$\operatorname{clip}(z, \text{lo}, \text{hi}) = \begin{cases} \text{lo} & z < \text{lo} \\ \text{hi} & z > \text{hi} \\ z & \text{otherwise} \end{cases}$$

and $\epsilon$ is typically $0.2$, giving the band $[0.8,\, 1.2]$.

### The full case analysis

This deserves careful treatment because the $\min$ behaves **asymmetrically** depending on
the sign of $\hat{A}_t$. Remember we are *maximizing* $L^{\text{CLIP}}$.

**Case A: $\hat{A}_t > 0$** (good token — we want to increase its probability)

| $\rho_t$ | unclipped | clipped | $\min(\cdot)$ | gradient? |
|---|---|---|---|---|
| $0.5$ | $0.5\hat{A}$ | $0.8\hat{A}$ | $0.5\hat{A}$ | yes (unclipped branch) |
| $1.0$ | $1.0\hat{A}$ | $1.0\hat{A}$ | $1.0\hat{A}$ | yes |
| $1.1$ | $1.1\hat{A}$ | $1.1\hat{A}$ | $1.1\hat{A}$ | yes |
| $1.2$ | $1.2\hat{A}$ | $1.2\hat{A}$ | $1.2\hat{A}$ | boundary |
| $1.5$ | $1.5\hat{A}$ | $1.2\hat{A}$ | $1.2\hat{A}$ | **no** (constant) |
| $3.0$ | $3.0\hat{A}$ | $1.2\hat{A}$ | $1.2\hat{A}$ | **no** |

Once $\rho_t > 1+\epsilon$, the objective is stuck at $1.2\hat{A}$. Increasing the
probability further yields no gain, so the gradient through this token is **zero**. PPO
says: *you have boosted this token enough for now; stop.*

But note the asymmetry at low ratios: at $\rho_t = 0.5$, the $\min$ picks the
**unclipped** $0.5\hat{A}$, which still has gradient. So if the policy has moved a good
token's probability *down* too far, PPO will happily push it back up. **The clip does not
block corrective moves.**

**Case B: $\hat{A}_t < 0$** (bad token — we want to decrease its probability)

Careful: $\hat{A}_t$ is negative, so multiplying flips the comparisons. Take
$\hat{A} = -1$:

| $\rho_t$ | unclipped | clipped | $\min(\cdot)$ | gradient? |
|---|---|---|---|---|
| $0.3$ | $-0.3$ | $-0.8$ | $-0.8$ | **no** (clipped) |
| $0.5$ | $-0.5$ | $-0.8$ | $-0.8$ | **no** |
| $0.8$ | $-0.8$ | $-0.8$ | $-0.8$ | boundary |
| $0.9$ | $-0.9$ | $-0.9$ | $-0.9$ | yes |
| $1.0$ | $-1.0$ | $-1.0$ | $-1.0$ | yes |
| $2.0$ | $-2.0$ | $-1.2$ | $-2.0$ | yes (unclipped is smaller) |

Once $\rho_t < 1-\epsilon$ the objective is pinned at $-0.8$ and the gradient vanishes:
*you have suppressed this token enough; stop.* And again the asymmetry works in the
corrective direction: at $\rho_t = 2.0$ the $\min$ selects the unclipped $-2.0$, which
retains gradient, so the policy is pushed to bring that bad token's probability back down.

### The summary that captures it

$$\hat{A} > 0: \ \text{gradient dies when } \rho > 1+\epsilon \qquad\qquad \hat{A} < 0: \ \text{gradient dies when } \rho < 1-\epsilon$$

In **both** cases the gradient survives in the direction that *corrects* an overshoot. The
$\min$ makes the objective **pessimistic**: it always takes the less optimistic of the two
estimates. That pessimism is the design. PPO never lets an optimistic
importance-weighted estimate justify a large step, but it always permits a step that undoes
one.

### Why this works — three framings

**As variance control (Section 1.16).** The ratio is an importance weight, and importance
weights have unbounded variance. Clipping bounds them, trading bias for a finite-variance
estimator.

**As an implicit trust region.** The original TRPO enforced a hard KL constraint via
constrained optimization with second-order machinery. PPO achieves a similar effect with a
first-order clip that any autodiff framework handles. This is the entire selling point of
the paper: TRPO-like reliability, SGD-like simplicity.

**As "Proximal".** The name says it — keep the new policy *proximal* (near) to the old one.

### Two terminology warnings from the lecture

1. $L^{\text{CLIP}}$ is an **objective to maximize**, not a loss to minimize.
   Implementations negate it before calling `backward()`.
2. The $r$ in "ratio" is **not** the reward. The literature overloads $r$ for both; these
   notes use $\rho_t$ for the ratio to avoid it.

---

## 4.9 Step 7: the value loss

The value model is trained by regression onto the returns computed in step 4:

$$L^{V}(\phi) = \mathbb{E}_t\Big[\big(V_\phi(s_t) - \text{returns}_t\big)^2\Big]$$

This is the lecture's "trained jointly with policy" and "label = reward".

**The clipped variant**, used by most implementations for the same stability reason as the
policy clip:

$$V^{\text{clipped}} = V_{\text{old}} + \operatorname{clip}\big(V_\phi - V_{\text{old}},\, -\epsilon_v,\, +\epsilon_v\big)$$

$$L^{V} = \tfrac{1}{2}\,\mathbb{E}_t\Big[\max\Big(\big(V_\phi - \text{returns}\big)^2,\; \big(V^{\text{clipped}} - \text{returns}\big)^2\Big)\Big]$$

Note this uses $\max$, not $\min$, because the value term is a **loss being minimized**
whereas $L^{\text{CLIP}}$ is an **objective being maximized**. Both are being pessimistic;
the direction of pessimism just flips with the sign convention.

**Why the value model is a source of trouble.** Its target $\text{returns}_t$ depends on
the current policy's behavior. As the policy changes, the targets move. The value model is
therefore permanently chasing a non-stationary objective — it is never fully converged, its
predictions are biased, and that bias flows straight into the advantages via $\delta_t$.
This is one of the strongest arguments for GRPO, which deletes the value model and uses an
empirical group mean instead.

**Whether to share parameters.** Two designs exist:

- **separate** — two full models. More memory, no interference. Standard for LLM RLHF.
- **shared** — one body with two heads (LM + value). Less memory, but the two objectives can
  fight over the shared representation.

For LLMs, separate is the norm, because the value head's gradients can otherwise damage the
language modeling representation.

---

## 4.10 Step 8: entropy bonus and total loss

Assemble the final scalar to minimize:

$$L^{\text{total}} = \underbrace{-\,L^{\text{CLIP}}}_{\text{policy}} \;+\; \underbrace{c_1 L^{V}}_{\text{value}} \;-\; \underbrace{c_2 H(\pi_\theta)}_{\text{entropy bonus}}$$

Typical weights: $c_1 \in [0.5, 1.0]$ and $c_2 \in [0, 0.01]$ (often exactly $0$ for LLM
RLHF, since the KL penalty already resists collapse).

**The entropy term** (Section 1.14) is computed over the full next-token distribution at
each position and averaged:

$$H = \frac{1}{L}\sum_{t=1}^{L} \left( -\sum_{i=1}^{V} p_{t,i} \log p_{t,i} \right)$$

Its job is to resist **mode collapse**. Without pressure toward uncertainty, a policy that
finds one high-reward response can concentrate all probability on it, at which point
sampling returns identical text, exploration dies, and learning stops.

**Signs are the most common bug here.** Track them carefully:

| term | we want it | enters $L^{\text{total}}$ with |
|---|---|---|
| $L^{\text{CLIP}}$ | large | **minus** |
| $L^{V}$ | small | **plus** |
| $H$ | large | **minus** |

---

## 4.11 Step 9: the optimizer step

```python
L_total.backward()
clip_grad_norm_(parameters, max_norm=1.0)
optimizer.step()
optimizer.zero_grad()
```

**Gradient norm clipping** — distinct from PPO's ratio clipping, same word, unrelated
mechanism — rescales the whole gradient vector if its norm exceeds a threshold:

$$\text{if } \lVert g \rVert > g_{\max}: \quad g \leftarrow g \cdot \frac{g_{\max}}{\lVert g \rVert}$$

This is generic deep learning hygiene against occasional huge gradients, and it is
essentially mandatory here.

**Optimizer.** Adam or AdamW, with a much smaller learning rate than SFT — typically
$10^{-6}$ to $10^{-5}$ for the policy, versus $10^{-5}$ to $10^{-4}$ for SFT. The policy is
already good; PPO is making small corrections against a noisy signal, and a large learning
rate destroys it quickly.

**Separate optimizers.** The policy and value model usually get their own optimizers, often
with different learning rates (the value model can tolerate a larger one).

**Gradient accumulation.** PPO batches are large, so a batch is typically split into
minibatches with gradients accumulated before stepping.

**Early stopping on KL.** Many implementations check the KL between $\pi_\theta$ and
$\pi_{\theta_{\text{old}}}$ after each inner epoch and **break out of the inner loop** if it
exceeds a threshold. This is a safety valve for when clipping alone is not holding the
update in check.

---

## 4.12 The complete loop in pseudocode

```python
# ---------- INITIALIZATION ----------
pi_theta = load(sft_checkpoint)                 # trained
V_phi    = load(sft_checkpoint) + scalar_head   # trained
pi_ref   = freeze(load(sft_checkpoint))         # frozen anchor
r        = freeze(load(reward_model))           # frozen judge

# ---------- OUTER LOOP: usually ONE pass over the prompt dataset ----------
for iteration in range(num_iterations):

    # ===== STEP 1: ROLLOUT (the only place sampling happens) =====
    prompts = sample_batch(D)
    with no_grad():
        responses, logprobs_old = generate(pi_theta, prompts, T=1.0)
        # logprobs_old IS log pi_theta_old -- captured at generation time

    # ===== STEP 2: SCORING (all inference) =====
    with no_grad():
        scores       = r(prompts, responses)         # one scalar per response
        logprobs_ref = forward_logprobs(pi_ref, prompts, responses)
        values       = V_phi(prompts, responses)     # one scalar per token

    # ===== STEP 3: PER-TOKEN REWARDS =====
    kl      = logprobs_old - logprobs_ref
    rewards = -beta * kl
    rewards[:, last_token_index] += scores           # terminal reward

    # ===== STEP 4: ADVANTAGES (GAE) =====
    advantages, returns = compute_gae(rewards, values, gamma=1.0, lam=0.95)
    advantages = whiten(advantages)

    # ===== INNER LOOP: 1-4 passes over THIS batch =====
    for epoch in range(ppo_epochs):
        for minibatch in shuffle_split(batch):

            # ===== STEP 5: RATIO (gradients start here) =====
            logprobs_new = forward_logprobs(pi_theta, minibatch)   # NO sampling
            log_ratio    = logprobs_new - minibatch.logprobs_old
            ratio        = exp(log_ratio)

            # ===== STEP 6: CLIPPED POLICY OBJECTIVE =====
            L_clip = mean(minimum(
                ratio * minibatch.advantages,
                clamp(ratio, 1-eps, 1+eps) * minibatch.advantages
            ))

            # ===== STEP 7: VALUE LOSS =====
            V_new   = V_phi(minibatch)
            L_value = mean((V_new - minibatch.returns) ** 2)

            # ===== STEP 8: TOTAL =====
            H       = entropy(logprobs_new)
            L_total = -L_clip + c1 * L_value - c2 * H

            # ===== STEP 9: UPDATE =====
            L_total.backward()
            clip_grad_norm_(all_params, 1.0)
            optimizer.step()
            optimizer.zero_grad()

        # safety valve
        if approx_kl(logprobs_new, minibatch.logprobs_old) > kl_early_stop:
            break

    # batch is now DISCARDED. Next iteration generates fresh data.
```

### Reading the loop structure

Three nested levels of repetition, and it is worth being explicit about how many times each
runs, because the answer is "few" at every level:

| level | what repeats | how many times |
|---|---|---|
| 1 | inner gradient passes over one rollout batch (`ppo_epochs`) | **1 to 4** |
| 2 | passes over the prompt dataset | **usually 1**, occasionally 2 |
| 3 | the reward model's own training (stage 1) | **exactly 1** |

Level 1 is exactly why clipping exists: by pass 2 and beyond, the data is stale. With
`ppo_epochs = 1`, PPO is strictly on-policy and clipping is inert.

**So the lifetime of a single prompt is short:** generate one (or a few) responses, score
them, contribute to one batch, receive 1–4 gradient steps' worth of influence, and then be
retired — often never revisited.

**Why so few?** Section 1.22. The reward model is a proxy, and optimizing a proxy hard makes
it worse as a proxy. Practitioners typically do not fix an epoch count at all; they monitor
KL from the reference as a budget and stop when it is exhausted, or run periodic evaluations
and stop when true quality plateaus while reward is still climbing.

## 4.13 Hyperparameters

| name | typical | notes |
|---|---|---|
| learning rate | $10^{-6}$–$10^{-5}$ | much lower than SFT; the signal is noisy |
| $\beta$ (KL coef) | $0.01$–$0.1$ | the main knob for the alignment/drift tradeoff |
| $\epsilon$ (clip) | $0.2$ | remarkably robust; rarely needs tuning |
| $\gamma$ | $1.0$ | no reason to discount within one response |
| $\lambda$ (GAE) | $0.95$ | mostly Monte Carlo, mildly smoothed |
| `ppo_epochs` | $1$–$4$ | higher = more reuse, more staleness |
| $c_1$ (value coef) | $0.5$–$1.0$ | |
| $c_2$ (entropy) | $0$–$0.01$ | often $0$; the KL penalty already resists collapse |
| batch size | $512$–$1024$ | prompts per iteration |
| minibatch size | $32$–$128$ | |
| `max_new_tokens` | $512$–$2048$ | directly drives rollout cost |
| temperature $T$ | $1.0$ | **must** match what the log-probs assume |
| top-$p$ | $1.0$ (off) | truncation biases the gradient estimate |
| grad norm clip | $1.0$ | |
| target KL | $3$–$10$ | early-stopping threshold vs $\pi_{\text{ref}}$ |

The lecture's warning about "many hyperparameters to tune" is well earned: the interactions
are real. In particular $\beta$, the learning rate, and `ppo_epochs` all influence effective
step size, so tuning them independently is misleading.

---

# Part V — Implementation Details That Matter

These are the details that decide whether a PPO run works or silently fails. Most are not in
the papers.

## 5.1 Loss masking

Not every token in the context should contribute to the policy loss. Only tokens the
**policy actually generated** should.

| token source | in context? | train policy on it? |
|---|---|---|
| prompt $x$ | yes | **no** |
| model-generated $y$ | yes | **yes** |
| padding | yes | **no** |
| tool / API output | yes | **no** |

Implementation is a binary mask $m_t$ multiplied into the per-token loss, with the
normalization taken over the mask sum rather than the tensor size:

$$L = \frac{\sum_t \ell_t \, m_t}{\sum_t m_t}$$

**Why prompt tokens must be masked.** The policy did not choose them. Including them would
reinforce the model for "predicting" text it was handed, which is a different objective
entirely and corrupts the gradient.

**The agentic/tool-use case.** When a rollout interleaves model output with results returned
from the outside world — search results, a shell command's stdout, a Python traceback — those
returned tokens sit in the context but were **not generated by the policy**:

```
x                          -> masked
model tokens: <search:...> -> TRAINED
tool result (from world)   -> MASKED
model tokens: analysis...  -> TRAINED
tool result (traceback)    -> MASKED
model tokens: final answer -> TRAINED
```

Forgetting this mask means computing $\log \pi_\theta$ over text produced by a search engine
and reinforcing the model for reproducing it. It is the same class of bug as training on
prompt tokens, and it degrades models in confusing ways.

**Normalization choice.** Whether to average per-token over the batch or average per-sequence
then over the batch is a real design decision. Per-token averaging gives long responses more
influence; per-sequence weights all responses equally. This interacts with length bias
(Section 5.8).

## 5.2 Advantage whitening

$$\hat{A} \leftarrow \frac{\hat{A} - \operatorname{mean}(\hat{A})}{\operatorname{std}(\hat{A}) + 10^{-8}}$$

**Why.** The advantage multiplies the gradient, so its scale acts as a learning-rate
multiplier. Reward model output scales and value function accuracy both drift over a run, so
without normalization the effective learning rate drifts too, and no single learning rate
works throughout.

**Scope matters.** Whitening across the **whole batch** is standard. Whitening *per sequence*
would remove the between-response signal, which is precisely the signal you want. Get this
wrong and the run learns nothing while looking healthy.

**The caveat.** Dividing by a batch-sample standard deviation technically biases the estimator
and couples samples within a batch. It is universally done anyway because the stability gain
is large — another deliberate bias-for-variance trade.

## 5.3 KL estimators

The naive per-token KL estimate is

$$k_1 = \log \pi_\theta(y_t \mid \cdot) - \log \pi_{\text{ref}}(y_t \mid \cdot)$$

This is **unbiased** but has a surprising property: it can be **negative** for individual
tokens, even though the true KL is always $\ge 0$. The inequality holds for the true
expectation, not for a single-sample estimate. People often report this as a bug when it is
not.

Better estimators (from Schulman's writeup on the topic), with
$\rho = \pi_{\text{ref}}/\pi_\theta$ and samples drawn from $\pi_\theta$:

| estimator | formula | properties |
|---|---|---|
| $k_1$ | $-\log \rho$ | unbiased, high variance, can be negative |
| $k_2$ | $\tfrac{1}{2}(\log \rho)^2$ | biased, low variance, always $\ge 0$ |
| $k_3$ | $(\rho - 1) - \log \rho$ | **unbiased and always $\ge 0$** — preferred |

$k_3$ is the best of both: unbiased in expectation and non-negative sample by sample. Many
modern implementations use it for the reported KL metric, and sometimes for the penalty
itself.

**Two distinct uses to keep separate:** the KL **penalty** inside the reward (which affects
training) and the KL **metric** you log (which affects your monitoring and stopping
decisions). They need not use the same estimator, and confusing them makes debugging harder.

## 5.4 Adaptive KL control

Rather than fixing $\beta$, adapt it to hit a target KL:

$$\beta \leftarrow \begin{cases} 2\beta & \text{if } \text{KL} > 1.5\,\text{KL}_{\text{target}} \quad \text{(anchor harder)} \\[4pt] \beta/2 & \text{if } \text{KL} < \text{KL}_{\text{target}}/1.5 \quad \text{(allow more drift)} \\[4pt] \beta & \text{otherwise} \end{cases}$$

**The rationale.** The right $\beta$ depends on the reward scale, the task, and how far into
the run you are. Targeting a KL directly is more interpretable than targeting a penalty
coefficient: "stay within KL 6 of the reference" is a statement about the model, whereas
"use $\beta = 0.04$" is a statement about an arbitrary unit.

Some implementations use a proper controller for this; others keep $\beta$ fixed and simply
stop the run when KL exceeds budget. Both are defensible.

## 5.5 Value function clipping

Covered in Section 4.9. The reason it appears again here: the value model's targets are
non-stationary, so its predictions can jump between iterations. Clipping the value update
limits how far $V_\phi$ can move per step, for the same reason PPO clips the policy.

Worth noting this is **not** in the original PPO paper's core equations but is in essentially
every implementation, and ablations have found it meaningful. PPO's reputation for robustness
rests partly on such unpublished details.

## 5.6 The generation/training mismatch bug

This deserves its own section because it is common, silent, and destructive.

**The setup.** For speed, rollouts are often generated by a dedicated inference engine (vLLM,
SGLang, TensorRT-LLM) while the loss is computed in the training framework
(PyTorch/FSDP/DeepSpeed). Two different code paths must agree on the *exact same
distribution*.

**Ways they diverge:**

1. **Sampling parameters.** Generation at $T = 0.7$, top-$p = 0.9$ (serving defaults) while
   training computes log-probs under the full $T = 1.0$ distribution. The stored
   $\log \pi_{\theta_{\text{old}}}$ then does not match the tokens' actual sampling
   probabilities, and ratios are wrong from step one.
2. **Numerical precision.** Generation in bf16 with a fused kernel, training in fp32. Small
   log-prob discrepancies mean $\rho_t \ne 1$ on the first inner step even though nothing has
   been updated.
3. **Chat template / tokenization.** Generation applies one template, the reward model or
   trainer applies a slightly different one, so the reward model scores text the policy never
   produced.
4. **Kernel differences.** Different attention implementations or reduction orders — the same
   class of small discrepancy as (2).

**The diagnostic.** On the very first inner epoch of the first iteration, $\rho_t$ should be
**exactly 1** for every token, because $\pi_\theta = \pi_{\theta_{\text{old}}}$ by
construction:

$$\max_t \big\lvert \rho_t - 1 \big\rvert < \text{tolerance} \qquad \text{(first inner step)}$$

If it is not, you have a mismatch, and every subsequent conclusion about your run is suspect.

**The fix.** Either generate with exactly the settings your log-prob computation assumes
($T = 1.0$, no truncation), or recompute $\log \pi_{\theta_{\text{old}}}$ with the *training*
code path immediately after generation, so both sides of the ratio come from the same
implementation. The second option costs one extra forward pass and removes the class of bug
entirely.

## 5.7 Reward normalization

Recall from Section 1.20 that Bradley-Terry identifies rewards only **up to an additive
constant** — only differences carry meaning. So the raw scale of $r$ is arbitrary, and
normalizing is both permissible and useful:

$$r \leftarrow \frac{r - \mu_{\text{running}}}{\sigma_{\text{running}} + 10^{-8}}$$

**Why it helps.** A large constant offset in $r$ interacts badly with the KL penalty. If all
rewards are around $+50$ and $\beta\,\text{KL}$ is around $0.1$, the KL term is numerically
irrelevant and the anchor stops working. Centering the reward restores the intended balance
between the two terms.

**Whitening vs centering.** Some implementations only subtract the mean, leaving the scale
alone, on the grounds that dividing by a running standard deviation can amplify noise early
in training when few samples have been seen. Both approaches appear.

**Interaction with advantage whitening.** Note you may be normalizing twice — once on the
reward, once on the advantage. That is fine, but worth being conscious of when interpreting
magnitudes in your logs.

## 5.8 EOS, truncation, and length

**The EOS problem.** A response that hits `max_new_tokens` without emitting EOS was
*truncated*, not *completed*. Scoring it like a finished response teaches the model that
unterminated rambling is acceptable. Common handling: apply a penalty to responses that never
emitted EOS, or mask them out of the loss entirely — and always track the fraction of
truncated responses as a metric.

**Length bias.** RLHF famously makes responses longer, for several compounding reasons:

1. Human raters mildly prefer longer, more thorough-looking answers, so the reward model
   learns to reward length.
2. Per-token loss averaging can give long responses more total gradient weight.
3. A longer response accumulates more KL penalty, but if the reward gain from length exceeds
   it, length still wins.

This is a textbook case of Section 1.22: length correlates with quality in the training data,
so the proxy rewards length, and the optimizer exploits it. Mitigations include
length-penalizing the reward, normalizing the reward by length, or debiasing the reward model
itself. **Response length is one of the most informative things to monitor** — sharply rising
length is a classic reward-hacking signature.

**Where the reward attaches.** The terminal reward must land on the last *real* token.
Attaching it to a padding position, or off by one, breaks credit assignment in a way that is
very hard to spot.

## 5.9 What to monitor

The lecture lists "metric to monitor training" as a genuine difficulty, because reward going
up is not evidence that anything good is happening.

| metric | healthy | warning sign |
|---|---|---|
| reward (mean) | rising steadily | rising while evals fall = **hacking** |
| KL from $\pi_{\text{ref}}$ | slow, bounded growth | rapid growth = drifting off |
| entropy | slowly decreasing | collapsing = mode collapse |
| response length | roughly stable | climbing fast = length hacking |
| clip fraction | $\approx 0.05$–$0.2$ | $> 0.5$ = steps too large |
| approx KL vs $\pi_{\theta_{\text{old}}}$ | small | large = inner loop too long |
| value loss | decreasing | flat or rising = $V$ not learning |
| explained variance of $V$ | positive, rising | near $0$ = $V$ is useless |
| grad norm | stable | spikes = instability |
| truncated fraction | low | rising = length limit too tight |

**Two metrics deserve emphasis.**

**Clip fraction** — the share of tokens where clipping activated. It tells you whether
$\epsilon$ is doing any work. Near zero means clipping is inert (your steps are tiny); above
$\approx 0.5$ means most updates are being throttled, so your learning rate or `ppo_epochs`
is too aggressive.

**Explained variance of the value model:**

$$\text{EV} = 1 - \frac{\operatorname{Var}\big[\text{returns} - V\big]}{\operatorname{Var}\big[\text{returns}\big]}$$

If this is near zero, the value model is not predicting anything and your advantages are
essentially unbaselined returns, with all the variance problems of Section 1.18. This is the
metric that tells you whether paying for a value model is buying you anything; if it stays
near zero, GRPO's group baseline is likely a better use of the compute.

**The non-negotiable one: hold out real evaluations.** Reward is the proxy. The only way to
detect overoptimization is to periodically measure something the policy is *not* being
trained against — held-out win rates against a reference model, task benchmarks, or human
review. Reward climbing while held-out quality falls is the definitive signature of reward
hacking, and you cannot see it by watching reward alone.

---

# Part VI — Failure Modes

## 6.1 Reward hacking / overoptimization

**Symptom.** Reward climbs; held-out quality falls.

**Cause.** Section 1.22 in full. The reward model is a proxy fitted on finite data; the
optimizer finds where the proxy is wrong.

**Typical manifestations:** responses grow much longer with no added content; excessive
hedging, disclaimers, or restating the question; sycophancy (agreeing with the user regardless
of correctness); formatting tics the reward model happened to like; repetitive phrasing that
scores well; confident refusal to answer, if refusals were rated safe.

**Mitigations.** Larger $\beta$; stop earlier on a KL budget; a better or larger reward model;
ensembles of reward models; held-out evaluations to detect it at all.

## 6.2 Mode collapse

**Symptom.** Entropy falls sharply; sampled responses become near-identical; diversity metrics
collapse.

**Cause.** The policy concentrates on one high-reward response. Once entropy is gone there is
nothing left to explore with, so learning stalls — the lecture's "need diversity in
completions."

**Mitigations.** Entropy bonus ($c_2 > 0$); larger $\beta$; lower learning rate; verify you are
not accidentally sampling greedily or with aggressive truncation.

## 6.3 Value function failure

**Symptom.** Explained variance near zero; value loss flat or rising.

**Cause.** The value model's targets are non-stationary (Section 4.9), and it can simply fail
to track them — especially with sparse terminal rewards and long sequences.

**Consequence.** The advantages degrade toward unbaselined returns, variance explodes, and the
policy gradient becomes very noisy.

**Mitigations.** Higher value learning rate; value clipping; more value epochs; initialize the
value model from the reward model rather than the SFT model; or drop the value model and switch
to a group baseline (GRPO/RLOO).

## 6.4 KL explosion

**Symptom.** KL from $\pi_{\text{ref}}$ grows rapidly; output becomes incoherent.

**Cause.** $\beta$ too small, learning rate too high, or clipping insufficient to restrain the
update.

**Mitigations.** Adaptive $\beta$ (Section 5.4); KL early stopping; lower learning rate; fewer
`ppo_epochs`.

## 6.5 The silent mismatch

**Symptom.** Training appears to run normally but the model does not improve, or degrades for
no visible reason.

**Cause.** Section 5.6 — inconsistent sampling parameters, precision, or chat template between
generation and training.

**Mitigation.** The $\rho_t = 1$ assertion on the first inner step. This single check catches
an entire family of otherwise invisible bugs.

## 6.6 Reward model distribution shift

**Symptom.** Reward scores become implausible; the reward model assigns high scores to
obviously poor responses.

**Cause.** The policy has moved outside the distribution the reward model was trained on, so
$r$ is extrapolating rather than judging.

**Mitigation.** This is the fundamental limit of offline reward modeling. The real fix is
*iterative* RLHF: periodically collect fresh preference data on the **current** policy's
outputs and retrain the reward model, so its training distribution follows the policy.

---

# Part VII — Alternatives to PPO

The lecture's stated limitations of PPO: it needs **four models**, has **many
hyperparameters**, is prone to **training instability**, has **unclear metrics**, and it is not
obvious that preference tuning needs RL at all.

## 7.1 REINFORCE

The plain policy gradient of Section 1.17, with no value model, no ratio, no clipping:

$$\nabla_\theta J = \mathbb{E}\Big[\big(R - b\big)\, \nabla_\theta \log \pi_\theta(y \mid x)\Big]$$

Simplest possible option; higher variance. Strictly on-policy, so one gradient step per batch
of samples.

## 7.2 RLOO (REINFORCE Leave-One-Out)

Sample $k$ responses per prompt and use the mean of the *others* as each one's baseline:

$$b_i = \frac{1}{k-1}\sum_{j \ne i} R_j, \qquad\qquad \hat{A}_i = R_i - b_i$$

Leaving sample $i$ out of its own baseline keeps the baseline independent of $R_i$, which
preserves unbiasedness (Section 1.18 requires $b$ not to depend on the sampled $y$). No value
model needed.

## 7.3 GRPO (Group Relative Policy Optimization)

From the DeepSeekMath work (Shao et al., 2024). **Deletes the value model** and uses
within-group statistics as the baseline. Sample $G$ responses $y_1, \ldots, y_G$ for the *same*
prompt $x$, compute rewards $R_1, \ldots, R_G$, then

$$\hat{A}_i = \frac{R_i - \operatorname{mean}(R_1, \ldots, R_G)}{\operatorname{std}(R_1, \ldots, R_G) + \varepsilon}$$

Every token in response $i$ receives the same advantage $\hat{A}_i$ — the advantage is
sequence-level, not token-level.

| | PPO | GRPO |
|---|---|---|
| models needed | 4 | **3** (no value model) |
| baseline | learned $V_\phi$ | empirical group mean |
| advantage | token-level (GAE) | sequence-level |
| samples per prompt | typically 1 | must be $8$–$64$ |

**The trade.** You stop paying for a value model — its memory, its optimizer state, and its
instability (Section 6.3) — and instead pay in generation: $G$ responses per prompt rather than
one. Given that rollouts already dominate cost, this is not obviously cheaper in compute, but
it is markedly simpler and more stable, which is why it has become dominant for
reasoning-style training.

Note also that the group baseline needs *variation* within the group. If all $G$ responses get
identical rewards then $\hat{A}_i = 0$ for all of them and that prompt contributes no gradient
at all. With binary correctness rewards this happens constantly (all correct or all wrong),
which is why prompt difficulty filtering matters for GRPO.

## 7.4 Best-of-N (BoN)

Skip RL entirely — the lecture presents this as the pragmatic baseline:

$$y^\star = \operatorname*{arg\,max}_{y \in \{y_1, \ldots, y_N\}} r(x, y), \qquad y_i \sim \pi_{\text{sft}}(\cdot \mid x)$$

```
prompt -> LLM_SFT -> response A -> RM -> 0.8   <- return this
                  -> response B -> RM -> -2.0
                  -> response C -> RM -> 0.2
```

**Pros.** No training at all, no instability, no hyperparameters, and it is a surprisingly
strong baseline that RLHF papers are expected to beat.

**Cons.** Costs $N$ times more compute at *inference* time, on every request, forever. RLHF
pays once at training time. This is the lecture's "Best-of-N is costly at inference time."

BoN is also a useful conceptual tool: it upper-bounds what you can extract from a given reward
model without moving the policy at all, so it separates "is my reward model good?" from "is my
RL working?"

## 7.5 DPO (Direct Preference Optimization)

From Rafailov et al. (2023). Removes RL entirely and trains on preference pairs with a
supervised loss:

$$\mathcal{L}_{\text{DPO}} = -\,\mathbb{E}_{(x, y_w, y_l) \sim \mathcal{D}} \left[ \log \sigma\left( \beta \log \frac{\pi_\theta(y_w \mid x)}{\pi_{\text{ref}}(y_w \mid x)} - \beta \log \frac{\pi_\theta(y_l \mid x)}{\pi_{\text{ref}}(y_l \mid x)} \right) \right]$$

### The derivation, in the five steps the lecture gives

**Step 1 — start from the PPO objective.**

$$\max_\theta \; \mathbb{E}_{x \sim \mathcal{D},\, y \sim \pi_\theta}\big[r(x,y)\big] - \beta\, D_{\text{KL}}\big(\pi_\theta \parallel \pi_{\text{ref}}\big)$$

**Step 2 — derive the optimal policy.** This KL-regularized objective has a known closed-form
solution:

$$\pi^\star(y \mid x) = \frac{1}{Z(x)}\, \pi_{\text{ref}}(y \mid x) \exp\!\left(\frac{r(x,y)}{\beta}\right), \qquad Z(x) = \sum_y \pi_{\text{ref}}(y \mid x) \exp\!\left(\frac{r(x,y)}{\beta}\right)$$

Intuitively: start from the reference distribution and exponentially tilt it toward high
reward, with $\beta$ controlling how sharp the tilt is. $Z(x)$ is the partition function.

**Step 3 — identify a "reward" term.** Solve that expression for $r$:

$$r(x,y) = \beta \log \frac{\pi^\star(y \mid x)}{\pi_{\text{ref}}(y \mid x)} + \beta \log Z(x)$$

This is the pivotal observation: **any policy implicitly defines a reward**, recoverable as
$\beta$ times the log-ratio against the reference. The lecture's phrase "your language model is
secretly a reward model" is precisely this.

**Step 4 — write the Bradley-Terry formulation for this reward.** Using Section 1.20, and here
is the crucial cancellation — $Z(x)$ depends only on $x$, not on $y$, so it appears in both
terms and **cancels in the difference**:

$$r(x,y_w) - r(x,y_l) = \beta \log \frac{\pi^\star(y_w \mid x)}{\pi_{\text{ref}}(y_w \mid x)} - \beta \log \frac{\pi^\star(y_l \mid x)}{\pi_{\text{ref}}(y_l \mid x)}$$

The intractable partition function disappears. This is what makes DPO possible at all.

**Step 5 — infer the loss.** Replace $\pi^\star$ with the trainable $\pi_\theta$ and take the
negative log-likelihood, giving $\mathcal{L}_{\text{DPO}}$ above.

### What DPO gains and loses

| | PPO-based RLHF | DPO |
|---|---|---|
| training | multi-stage RL | single supervised stage |
| extra models | reward + value + ref (3) | ref only (1) |
| sampling during training | **yes**, on-policy rollouts | **no**, fixed dataset |
| reward model | trained separately | implicit, never materialized |
| data | prompts (responses sampled) | fixed preference pairs |

**The core structural difference.** DPO is off-policy: it only ever sees responses in its
dataset. It cannot discover a good response absent from the data, because it never generates
anything. PPO explores its own output distribution and can find behaviors no human
demonstrated. That is PPO's real advantage, and the reason on-policy methods persist despite
their cost.

**Which to use.** As the lecture concludes, there is no absolute consensus (see Xu et al.,
2024, "Is DPO Superior to PPO for LLM Alignment?"). Performance varies by task and is sensitive
to implementation. DPO is far easier to run correctly; PPO-style on-policy methods tend to win
when you have a good reward signal and enough compute to use it. Notably, the shift toward
*verifiable* rewards has moved the field back toward on-policy methods (GRPO), because when the
reward is a unit test rather than a preference model, exploration pays off.

## 7.6 Note on tool use and verifiable rewards

Tool use (search, code execution, shell) is trained through this same pipeline, with two
modifications worth recording.

**SFT teaches the format; RL teaches the decisions.** Supervised demonstrations efficiently
teach the *syntax*: emit a structured call, produce schema-valid arguments, read the result as
context. What SFT teaches poorly is *judgment* — whether to call a tool at all, which one, what
arguments, when to stop, and how to recover from an error. Those are sequential decisions with
delayed consequences, which is what RL is for.

**The reward becomes verifiable rather than preference-based.** For alignment, "good" is a
matter of taste, so you need a Bradley-Terry reward model. For tool use the outcome is often
machine-checkable: did it compile, did the tests pass, did the answer match, did the command
exit zero. The frozen reward *model* $r$ is then replaced by a *program*. This is usually
called RLVR (RL with verifiable rewards), and it eliminates the reward-model-hacking concern of
Section 6.1 — you cannot sweet-talk a compiler. It introduces a different exploit surface,
though: writing code that special-cases the tests instead of solving the problem. The
vulnerability moves from the judge's taste to the specification's loopholes.

**How the rollout changes.** Generation is no longer one uninterrupted stream; it pauses for the
environment:

```
x
  -> pi_theta samples tokens ... <search: "...">
  -> STOP. execute the tool. get real output from the world.
  -> append the result to the context
  -> pi_theta resumes ... <python: "...">
  -> STOP. run it. it may throw.
  -> append the traceback
  -> pi_theta resumes ... final answer
  -> verify. reward.
```

This is the first point at which the lecture's "Environment" box does real work. In plain RLHF
the environment merely appends a token (Section 2.2); with tools it has genuine state, latency,
and failure modes, and it returns information the model could not have predicted.

**Everything else carries over unchanged**: sampling from $\pi_\theta$, the ratio against
$\pi_{\theta_{\text{old}}}$, clipping, and the KL anchor to $\pi_{\text{ref}}$ (which is what
stops the model from forgetting how to write prose while learning to call tools). The two things
to get right are the loss masking of Section 5.1 and the credit assignment problem, which is much
harder over long trajectories — a strong argument for sequence-level group baselines here.

---

# Part VIII — Fully Worked Numerical Example

One complete PPO iteration, end to end. Vocabulary of four tokens, one prompt, one three-token
response.

**Setup.** Prompt `x = "Rate this:"`, vocabulary
$\{$`" good"`, `" bad"`, `" ok"`, `EOS`$\}$, and hyperparameters

$$\beta = 0.1, \quad \gamma = 1.0, \quad \lambda = 0.95, \quad \epsilon = 0.2, \quad c_1 = 0.5, \quad c_2 = 0$$

### Step 1 — rollout

At each position the policy produces a distribution; we sample with inverse CDF.

```
POSITION 1, context = "Rate this:"
  p = [" good"=0.50, " bad"=0.20, " ok"=0.25, EOS=0.05]
  cumulative = [0.50, 0.70, 0.95, 1.00]
  u = 0.62  ->  falls in [0.50, 0.70)  ->  sample " bad"
  log pi_theta_old(1) = log(0.20) = -1.609

POSITION 2, context = "Rate this: bad"
  p = [" good"=0.10, " bad"=0.15, " ok"=0.70, EOS=0.05]
  cumulative = [0.10, 0.25, 0.95, 1.00]
  u = 0.31  ->  falls in [0.25, 0.95)  ->  sample " ok"
  log pi_theta_old(2) = log(0.70) = -0.357

POSITION 3, context = "Rate this: bad ok"
  p = [" good"=0.05, " bad"=0.05, " ok"=0.10, EOS=0.80]
  cumulative = [0.05, 0.10, 0.20, 1.00]
  u = 0.88  ->  falls in [0.20, 1.00)  ->  sample EOS
  log pi_theta_old(3) = log(0.80) = -0.223
```

So the sampled response is `" bad ok"` followed by `EOS`, with
$\log \pi_{\theta_{\text{old}}} = (-1.609,\; -0.357,\; -0.223)$ and

$$\log \pi_{\theta_{\text{old}}}(y \mid x) = -1.609 - 0.357 - 0.223 = -2.189, \qquad \pi_{\theta_{\text{old}}}(y \mid x) = e^{-2.189} = 0.112$$

Note the sequence probability came out of a **sum** of log-probs, per Section 1.11 — never a
product of probabilities.

### Step 2 — scoring

$$r(x, y) = -1.50 \qquad \text{(a negative response scored poorly)}$$

Reference log-probs from the frozen SFT model on the same tokens:
$\log \pi_{\text{ref}} = (-2.303,\; -0.511,\; -0.223)$ — that is, $\pi_{\text{ref}}$ gave
`" bad"` probability $0.10$, which the policy has boosted to $0.20$.

Value predictions: $V = (-0.80,\; -1.00,\; -1.20)$.

### Step 3 — per-token rewards

$$
\begin{aligned}
\text{kl}_1 &= -1.609 - (-2.303) = 0.693 \\
\text{kl}_2 &= -0.357 - (-0.511) = 0.154 \\
\text{kl}_3 &= -0.223 - (-0.223) = 0.000
\end{aligned}
$$

Position 1 shows the policy drifting *upward* on `" bad"` relative to the reference;
position 3 shows no drift at all on `EOS`.

With $R_t = -\beta\,\text{kl}_t$ and the terminal reward added at $t = 3$:

$$R = \big(-0.0693,\; -0.0154,\; -0.0000 + (-1.50)\big) = \big(-0.0693,\; -0.0154,\; -1.5000\big)$$

### Step 4 — GAE advantages

```
V = [-0.80, -1.00, -1.20]

t=3:  V_next = 0 (terminal)
      delta_3 = -1.5000 + 1.0*0     - (-1.20) = -0.300
      A_3     = -0.300 + 0.95*0              = -0.300

t=2:  V_next = V_3 = -1.20
      delta_2 = -0.0154 + (-1.20)   - (-1.00) = -0.2154
      A_2     = -0.2154 + 0.95*(-0.300)      = -0.5004

t=1:  V_next = V_2 = -1.00
      delta_1 = -0.0693 + (-1.00)   - (-0.80) = -0.2693
      A_1     = -0.2693 + 0.95*(-0.5004)     = -0.7447
```

$$\hat{A} = \big(-0.7447,\; -0.5004,\; -0.3000\big), \qquad \text{returns} = \hat{A} + V = \big(-1.5447,\; -1.5004,\; -1.5000\big)$$

All advantages are **negative**: this response was worse than the value model expected, so
every token will be pushed *down*. Note how the bad terminal reward propagated backwards
through the reverse scan to reach position 1 — that is credit assignment working.

### Step 5 — ratio, after one gradient step has moved the policy

Suppose the first inner epoch has already nudged the weights, and the current policy now
assigns $\pi_\theta(\text{`` bad''}) = 0.14$, $\pi_\theta(\text{`` ok''}) = 0.66$,
$\pi_\theta(\text{EOS}) = 0.82$:

| $t$ | $\log \pi_\theta$ | $\log \pi_{\theta_{\text{old}}}$ | $\log \rho_t$ | $\rho_t$ |
|---|---|---|---|---|
| 1 | $-1.966$ | $-1.609$ | $-0.357$ | $0.700$ |
| 2 | $-0.416$ | $-0.357$ | $-0.059$ | $0.943$ |
| 3 | $-0.198$ | $-0.223$ | $+0.025$ | $1.025$ |

The policy has already reduced `" bad"` from $0.20$ to $0.14$ — responding to the negative
advantage, as intended.

### Step 6 — clipping

With $\epsilon = 0.2$ the band is $[0.8,\, 1.2]$.

```
POSITION 1:  ratio = 0.700,  A = -0.7447    (A < 0, ratio BELOW the band)
   unclipped:  0.700 * (-0.7447) = -0.5213
   clipped:    clip(0.700, 0.8, 1.2) = 0.800
               0.800 * (-0.7447) = -0.5958
   min(-0.5213, -0.5958) = -0.5958    <- CLIPPED branch selected
   => gradient is ZERO here. "You have suppressed ' bad' enough for now."

POSITION 2:  ratio = 0.943,  A = -0.5004    (inside the band)
   unclipped:  0.943 * (-0.5004) = -0.4718
   clipped:    same value
   min = -0.4718                      <- unclipped, gradient FLOWS

POSITION 3:  ratio = 1.025,  A = -0.3000    (inside the band)
   unclipped:  1.025 * (-0.3000) = -0.3075
   clipped:    same value
   min = -0.3075                      <- unclipped, gradient FLOWS
```

$$L^{\text{CLIP}} = \tfrac{1}{3}\big(-0.5958 - 0.4718 - 0.3075\big) = -0.4584$$

Position 1 is the instructive one. The policy pushed `" bad"` down hard enough that the ratio
left the trust region, so PPO cut the gradient there — exactly the behavior in Section 4.8's
Case B. Positions 2 and 3 are still within budget and keep learning.

### Step 7 — value loss

Suppose the value model now predicts $V^{\text{new}} = (-1.20,\; -1.30,\; -1.40)$ against
targets $\text{returns} = (-1.5447,\; -1.5004,\; -1.5000)$:

$$L^{V} = \tfrac{1}{3}\Big(0.3447^2 + 0.2004^2 + 0.1000^2\Big) = \tfrac{1}{3}\big(0.1188 + 0.0402 + 0.0100\big) = 0.0563$$

### Step 8 — total loss

$$L^{\text{total}} = -L^{\text{CLIP}} + c_1 L^{V} - c_2 H = 0.4584 + 0.5(0.0563) - 0 = 0.4865$$

### Step 9 — update

Backpropagate $L^{\text{total}}$, clip the gradient norm to $1.0$, step both optimizers.

**Net effect of this iteration.** The reward model disliked the response, so all advantages
were negative, and the policy reduced the probability of the tokens it sampled. The KL term
additionally penalized position 1, where the policy had drifted furthest from the SFT
reference. Clipping then prevented position 1 from being pushed any further in a single batch.
All three mechanisms visible in one example.

---

# Part IX — Glossary

| term | meaning |
|---|---|
| **advantage** $\hat{A}_t$ | reward minus baseline; how much better an action was than expected. Its sign determines whether to boost or suppress. |
| **autoregressive** | generating one token at a time, each conditioned on all previous tokens. |
| **baseline** | a quantity subtracted from the reward to reduce gradient variance without introducing bias. |
| $\beta$ | the KL penalty coefficient; controls how tightly the policy is anchored to the reference. |
| **BoN (Best-of-N)** | generate $N$ responses, return the highest reward-model score. No training; costs $N\times$ at inference. |
| **bootstrapping** | using your own value estimate as part of the target for another value estimate. |
| **Bradley-Terry** | the model converting pairwise comparisons into a scalar scale: $P(A \succ B) = \sigma(r_A - r_B)$. |
| **categorical distribution** | a distribution over a finite set of unordered outcomes. An LLM emits one per token position. |
| **chain rule (probability)** | $P(a,b,c) = P(a)P(b\mid a)P(c\mid a,b)$; the factorization enabling autoregressive generation. |
| **clip fraction** | share of tokens where PPO clipping activated. A key diagnostic metric. |
| **clipping (PPO)** | bounding the importance ratio to $[1-\epsilon, 1+\epsilon]$. Distinct from gradient-norm clipping. |
| **DPO** | Direct Preference Optimization. Replaces RL with a supervised loss on preference pairs. |
| **entropy** $H$ | a measure of a distribution's uncertainty. Falling entropy signals mode collapse. |
| **EOS** | end-of-sequence token; terminates generation. |
| **expectation** | probability-weighted average. The RLHF objective is one. |
| **explained variance** | $1 - \operatorname{Var}[\text{returns} - V]/\operatorname{Var}[\text{returns}]$; whether the value model predicts anything. |
| **GAE** | Generalized Advantage Estimation; exponentially-weighted average of $k$-step estimates, tuned by $\lambda$. |
| **Goodhart's law** | when a measure becomes a target it ceases to be a good measure. The core hazard of RLHF. |
| **greedy decoding** | always take the argmax token. Deterministic; not used for PPO rollouts. |
| **GRPO** | Group Relative Policy Optimization. Drops the value model; uses the within-group mean reward as baseline. |
| **Gumbel-max** | sampling by adding Gumbel noise to logits and taking the argmax. Equivalent to categorical sampling. |
| **importance sampling** | reweighting samples from one distribution to estimate an expectation under another. Source of PPO's ratio. |
| **KL divergence** | an asymmetric measure of how different two distributions are. |
| **logits** $\ell_i$ | the model's raw pre-softmax outputs. Unconstrained reals. |
| **log-prob** | $\log p$; always $\le 0$. Used everywhere instead of raw probabilities for numerical stability. |
| **MDP** | Markov Decision Process; the formal framework for RL. |
| **MLE** | maximum likelihood estimation. The objective of pretraining, SFT, reward modeling, and DPO — but *not* PPO. |
| **mode collapse** | the policy concentrating on a single output; $H \to 0$. |
| **Monte Carlo** | estimating an expectation by averaging over samples. |
| **nucleus sampling** | see top-$p$. |
| **off-policy** | training on data generated by a different policy. |
| **on-policy** | training on data generated by the current policy. PPO is approximately on-policy. |
| **overoptimization** | reward improving while true quality degrades. |
| $\pi_{\text{ref}}$ | the frozen reference model (the SFT checkpoint); the long-horizon anchor for the KL penalty. |
| $\pi_\theta$ | the current, trainable policy. |
| $\pi_{\theta_{\text{old}}}$ | the policy snapshot taken at generation time; the ratio's denominator. |
| **policy** | the distribution over actions given a state; here, the LLM's next-token distribution. |
| **policy gradient** | $\nabla_\theta J = \mathbb{E}[R \nabla_\theta \log \pi_\theta]$; the score function estimator. |
| **PPO** | Proximal Policy Optimization. "Proximal" = keep the new policy near the old one. |
| `ppo_epochs` | number of gradient passes over one rollout batch (1–4). |
| **ratio** $\rho_t$ | $\pi_\theta / \pi_{\theta_{\text{old}}}$ for a token. *Not* the reward, despite the literature's overloaded $r$. |
| **reward hacking** | exploiting flaws in the reward model to score well without being good. |
| **reward model (RM)** | a model trained on preference pairs that scores $(x,y)$ pairs. |
| **RLHF** | Reinforcement Learning from Human Feedback. |
| **RLVR** | RL with Verifiable Rewards; the reward is a program (tests, a checker) rather than a learned model. |
| **RLOO** | REINFORCE with a leave-one-out baseline. |
| **rollout** | generating responses with the current policy; the sampling phase of a PPO iteration. |
| **softmax** | converts logits into a normalized distribution. |
| **SFT** | Supervised Fine-Tuning; the stage before preference tuning. |
| **temperature** $T$ | logit scaling that sharpens ($T<1$) or flattens ($T>1$) the sampling distribution. Must match between generation and log-prob computation. |
| **TD error** $\delta_t$ | $R_t + \gamma V(s_{t+1}) - V(s_t)$; the "surprise". |
| **top-$k$ / top-$p$** | truncated sampling; sets the distribution's tail to *exactly* zero, making unlikely tokens unselectable. |
| **trust region** | a constraint keeping updates within a region where your approximations remain valid. |
| **value model** $V_\phi$ | predicts expected future reward from a state; supplies PPO's baseline. Trained jointly with the policy. |
| **whitening** | subtracting the mean and dividing by the standard deviation. |
| $y \sim \pi_\theta(y \mid x)$ | "the response $y$ is **sampled from the policy**, conditioned on prompt $x$." Not a dataset label — text the model just generated. This is what makes PPO on-policy. |

---

# Part X — Open Questions (Question Bank)

## Q1. Why so few epochs in PPO, per prompt?

**Short answer.** Reward hacking (Sections 1.22 and 6.1). The reward model is a learned proxy
fitted on order $10^4$ comparisons, accurate only near the SFT distribution. PPO is an
optimizer, so it actively seeks the regions where the proxy is highest — which are
disproportionately the regions where the proxy is *wrong*. The longer you optimize, the further
the policy moves from where the reward model was validated.

The three nested levels, for reference:

| level | how many |
|---|---|
| inner passes over a rollout batch (`ppo_epochs`) | 1 to 4 |
| passes over the prompt dataset | usually 1, sometimes 2 |
| the reward model's own training | exactly 1 (it overfits beyond) |

**Still to dig into:**

- How is the KL budget threshold chosen in practice? Is it tuned per task, or are there
  transferable defaults?
- Empirically, at what KL from the reference does true quality start degrading, and how does
  that scale with model size?
- How does `ppo_epochs` interact with clipping quantitatively? Is `ppo_epochs = 1` (strictly
  on-policy, clipping inert) generally better if you can afford the generation?
- Does iterative RLHF — periodically refreshing the reward model on the current policy's
  outputs — actually let you train for meaningfully longer?

## Q2. Credit assignment over long, multi-step trajectories

When a twenty-step tool-using trajectory ends in a single failure signal, how is credit assigned
to the individual steps? The token-level value model struggles over long branching trajectories
(Section 6.3), which is one motivation for sequence-level group baselines. Open: what actually
works for long-horizon agentic RL, and how do process rewards (scoring intermediate steps)
compare to outcome-only rewards?

---

## References

- Schulman et al., 2017. *Proximal Policy Optimization Algorithms.*
- Schulman et al., 2015. *High-Dimensional Continuous Control Using Generalized Advantage
  Estimation.*
- Ouyang et al., 2022. *Training language models to follow instructions with human feedback.*
  (InstructGPT — the source of the RLHF objective used here.)
- Bradley & Terry, 1952. *The rank analysis of incomplete block designs: I. The method of paired
  comparisons.*
- Rafailov et al., 2023. *Direct Preference Optimization: Your Language Model is Secretly a
  Reward Model.*
- Shao et al., 2024. *DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open
  Language Models.* (GRPO.)
- Lambert et al., 2024. *RewardBench: Evaluating Reward Models for Language Modeling.*
- Xu et al., 2024. *Is DPO Superior to PPO for LLM Alignment? A Comprehensive Study.*
- Amidi & Amidi. *CME 295: Transformers & Large Language Models*, Lecture 5.




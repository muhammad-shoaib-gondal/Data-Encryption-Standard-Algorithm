# PPO and RLHF: A Complete, Detailed Guide

Companion notes for CME 295 (Transformers & Large Language Models), Lecture 5:
Preference Tuning — Data Collection, RLHF, DPO.

These notes are deliberately exhaustive. Every symbol is defined, every statistical
concept used anywhere in the pipeline is explained from first principles, and every
formula is written in plain ASCII inside code blocks (no LaTeX) so it renders
identically everywhere.

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

```
x            a prompt (sequence of input tokens)
y            a response / completion (sequence of generated tokens)
y_t          the t-th token of the response
y_<t         all response tokens before position t
|y|          number of tokens in the response
T            the final token index of a response (= |y|); also temperature (context disambiguates)
V            vocabulary size (e.g. ~128,000)
D            the dataset of prompts
theta        the trainable parameters of the policy
phi          the trainable parameters of the value model

pi_theta(y|x)        the policy: probability of full response y given prompt x
pi_theta(y_t|x,y_<t) the policy: probability of a single next token
pi_theta_old         snapshot of the policy at generation time
pi_ref               frozen reference model (the SFT checkpoint)
pi_sft               the SFT model (= pi_ref at initialization)

r(x, y)      the reward model's scalar score for a complete (prompt, response) pair
R_t          the per-token reward used by the RL algorithm at position t
V_phi(s_t)   the value model's prediction at state s_t
A_t          the advantage at position t
delta_t      the temporal-difference (TD) error at position t
ratio_t      pi_theta(y_t|...) / pi_theta_old(y_t|...)

beta         KL penalty coefficient
eps          PPO clipping parameter (commonly 0.2)
gamma        discount factor
lambda       GAE smoothing parameter
c1, c2       loss weights for the value term and entropy term

y_w          the preferred ("winning") response in a preference pair
y_l          the dispreferred ("losing") response in a preference pair

E[...]       expectation (average)
Var[...]     variance
sigmoid(z)   1 / (1 + exp(-z))
1[cond]      indicator: 1 if cond is true, else 0
```

## 0.2 Reading conventions

All math is plain ASCII inside code blocks. A few conventions:

- `~` means "is distributed as" / "is sampled from". So `y ~ pi_theta(.|x)` reads
  "y is sampled from the distribution pi_theta conditioned on x".
- `.` inside a distribution's argument, as in `pi_theta(.|x)`, marks the slot that
  varies. `pi_theta(.|x)` is the *whole distribution*; `pi_theta(y|x)` is a *single
  number*, the probability of one specific y.
- `:=` means assignment (as in code), not equality.
- `prod` is a product over a range; `sum` is a summation over a range.
- `log` is the natural logarithm throughout.

That distinction in the second bullet matters more than it looks. The expression
`pi_theta(y|x)` does double duty in PPO: as a *distribution* you sample from, and as a
*number* you compute gradients of. Most confusion about the objective traces back to
conflating those two uses.

---

# Part I — Statistical Foundations

This part assumes no probability background and builds up everything PPO needs.

## 1.1 Random variables and distributions

A **random variable** is a quantity whose value is not determined until it is
observed. A **distribution** describes how likely each possible value is.

For our purposes, everything is **discrete**: the next token is one of `V` choices.
A discrete distribution is fully described by a list of probabilities, one per
outcome, satisfying two rules:

```
(1)  p_i >= 0            for every outcome i          (no negative probabilities)
(2)  sum_i p_i = 1                                    (something must happen)
```

Rule (2) is called normalization. Anything violating it is not a distribution.

**Why this matters for LLMs.** A language model's final layer produces `V` real
numbers called **logits**, which are unconstrained — they can be negative, large,
anything. They are *not* a distribution. The softmax function (Section 1.10) is what
converts them into one.

## 1.2 The categorical distribution

The **categorical distribution** is the distribution over a finite set of unordered
outcomes. It is the single most important distribution in this entire document,
because *a language model is a categorical distribution generator*. At every token
position, the model outputs one categorical distribution over the vocabulary.

```
Categorical(p_1, p_2, ..., p_V)

outcome:       token 1   token 2   ...   token V
probability:     p_1       p_2     ...     p_V
```

Example over a toy 4-token vocabulary:

```
token      probability
-------    -----------
" the"        0.60
" a"          0.25
" this"       0.10
" xyzzy"      0.05
                -----
                1.00     <- normalized, as required
```

Nothing about the ordering matters. There is no notion of one token being "close to"
another in this distribution — that structure lives in the embeddings, not here.

## 1.3 Expectation

The **expectation** (or expected value, or mean) of a function `f` of a random
variable is the probability-weighted average of `f` over all outcomes:

```
E_{i ~ p}[ f(i) ]  =  sum_i  p_i * f(i)
```

Read it as: "the average value of `f`, if you drew outcomes according to `p` forever."

Worked example with the toy vocabulary above, where `f` is a reward assigned to each
token:

```
token      p       f (reward)     p * f
-------  -----   ------------   --------
" the"    0.60        1.0         0.60
" a"      0.25        0.5         0.125
" this"   0.10        2.0         0.20
" xyzzy"  0.05      -10.0        -0.50
                                 ------
                        E[f] =    0.425
```

Note what the expectation does: the terrible token pulls the average down, but only
in proportion to how likely it is. This proportional weighting is the entire logic of
the RLHF objective.

**Three properties used constantly:**

```
(1)  Linearity:        E[a*f + b*g]  =  a*E[f] + b*E[g]
(2)  Constants:        E[c]  =  c
(3)  Nested/tower:     E_x[ E_y|x [ f(x,y) ] ]  =  E_{x,y}[ f(x,y) ]
```

Property (3) is why the RLHF objective can write `E_{x ~ D, y ~ pi_theta}` as a single
expectation even though there are two sequential sampling steps.

**Where this appears in PPO.** The whole objective is an expectation:

```
maximize over theta:   E_{x ~ D, y ~ pi_theta(.|x)} [ r(x,y) - beta * log( pi_theta(y|x) / pi_ref(y|x) ) ]
```

Everything else in this document is machinery for estimating and differentiating that
one expectation.

## 1.4 Variance and standard deviation

**Variance** measures spread — how far outcomes typically fall from the mean:

```
Var[f]  =  E[ (f - E[f])^2 ]  =  E[f^2] - (E[f])^2

std[f]  =  sqrt( Var[f] )
```

The standard deviation is in the same units as `f`, which makes it the interpretable
one.

**Why variance dominates practical RL.** Every gradient in PPO is estimated from a
finite sample, so it is itself a random variable. High variance means the gradient
points in a wildly different direction each batch, and training either progresses
slowly or destabilizes. A large fraction of the design of PPO — baselines, advantage
normalization, GAE, clipping — exists to reduce variance. Keep this lens; it explains
choices that otherwise look arbitrary.

## 1.5 Bernoulli and binomial: the "60 out of 100" question

A **Bernoulli** trial is a single yes/no event with success probability `p`.

```
Var[single Bernoulli trial] = p * (1 - p)
```

A **binomial** counts successes in `n` independent Bernoulli trials:

```
E[count]   = n * p
Var[count] = n * p * (1 - p)
std[count] = sqrt( n * p * (1 - p) )
```

**Applied to token sampling.** If a token has probability 0.6 and you sample the same
distribution 100 times, how many times does it come up?

```
n = 100, p = 0.6

E[count]   = 100 * 0.6            = 60
std[count] = sqrt(100*0.6*0.4)    = sqrt(24)  ~= 4.9
```

So you expect **60, plus or minus about 5**. Roughly two thirds of the time you land
in 55–65, and about 95% of the time in 50–70. You would essentially never see exactly
60 as a guarantee.

This is the precise answer to "if we repeat 100 times will it be selected 60 times":
60 is the *expectation*, not the outcome. The spread is real and it is what provides
exploration in RL.

**Important caveat about LLM generation.** The binomial model above assumes you sample
the *same* distribution `n` times. That is NOT what happens during generation. In
generation you sample each position **once**, from a *different* distribution each
time (because the context grows). The 60% figure describes the frequency across many
independent *regenerations* of the same prompt, not repeated draws at one position.

**Scaling to full responses.** Suppose at each of 400 positions there is a 0.1%
chance of drawing a genuinely bad token. The probability that a full response contains
at least one:

```
P(at least one bad token) = 1 - (1 - 0.001)^400
                          = 1 - 0.999^400
                          ~= 1 - 0.670
                          ~= 0.33
```

A one-in-a-thousand per-token failure becomes a one-in-three per-response failure.
This compounding is exactly why truncated sampling (Section 1.13) exists.

## 1.6 The law of large numbers

The **law of large numbers** states that the sample average of independent draws
converges to the true expectation as the number of draws grows:

```
(1/N) * sum_{n=1..N} f(i_n)   ->   E[f]     as N -> infinity
```

The rate matters: the standard error of the sample mean shrinks as

```
std_error = std[f] / sqrt(N)
```

The `sqrt(N)` is unforgiving. To halve your error you need **four times** the samples.
This is the fundamental economics of RLHF: rollouts are expensive, and buying
precision by brute force gets costly fast. Hence the emphasis on variance reduction,
which improves `std[f]` instead of `N`.

## 1.7 Monte Carlo estimation

**Monte Carlo estimation** means approximating an expectation by sampling:

```
E_{y ~ pi_theta}[ f(y) ]   ~=   (1/N) * sum_{n=1..N} f(y_n)      where y_n ~ pi_theta
```

You cannot compute the RLHF expectation exactly. The sum would range over every
possible response — for a 400-token response over a 128,000-token vocabulary that is
`128000^400` terms, a number with over 2,000 digits. Exact computation is not merely
slow, it is physically impossible.

So instead: **generate a handful of responses and average.** That is what a rollout
is. Sampling is not an approximation shortcut chosen for convenience; it is the only
way the objective can be touched at all.

Everything else follows. Because we estimate by sampling, the estimate is noisy.
Because it is noisy, we need variance reduction. Because we sample from the policy we
are changing, we need importance corrections. The entire structure of PPO is
downstream of this one fact.

## 1.8 Bias, variance, and estimators

An **estimator** is a rule for computing a guess of some quantity from data. Two ways
an estimator can be wrong:

```
BIAS      systematic error: the estimator converges to the WRONG value
          even with infinite data.

VARIANCE  random error: the estimator is right on average but any single
          estimate can be far off.
```

An estimator is **unbiased** if `E[estimate] = true value`.

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
best total error is frequently at a nonzero amount of bias. This shows up in at least
four places in PPO:

```
1. GAE's lambda        lambda=1 -> unbiased, high variance
                       lambda=0 -> biased, low variance
2. Truncated sampling  top-p introduces bias in the gradient estimate,
                       reduces variance from junk tokens
3. Clipping            introduces bias, dramatically reduces variance
                       from large importance ratios
4. Discounting gamma   gamma<1 biases the objective, reduces variance
```

Note the pattern: PPO accepts bias in several places to control variance. That is a
deliberate engineering position, not an oversight.

## 1.9 Conditional probability and the chain rule

**Conditional probability** `P(A|B)` is the probability of A given that B is known.

The **chain rule of probability** decomposes a joint probability into a product of
conditionals:

```
P(a, b, c)  =  P(a) * P(b|a) * P(c|a,b)
```

**This is what an autoregressive LLM is.** The model never represents the probability
of a whole response directly. It factorizes:

```
pi_theta(y|x)  =  prod_{t=1..T}  pi_theta(y_t | x, y_<t)
```

Written out for a 3-token response `y = (y_1, y_2, y_3)`:

```
pi_theta(y|x) = pi_theta(y_1 | x)
              * pi_theta(y_2 | x, y_1)
              * pi_theta(y_3 | x, y_1, y_2)
```

Each factor is one categorical distribution — one forward pass through the network.
The product over positions is the sequence probability.

**Two consequences that matter enormously:**

First, sampling a response is just sampling each factor in order. That is why
generation is a simple loop.

Second, sequence probabilities are astronomically small. A 400-token response with a
typical per-token probability of 0.1 has

```
pi_theta(y|x) ~= 0.1^400 = 10^-400
```

which **underflows to exactly 0.0 in float32** (whose smallest normal positive value
is about `10^-38`). You cannot represent sequence probabilities numerically. Which
brings us to logs.

## 1.10 Softmax and temperature

The **softmax** converts unconstrained logits into a valid distribution:

```
p_i  =  exp(l_i / T)  /  sum_{j=1..V} exp(l_j / T)
```

It satisfies both distribution rules by construction: `exp` is always positive, and
dividing by the sum forces normalization.

**Temperature `T`** rescales the logits before exponentiating, which reshapes the
distribution:

```
T -> 0      distribution collapses onto the single largest logit
            (this IS greedy decoding / argmax)
T = 1       the model's true, calibrated distribution
T > 1       distribution flattens, tail gets fatter, output more random
T -> inf    approaches uniform over the whole vocabulary
```

Concretely, with logits `[3.0, 1.0, 0.0]`:

```
T = 0.5:   [0.976, 0.018, 0.006]     sharp - nearly deterministic
T = 1.0:   [0.844, 0.114, 0.042]     the model's actual belief
T = 2.0:   [0.665, 0.245, 0.090]     flattened
T = 5.0:   [0.428, 0.287, 0.235]     approaching uniform
```

A property worth knowing: **softmax is shift-invariant.** Adding a constant `c` to
every logit changes nothing, because `exp(l_i + c) = exp(c) * exp(l_i)` and the
`exp(c)` cancels between numerator and denominator. Implementations exploit this by
subtracting `max(l)` before exponentiating, which prevents `exp` from overflowing.
This is the "log-sum-exp trick".

**Where temperature matters in PPO.** During rollouts, the temperature you generate
with defines the distribution `pi_theta` in the objective. If you generate at `T=0.7`
but compute log-probabilities at `T=1.0`, those are two different distributions and
your gradient is silently wrong. See Section 5.6 — this is a real and common bug.

## 1.11 Log probabilities and why we use them

Every implementation works with `log p`, never `p`. Four reasons:

**1. Products become sums.** The chain rule product turns into a sum:

```
log pi_theta(y|x)  =  sum_{t=1..T}  log pi_theta(y_t | x, y_<t)
```

Sums are numerically stable and trivially differentiable.

**2. Underflow disappears.** The response that had probability `10^-400`:

```
log(10^-400)  =  -400 * log(10)  ~=  -921
```

`-921` is a perfectly ordinary float. The information is preserved.

**3. Ratios become differences.** This is used everywhere in PPO:

```
ratio  =  p / q        becomes      log ratio = log p - log q
                       recovered as ratio = exp(log p - log q)
```

Every ratio and KL term in PPO is computed this way — as a difference of log-probs,
then exponentiated only at the end if needed.

**4. Better-conditioned gradients.** The gradient of `log p` with respect to logits is
clean and bounded, whereas the gradient of `p` itself vanishes for small `p`.

**Sign convention.** Since probabilities are in `[0,1]`, log-probs are in
`(-inf, 0]`. Log-probs are always **negative** (or zero for a certainty). A log-prob
of `-0.2` is a high probability (~0.82); `-10` is a low one (~0.000045).

## 1.12 How to actually sample: inverse CDF and Gumbel-max

Given a categorical distribution, how do you mechanically draw from it?

### Method 1: inverse CDF (what `torch.multinomial` does)

Build the **cumulative distribution function** and use one uniform random number:

```
1.  compute cumulative sums:   c_i = p_1 + p_2 + ... + p_i
2.  draw                        u ~ Uniform(0, 1)
3.  select the FIRST i with     c_i >= u
```

The geometric picture: cut the interval `[0,1]` into segments, one per token, where
each segment's **width equals that token's probability**. Throw a dart uniformly at
`[0,1]`; take whichever segment it hits.

```
token      p      cumulative    owns the interval
-------  -----   -----------   ------------------
" the"    0.60      0.60         [0.00, 0.60)
" a"      0.25      0.85         [0.60, 0.85)
" this"   0.10      0.95         [0.85, 0.95)
" xyzzy"  0.05      1.00         [0.95, 1.00)

|-------------------------|----------|----|--|
0.0                      0.60      0.85 0.95 1.0
         " the"            " a"   " this" " xyzzy"

u = 0.91  ->  first cumulative >= 0.91 is 0.95  ->  pick " this"
```

**Why it is correct.** The probability that a uniform `u` lands in a segment equals
that segment's width, and the width was constructed to equal `p_i`. So
`P(select i) = p_i` exactly. Width *is* probability.

**Can the least likely token be selected?** Yes. `" xyzzy"` owns `[0.95, 1.00)`, so it
is chosen 5% of the time. Any token with nonzero probability is reachable. A token
with probability `10^-9` owns a segment of width `10^-9` and appears about once per
billion draws. Proportional selection means bad tokens are picked exactly as often as
the model believes they should be — no more, no less.

### Method 2: Gumbel-max (common on GPUs)

Add independent Gumbel noise to the raw logits and take the argmax:

```
g_i  =  -log( -log( u_i ) )     with u_i ~ Uniform(0,1)      [Gumbel(0,1) noise]

selection  =  argmax_i ( l_i + g_i )
```

This provably yields a sample from the *exact* same categorical distribution as
inverse-CDF sampling. It is attractive because it needs no normalization (no softmax,
no cumulative sum) and vectorizes perfectly across a batch.

### Special case: greedy decoding

```
selection = argmax_i p_i
```

No randomness. Equivalent to `T -> 0`. **Not** used for PPO rollouts, because it makes
`y` a deterministic function of `x`: every rollout of a prompt returns the identical
response, the Monte Carlo estimate collapses onto a single point, exploration
vanishes, and the gradient stops being an unbiased estimate of the objective's
gradient.

## 1.13 Truncated sampling: top-k and top-p

Pure sampling can select any token, and over hundreds of positions the tail risk
compounds (Section 1.5). Truncation removes the tail.

**Top-k**: keep the `k` highest-probability tokens, zero the rest, renormalize.

```
k = 2 applied to our example:

before:  " the" 0.60   " a" 0.25   " this" 0.10   " xyzzy" 0.05
keep top 2:      0.60        0.25          0            0
renormalize:  0.60/0.85   0.25/0.85
           =    0.706       0.294        0.0          0.0
```

**Top-p (nucleus sampling)**: keep the smallest set of highest-probability tokens
whose total mass reaches `p_threshold`, then renormalize.

```
S = smallest set (by descending probability) such that sum_{i in S} p_i >= p_threshold

p_i  <-  p_i * 1[i in S]  /  sum_{j in S} p_j
```

```
p_threshold = 0.9 applied to our example:

" the"    0.60   cumulative 0.60   < 0.9  -> keep, continue
" a"      0.25   cumulative 0.85   < 0.9  -> keep, continue
" this"   0.10   cumulative 0.95  >= 0.9  -> keep, STOP
" xyzzy"  0.05                            -> discard

renormalized: 0.632, 0.263, 0.105, 0.0
```

**The key property.** Both methods set the tail to **exactly zero**, not merely small.
The least likely token becomes genuinely unselectable rather than improbable. This is
the direct answer to the tail-risk problem.

**Why top-p is usually preferred.** It adapts to the model's confidence:

```
context: "The capital of France is"
   model is confident -> nucleus contains ~1 token -> effectively deterministic

context: "Once upon a time, there"
   model is uncertain -> nucleus contains hundreds -> genuine diversity
```

Top-k cannot do this; a fixed `k` is too permissive when the model is confident and
too restrictive when it is not.

**The catch for PPO.** The objective is an expectation over `y ~ pi_theta(.|x)`,
meaning the *untruncated* distribution. The moment you truncate, you sample from a
different distribution than the one appearing in the ratio and KL terms, and the
gradient estimator becomes **biased**. Standard practice is therefore to run PPO
rollouts at `T = 1.0` with little or no truncation, relying on the SFT
initialization to already place negligible mass on garbage.

## 1.14 Entropy

**Entropy** measures the uncertainty (or spread, or "randomness") of a distribution:

```
H(p)  =  - sum_i  p_i * log p_i
```

Bounds:

```
H = 0                      a certainty (one token has p=1)
H = log(V)                 uniform over the whole vocabulary (maximum)
```

For our toy example:

```
H = -(0.60*log(0.60) + 0.25*log(0.25) + 0.10*log(0.10) + 0.05*log(0.05))
  = -(0.60*(-0.511) + 0.25*(-1.386) + 0.10*(-2.303) + 0.05*(-3.000))
  = -(-0.3066 - 0.3466 - 0.2303 - 0.1500)
  = 1.033 nats
```

("nats" because we used natural log; with log base 2 the unit is bits.)

**Why PPO tracks entropy.** Entropy is the early-warning signal for **mode collapse**.
If the policy discovers one response that scores well, it can concentrate all
probability there, driving entropy toward zero. At that point sampling returns the
same text every time, there is no exploration left, and learning stops. The optional
**entropy bonus** in the loss (Section 4.10) adds `+c2 * H` to reward the policy for
staying uncertain. Falling entropy in your logs is one of the most reliable indicators
that a run is going wrong.

## 1.15 KL divergence

The **Kullback-Leibler divergence** measures how different one distribution is from
another:

```
KL( p || q )  =  sum_i  p_i * log( p_i / q_i )   =   E_{i ~ p} [ log( p_i / q_i ) ]
```

Read `KL(p || q)` as "the divergence of `p` from reference `q`". Properties:

```
1.  KL >= 0 always                          (Gibbs' inequality)
2.  KL = 0  if and only if  p == q
3.  ASYMMETRIC:  KL(p||q)  !=  KL(q||p)     it is NOT a distance metric
4.  KL(p||q) = infinity if q_i = 0 where p_i > 0
```

Property 3 is not a technicality — it determines behavior. `KL(p||q)` averages over
samples from `p`, so it heavily penalizes `p` putting mass where `q` has little. It is
"mode-seeking" in the direction that keeps `p` inside `q`'s support.

**In PPO** we penalize `KL(pi_theta || pi_ref)`:

```
KL( pi_theta || pi_ref )  =  E_{y ~ pi_theta} [ log pi_theta(y|x) - log pi_ref(y|x) ]
```

The ordering is deliberate. We sample from `pi_theta` (that is what a rollout gives
us), and we want to punish the policy for placing probability on text the reference
model considers unlikely. That is precisely the direction that catches drift into
degenerate, reward-hacked output.

**Sequence-level vs token-level.** In practice this is computed per token and summed,
using the log-prob decomposition:

```
per-token:  kl_t  =  log pi_theta(y_t | x, y_<t)  -  log pi_ref(y_t | x, y_<t)
sequence:   KL    =  sum_t kl_t
```

**Note on terminology.** What PPO computes is a single-sample *estimate* of the KL,
not the full sum over the vocabulary. It is unbiased in expectation but can be
negative for an individual token, which surprises people who know `KL >= 0`. The
inequality holds for the true KL, not for a one-sample estimate. Section 5.3 covers
better estimators.

## 1.16 Importance sampling

**The problem it solves:** you want an expectation under distribution `p`, but your
samples came from a different distribution `q`.

**The identity:**

```
E_{y ~ p}[ f(y) ]  =  sum_y p(y) * f(y)
                   =  sum_y q(y) * [ p(y)/q(y) ] * f(y)
                   =  E_{y ~ q} [ ( p(y)/q(y) ) * f(y) ]
```

The derivation is just multiplying by `q(y)/q(y)`. The factor `p(y)/q(y)` is the
**importance weight**: it reweights each sample to correct for having drawn from the
wrong distribution. A sample that `q` overproduces relative to `p` gets down-weighted,
and vice versa.

**Requirement:** `q(y) > 0` wherever `p(y) > 0`. If `q` can never produce a sample
that `p` cares about, no reweighting can fix it.

**This is exactly where PPO's ratio comes from.** You generate with `pi_theta_old`,
then take several gradient steps, so by step two your samples are stale — they came
from `pi_theta_old` but you want an expectation under the current `pi_theta`:

```
E_{y ~ pi_theta}[ A ]  =  E_{y ~ pi_theta_old} [ ( pi_theta(y|x) / pi_theta_old(y|x) ) * A ]
                                                  \___________________________________/
                                                              ratio_t
```

**The catastrophe importance sampling is prone to.** If `p` and `q` differ much, the
weights have enormous variance. A single sample with weight 1000 dominates the entire
batch average, and the estimate becomes garbage.

```
ratio = 1.0     samples perfectly on-policy, estimate is clean
ratio = 1.2     mild staleness, fine
ratio = 50      one sample now dominates the batch, estimate is meaningless
```

**And that is the justification for clipping.** PPO bounds the importance weight to
`[1-eps, 1+eps]` and thereby bounds the variance. It introduces bias (the clipped
estimator is no longer unbiased) in exchange for not blowing up. Section 1.8's
tradeoff, made concrete.

## 1.17 The score function estimator (REINFORCE)

We need the gradient of an expectation whose *distribution* depends on the parameters:

```
J(theta)  =  E_{y ~ pi_theta}[ R(y) ]
```

The difficulty: you cannot simply push the gradient inside, because `theta` controls
which samples you get, not just the values.

**The derivation** (the "log-derivative trick"):

```
grad_theta J  =  grad_theta  sum_y pi_theta(y) * R(y)

              =  sum_y  [ grad_theta pi_theta(y) ] * R(y)

                                    grad_theta pi_theta(y)
              =  sum_y pi_theta(y) * ---------------------- * R(y)
                                        pi_theta(y)

              =  sum_y pi_theta(y) * [ grad_theta log pi_theta(y) ] * R(y)

              =  E_{y ~ pi_theta} [ R(y) * grad_theta log pi_theta(y) ]
```

The third step multiplies and divides by `pi_theta(y)`. The fourth uses the identity
`grad log f = (grad f) / f`.

**The result — the policy gradient theorem:**

```
grad_theta J  =  E_{y ~ pi_theta} [ R(y) * grad_theta log pi_theta(y) ]
```

This is remarkable and worth pausing on. The right-hand side is an expectation you
can estimate by sampling, and `grad log pi_theta` is just backprop through the model's
own log-probability output. `R(y)` need not be differentiable at all — it can be a
neural reward model, a unit test, or a human. The gradient flows only through the
policy's log-prob.

**Interpretation.** `grad log pi_theta(y)` is the direction in parameter space that
makes `y` more likely. Multiplying by `R(y)`:

```
R(y) > 0   ->  step in that direction  ->  make y MORE likely
R(y) < 0   ->  step against it         ->  make y LESS likely
```

The magnitude of `R` sets the step size. That is the whole mechanism: **reinforce what
scored well, suppress what scored badly, proportionally.**

**The problem with using this directly.** Its variance is enormous. Consider rewards
that are all positive, say every response scores between +8 and +10. Then every
gradient term pushes *up* on every sampled response, including the mediocre ones. The
learning signal — that +10 is better than +8 — is a small difference riding on a large
common offset. Which leads directly to baselines.

## 1.18 Baselines and variance reduction

**The key theorem:** subtracting any function `b(x)` that does not depend on `y`
leaves the gradient unbiased.

```
grad_theta J  =  E [ ( R(y) - b(x) ) * grad_theta log pi_theta(y) ]
```

**Why subtracting is free.** Because the score function has zero mean:

```
E_{y ~ pi_theta} [ grad_theta log pi_theta(y) ]
     =  sum_y pi_theta(y) * grad_theta log pi_theta(y)
     =  sum_y grad_theta pi_theta(y)
     =  grad_theta sum_y pi_theta(y)
     =  grad_theta (1)
     =  0
```

So `E[ b(x) * grad log pi_theta ] = b(x) * 0 = 0`. The baseline term contributes
nothing to the expectation — but it can dramatically reduce the *variance*.

**The intuition, with numbers.** Four responses to one prompt:

```
without baseline:
  R = [8, 9, 10, 11]      every gradient pushes UP, magnitudes 8..11
                          the useful signal (spread of 3) is swamped
                          by the common offset (~9.5)

with baseline b = mean = 9.5:
  R - b = [-1.5, -0.5, +0.5, +1.5]
                          the two worse responses are pushed DOWN,
                          the two better ones UP.
                          Pure relative signal. Much lower variance.
```

**This is what "advantage" means.** The advantage is reward minus baseline, which is
the lecture's `Advantage ~ Reward - Baseline`. The two standard choices of baseline:

```
PPO:   b(x) = V_phi(x)                    a LEARNED value model
GRPO:  b(x) = mean of rewards in a group  an EMPIRICAL group average
```

PPO pays for a whole extra trained model to get its baseline. GRPO pays in extra
samples per prompt instead. Same statistical purpose, different cost structure.

## 1.19 Maximum likelihood estimation

**Maximum likelihood estimation (MLE)** picks parameters that make the observed data
most probable:

```
theta_hat  =  argmax_theta  prod_n P(data_n | theta)
           =  argmax_theta  sum_n log P(data_n | theta)        (take logs)
           =  argmin_theta  - sum_n log P(data_n | theta)      (negate to minimize)
```

The final line is the **negative log-likelihood** loss.

**Where MLE appears in this pipeline:**

```
Pretraining / SFT:   MLE of next tokens.  Loss = -sum_t log pi_theta(y_t | x, y_<t)
                     (this is exactly cross-entropy loss)

Reward modeling:     MLE under the Bradley-Terry model (next section)

DPO:                 MLE under an implicitly-defined reward

PPO:                 NOT MLE. This is the odd one out — PPO maximizes expected
                     reward, not the likelihood of any fixed dataset. Which is
                     why it needs sampling and why it behaves so differently.
```

That last row is worth internalizing. SFT asks "make this specific text more likely."
PPO asks "make whatever scores well more likely," and it has to *discover* what scores
well by generating.

## 1.20 Sigmoid, logits, and the Bradley-Terry model

The **sigmoid** (logistic) function squashes any real number into `(0,1)`:

```
sigmoid(z)  =  1 / (1 + exp(-z))

sigmoid(-inf) = 0     sigmoid(-2) = 0.119
sigmoid(0)    = 0.5   sigmoid(+2) = 0.881
sigmoid(+inf) = 1
```

Useful identities:

```
sigmoid(-z)          =  1 - sigmoid(z)
d/dz sigmoid(z)      =  sigmoid(z) * (1 - sigmoid(z))
log sigmoid(z)       =  -log(1 + exp(-z))          [ = -softplus(-z), stable form ]
```

**The Bradley-Terry model** (Bradley & Terry, 1952) models pairwise comparisons. Given
two items with real-valued "strengths", the probability that the first beats the
second depends only on their difference:

```
P( y_w preferred over y_l | x )  =  exp(r(x,y_w)) / ( exp(r(x,y_w)) + exp(r(x,y_l)) )

                                 =  sigmoid( r(x,y_w) - r(x,y_l) )
```

The second form follows from dividing numerator and denominator by `exp(r(x,y_w))`.

```
r(x,y_w) - r(x,y_l) =  0   ->  P = 0.50   coin flip, model sees them as equal
                    = +1   ->  P = 0.73
                    = +2   ->  P = 0.88
                    = +4   ->  P = 0.98   near-certain preference
```

**Consequence: rewards are only identified up to an additive constant.** Since only
differences matter, adding any constant `c` to every reward leaves all predicted
preferences unchanged. The reward model's absolute scale is arbitrary — `r = 5.0` means
nothing on its own, only `r(A) - r(B)` is meaningful. This is why reward
normalization (Section 5.7) is both permissible and necessary.

**The reward model's training loss** is the negative log-likelihood under this model:

```
Loss(r)  =  - E_{(x, y_w, y_l) ~ D} [ log sigmoid( r(x,y_w) - r(x,y_l) ) ]
```

Minimizing this pushes the score gap in the direction humans preferred. Note it needs
only *which* response was better, never a numeric quality score — which is the
lecture's point that comparing is easier than generating or absolute rating.

## 1.21 Standardization (whitening)

**Standardizing** (or whitening) a set of numbers means shifting and scaling them to
have mean 0 and standard deviation 1:

```
z_i  =  ( a_i - mean(a) )  /  ( std(a) + tiny )
```

The `tiny` (e.g. `1e-8`) prevents division by zero when all values are identical.

**Why PPO whitens advantages.** The advantage scale drifts over training as the reward
model's outputs and the value function's accuracy change. Since the advantage
multiplies the gradient, a drifting scale acts like a drifting learning rate. Whitening
per batch pins the effective step size, making a single learning rate work throughout
the run.

**The subtlety:** whitening divides by a *sample* standard deviation computed from the
same batch, which technically introduces bias and couples the samples in a batch. In
practice it is such a large stability win that essentially every implementation does
it. Another deliberate bias-for-variance trade.

## 1.22 Goodhart's law and overoptimization

**Goodhart's law:** when a measure becomes a target, it ceases to be a good measure.

This is the central statistical hazard of RLHF, and it explains the epoch counts.

The reward model `r` is a *learned approximation* of true human preference, fit to a
finite dataset (order 10,000 comparisons). It is accurate in the region where that
data lived — near the SFT model's output distribution — and unreliable elsewhere.

PPO then optimizes against `r`. As the policy moves, it leaves the region where `r`
was validated and enters territory where `r` is merely extrapolating. And PPO is an
*optimizer*: it will actively seek out the places where `r` is highest, which are
disproportionately the places where `r` is **wrong**.

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

This gap between proxy reward and true quality is called **reward
overoptimization**, and it is why:

```
1.  the objective carries a KL penalty at all
2.  runs use very few epochs (often a single pass over the prompts)
3.  practitioners stop on a KL budget rather than a fixed step count
4.  the reward model itself is trained for only ONE epoch (it overfits beyond that)
```

The KL penalty is best understood as a **trust region on the proxy**: stay close
enough to the reference that the reward model's estimates remain meaningful.

---

# Part II — Reinforcement Learning Formulation

## 2.1 The MDP

Reinforcement learning is formalized as a **Markov Decision Process (MDP)**, defined
by five components:

```
S           set of states
A           set of actions
P(s'|s,a)   transition dynamics: where you land after taking action a in state s
R(s,a)      reward function
gamma       discount factor
```

An **agent** observes a state, takes an action according to its **policy**, receives a
reward, and lands in a new state. Repeat. The goal is to choose a policy maximizing
cumulative reward.

The "Markov" property means the state contains everything relevant: the future depends
only on the current state, not the path taken to reach it.

## 2.2 Mapping an LLM onto the MDP

This is the lecture's RL-formulation slide, made precise:

```
RL concept        LLM realization
--------------    ---------------------------------------------------
agent             the LLM
policy            pi_theta, the model's next-token distribution
state s_t         the full context so far: (x, y_1, ..., y_{t-1})
action a_t        the next token y_t
action space      the entire vocabulary (~128,000 discrete actions)
transition        DETERMINISTIC: append the token to the context.
                  s_{t+1} = s_t + [y_t].  No randomness whatsoever.
reward            the reward model's score, at the END of the response
episode           one full response, from first token to EOS
terminal state    EOS emitted, or max length reached
```

**Several features make this a very unusual MDP, and they explain PPO's shape here:**

**1. The transition function is deterministic and trivial.** In robotics, `P(s'|s,a)`
is complex and stochastic. Here, taking action `y_t` in state `s_t` puts you in
`s_t + [y_t]` with probability 1. All the stochasticity in the system comes from the
*policy's own sampling*, not from the environment. The "Environment" box in the
lecture's diagram is essentially a string concatenation.

**2. The action space is enormous.** 128,000 discrete actions per step, versus a
handful in most classic RL benchmarks.

**3. The reward is extremely sparse and delayed.** You emit 400 tokens and receive
exactly one scalar at the very end. Every intermediate action gets no direct feedback.
This is the hardest part of the setup, and all of Section 2.5–2.7 exists to address it.

**4. Episodes are short and always terminate.** A few hundred to a few thousand steps,
guaranteed to end.

**5. The state is the entire history.** So the Markov property holds trivially — the
context *is* the history.

## 2.3 Trajectories and returns

A **trajectory** is one complete episode:

```
tau  =  ( s_1, a_1, R_1, s_2, a_2, R_2, ..., s_T, a_T, R_T )
```

For an LLM, one trajectory = one prompt with one sampled response.

The **return** from position `t` is the total future reward from that point on:

```
G_t  =  R_t + R_{t+1} + R_{t+2} + ... + R_T
```

With discounting (next section):

```
G_t  =  R_t + gamma*R_{t+1} + gamma^2*R_{t+2} + ...
     =  sum_{k=0..T-t}  gamma^k * R_{t+k}
```

The objective is to maximize the expected return, `E[G_1]`.

## 2.4 Discounting

The **discount factor** `gamma` in `[0,1]` down-weights future rewards:

```
gamma = 0      completely myopic: only the immediate reward matters
gamma = 0.99   standard in classic RL: rewards ~100 steps out still count
gamma = 1.0    no discounting: all future rewards weighted equally
```

Discounting exists in classic RL for two reasons: mathematical convergence over
infinite horizons, and modeling genuine preference for sooner rewards.

**In RLHF, `gamma = 1.0` is standard.** This surprises people coming from classic RL,
but the reasoning is sound:

```
1.  Episodes are finite and short, so there is no divergence to prevent.
2.  There is no reason to prefer a good token "sooner". A response is judged
    as a whole; token 300 being good is worth exactly as much as token 3
    being good.
3.  With one terminal reward, gamma < 1 would systematically discount the
    reward for early tokens, biasing credit assignment toward the end of
    the response for no principled reason.
```

So in RLHF you will typically see `gamma = 1`, and the discounting machinery, while
present in the equations, is inert.

## 2.5 Value, Q, and advantage

Three related functions. Getting these straight is essential.

**The state-value function** `V(s)` — "how good is this position?"

```
V^pi(s)  =  E_{pi} [ G_t | s_t = s ]
```

The expected total future reward from state `s`, if you continue following policy
`pi`. In LLM terms: given the context so far, how well is this response expected to
score once finished?

**The action-value function** `Q(s,a)` — "how good is this position if I take this
specific action?"

```
Q^pi(s,a)  =  E_{pi} [ G_t | s_t = s, a_t = a ]
```

**The advantage function** — "was that action better or worse than average?"

```
A^pi(s,a)  =  Q^pi(s,a)  -  V^pi(s)
```

This is the single most important quantity in PPO. It is the lecture's
`Advantage ~ Reward - Baseline`, with `V` as the baseline.

**Reading the sign is everything:**

```
A > 0    this action did BETTER than the policy's average from this state
         -> increase its probability

A = 0    this action was exactly average
         -> no change

A < 0    this action did WORSE than average
         -> decrease its probability
```

**Why the advantage rather than the raw return.** Suppose every response to a prompt
scores +9. Using raw returns, you would push up on all of them equally and learn
nothing about which was better. Subtracting `V` removes the shared component and leaves
only the *relative* signal. This is Section 1.18's baseline argument, in RL language.

**About the value model in RLHF specifically.** As the lecture notes, it is:

```
- token-level:      it predicts a value at EVERY position, not just at the end
- policy-dependent: it answers "what reward if I FOLLOW THE POLICY from here"
- trained jointly:  updated alongside the policy, since the policy keeps changing
- label = reward:   its regression target is the actual observed return
```

The "policy-dependent" point deserves emphasis: `V` is not a fixed property of the
text. It is a prediction about what *this current policy* would do next. So as the
policy improves, `V`'s targets shift — the value model is chasing a moving target,
which is a major source of PPO's instability.

Architecturally it is usually the SFT model with the language-modeling head replaced
by a scalar head, producing one number per token position.

## 2.6 TD error and bootstrapping

The **temporal-difference (TD) error** compares a one-step-lookahead estimate against
the current value prediction:

```
delta_t  =  R_t  +  gamma * V(s_{t+1})  -  V(s_t)
            \____________________/         \_____/
              a better estimate of         the current
              the value of s_t             estimate
```

Interpretation: it is the **surprise**. `R_t + gamma*V(s_{t+1})` uses one step of real
observed reward plus an estimate of the rest; `V(s_t)` is the pure estimate made
before seeing that reward. The difference measures how much better or worse things
turned out than expected.

```
delta_t > 0    pleasant surprise: better than the value model predicted
delta_t < 0    unpleasant surprise: worse than predicted
delta_t = 0    exactly as predicted
```

**Bootstrapping** means using your own estimate `V(s_{t+1})` as part of the target for
`V(s_t)`. It is what makes TD methods sample-efficient — you do not have to wait for
the episode to finish to get a learning signal. The cost is bias: if `V` is wrong, that
error propagates into the targets.

**The two extremes of estimating the advantage:**

```
1-step TD:        A_t ~= delta_t
                  LOW variance (one reward term), HIGH bias (leans on V heavily)

Monte Carlo:      A_t ~= G_t - V(s_t)
                  HIGH variance (full random return), LOW bias (uses real rewards)
```

GAE interpolates between them.

## 2.7 Generalized Advantage Estimation (GAE)

GAE (Schulman et al., 2015 — the lecture's suggested reading) forms an
exponentially-weighted average of all the `k`-step advantage estimators:

```
A_t^GAE  =  sum_{l=0..T-t}  (gamma * lambda)^l  *  delta_{t+l}
```

Written out:

```
A_t = delta_t
    + (gamma*lambda)   * delta_{t+1}
    + (gamma*lambda)^2 * delta_{t+2}
    + (gamma*lambda)^3 * delta_{t+3}
    + ...
```

**`lambda` is the bias-variance dial:**

```
lambda = 0     A_t = delta_t
               pure 1-step TD. Lowest variance, highest bias.

lambda = 1     A_t = sum_l gamma^l * delta_{t+l}  =  G_t - V(s_t)
               pure Monte Carlo. Highest variance, no bias from V's errors.

lambda = 0.95  the standard choice. Mostly Monte Carlo, mildly smoothed.
```

**The efficient implementation** computes this with a single backward pass over the
sequence, using the recursion `A_t = delta_t + gamma*lambda*A_{t+1}`:

```
A_next = 0
for t = T down to 1:
    if t == T:
        V_next = 0                      # nothing after the terminal token
    else:
        V_next = V[t+1]
    delta  = R[t] + gamma * V_next - V[t]
    A[t]   = delta + gamma * lambda * A_next
    A_next = A[t]
```

This is `O(T)` — one reverse scan, no nested loops. Note the boundary condition: after
the terminal token there is no future, so `V_next = 0`.

**The regression targets for the value model** come out of the same computation:

```
returns[t]  =  A[t]  +  V[t]
```

This identity follows directly from `A = G - V`. The value model is then trained to
regress toward `returns[t]`. This is the lecture's "label = reward".

## 2.8 On-policy vs off-policy

```
ON-POLICY    the data used for the update was generated by the CURRENT policy
OFF-POLICY   the data came from some other policy (an old version, a human,
             another model)
```

**PPO is on-policy** (approximately). The objective is an expectation over
`y ~ pi_theta(.|x)` — the policy being optimized. This has hard consequences:

```
1.  You must GENERATE fresh data every iteration. You cannot reuse a fixed dataset.
2.  Generation dominates the compute cost, typically well over half the wall clock.
3.  Data is discarded after a few gradient steps. It is not "sample efficient"
    in the supervised-learning sense.
4.  You need the reward model available online, because the responses being
    scored did not exist until a moment ago and have no precomputed labels.
```

**Why "approximately".** Strictly on-policy would mean one gradient step per batch of
samples. PPO takes several (`ppo_epochs`), so after the first step the data is
slightly off-policy. The importance ratio corrects for this, and clipping bounds how
far the correction is trusted. PPO is best described as **"near-on-policy with an
importance correction."**

**Contrast with DPO**, which is fully off-policy: `y_w` and `y_l` come from a fixed
preference dataset, nothing is generated during training, and the whole thing reduces
to a supervised loss. That is precisely why DPO needs no reward model and no value
model — and also why it cannot discover behaviors absent from its dataset.

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

```
stage          data                          objective            scale
-----------    --------------------------    -----------------    ------------
Pretraining    raw text                      next-token MLE       trillions of tokens
SFT            (prompt, ideal response)      next-token MLE       O(10k - 1M) examples
Reward model   (prompt, better, worse)       Bradley-Terry MLE    O(10k) comparisons
PPO            prompts only                  expected reward      O(100k) episodes
```

Note the progression in what the data contains. Pretraining data has no notion of a
task. SFT data has a task and one correct answer. Preference data has a task and a
*relative judgment*. Only PPO's data has no answers at all — just prompts, with the
model generating its own candidates.

## 3.2 Why preferences instead of more SFT

The lecture's motivation is that an SFT model may still misbehave, and SFT alone gives
you no way to inject **negative** signal. The reasons preference data helps:

**1. Comparing is easier than generating.** Asking a human to write the ideal response
to a hard prompt is slow, expensive, and requires expertise. Asking which of two
responses is better is fast and needs less skill. So you get far more data per dollar,
on harder prompts.

**2. SFT can only say "do this," never "not that."** Cross-entropy loss raises the
probability of the target text. There is no mechanism to lower the probability of a
specific bad response. Preference tuning has both directions, which is the lecture's
"need to inject negative signals."

**3. SFT is sensitive to distribution.** Training on text the model finds unlikely can
degrade it in unexpected ways. Preference methods operate on the model's own
distribution — in PPO's case, literally on its own samples.

**4. Absolute ratings are unreliable.** Humans are inconsistent when asked to score
quality from 1–10 (my 7 is your 5, and both drift over a session). Pairwise judgments
are far more stable, and Bradley-Terry converts them into a consistent scalar scale.

**One caveat the lecture raises:** a misbehaving model is also a signal to go check
your SFT data quality. Preference tuning is not a repair for a bad SFT stage.

## 3.3 Preference data collection

**Three labeling formats:**

```
POINTWISE    each (prompt, response) gets an absolute score
             obs1: 0.4   obs2: 0.9   obs3: 0.1   obs4: 0.2

PAIRWISE     comparisons between two responses
             obs1 < obs2,  obs1 > obs3,  obs1 > obs4,  obs2 > obs3

LISTWISE     a full ranking of several responses
             obs2 (1st), obs1 (2nd), obs4 (3rd), obs3 (4th)
```

Pairwise is the standard, because it is the easiest to label reliably and it maps
directly onto Bradley-Terry.

**The recipe for pairwise data:**

```
STEP 1 — generate a pair of responses for the SAME prompt
  - prompts from production logs or a reference distribution
  - responses from the SFT model with sampling (different seeds/temperature),
    from synthetic generation, or from rewrites of existing responses

STEP 2 — label which is better
  - human raters (this is the "HF" in RLHF)
  - proxies: LLM-as-a-judge, or metrics like BLEU / ROUGE where applicable
  - the scale can be binary (better/worse) or nuanced (much better,
    slightly better, tie, ...)
```

**Details that matter in practice:**

Both responses must answer the *same* prompt — the Bradley-Terry model compares
strengths conditional on `x`. Generating them by sampling the same model twice at
temperature is the cheapest source of genuinely comparable pairs, and it is another
place where stochastic sampling (Part I) is load-bearing.

Ties are awkward: plain Bradley-Terry has no tie outcome, so implementations either
discard ties or extend the model.

Human agreement rates on these comparisons are typically well short of perfect,
which places a ceiling on how good the reward model can be. The reward model cannot be
more accurate than the consistency of its labels.

## 3.4 Stage 1: reward modeling

**Goal.** Learn a function that scores responses the way humans would.

```
input:   (prompt x, response y)
output:  a single scalar r(x,y)
```

**Architecture.** A pretrained LLM with the language-modeling head replaced by a
**classification/regression head** producing one number. For decoder-only models the
score is typically read off the final token's hidden state; for encoder-only models
(BERT and similar) it comes from the `[CLS]` projection, as the lecture notes.

Initializing from a strong pretrained model matters — the reward model needs to
*understand* the text before it can judge it.

**The loss** (derived in Section 1.20):

```
Loss(r)  =  - E_{(x, y_w, y_l) ~ D} [ log sigmoid( r(x,y_w) - r(x,y_l) ) ]
```

**Reading the loss:**

```
r(y_w) - r(y_l) = +4   ->  sigmoid = 0.982  ->  loss = 0.018   already correct
r(y_w) - r(y_l) =  0   ->  sigmoid = 0.500  ->  loss = 0.693   no opinion
r(y_w) - r(y_l) = -4   ->  sigmoid = 0.018  ->  loss = 4.02    confidently wrong
```

Gradient descent widens the gap in the direction humans chose. Note that the loss
never references an absolute target score — only the difference is supervised, which
is exactly the identifiability property from Section 1.20.

**Implementation note.** Both responses in a pair are usually put in the same forward
batch so the shared prompt encoding is computed once, and the difference is taken
inside the loss.

**Data scale.** Order 10,000 comparisons is typical, per the lecture.

**Trained for ONE epoch.** The reward model overfits quickly beyond a single pass.
This is worth remembering: even the supervised stage of RLHF is single-pass.

**Evaluation.** Benchmarks like RewardBench (Lambert et al., 2024) measure how often a
reward model ranks a held-out pair correctly.

**The fundamental limitation.** The reward model is accurate near the distribution it
was trained on, and unreliable outside it. It is a *proxy*, and PPO will exploit its
flaws (Section 1.22). Everything about the KL penalty and short training exists
because of this.

## 3.5 Stage 2: the RL objective

The full objective from Ouyang et al. (2022), which the lecture presents:

```
maximize over theta:

  E_{x ~ D, y ~ pi_theta(.|x)}  [  r(x,y)  -  beta * log( pi_theta(y|x) / pi_ref(y|x) )  ]
                                   \______/     \_________________________________________/
                                  maximize            don't deviate too much
                                  rewards             from the base model
```

**Term by term:**

```
E_{x ~ D}                prompts drawn from a fixed prompt dataset
E_{y ~ pi_theta(.|x)}    responses SAMPLED FROM THE POLICY BEING TRAINED.
                         This is what makes the method on-policy, and it is
                         why generation is part of the training loop.
r(x,y)                   the frozen reward model's score
beta                     the KL coefficient: how strongly to anchor to the reference
log(pi_theta/pi_ref)     the per-sample KL estimate against the frozen SFT model
```

**On `y ~ pi_theta(y|x)` specifically**, since it is the crux: `y` is a response
*generated by the current model*, not a label from a dataset. There is no ground truth
`y` anywhere in this stage. The model proposes; the reward model judges. Concretely,
`pi_theta(.|x)` is the distribution over complete responses induced by autoregressive
sampling (Section 1.9), and drawing from it means running the generation loop of
Section 4.3.

**What the two terms trade off.** Maximizing `r` alone would let the policy run off to
whatever text maximizes a flawed proxy. The KL term prices the distance travelled. The
result is a **trust region**: find the highest-reward text that is still recognizably
close to the SFT model. The lecture's note that this "avoids reward hacking and
training instability" is exactly this.

**Choosing `beta`:**

```
beta too small   the policy drifts far, reward climbs, real quality collapses
                 (reward hacking; classic symptoms are repetition, degenerate
                 formatting, sycophancy)
beta too large   the policy barely moves from SFT; you spent a lot of compute
                 to change nothing
```

**Data scale.** Order 100,000 episodes, per the lecture, with the "label" being the
reward model's score rather than any human annotation. Human effort was spent once, in
stage 1.

**Initialization.** The policy starts at the SFT model. So does the value model
(with a new head), and `pi_ref` is a frozen copy of it.

Note that this objective says nothing about *how* to optimize it. PPO is one choice of
optimizer for it; REINFORCE, RLOO, and GRPO are others.

---

# Part IV — PPO, Step by Step

## 4.1 The four models

PPO for LLMs requires four models in memory. This is the lecture's main stated
limitation.

```
name          symbol         role                              trained?
-----------   ------------   -------------------------------   ---------
POLICY        pi_theta       the LLM being aligned             YES
VALUE         V_phi          predicts expected return          YES
REWARD        r              scores complete responses         NO (frozen)
REFERENCE     pi_ref         anchor for the KL penalty         NO (frozen)
```

**Initialization:**

```
pi_theta   := copy of SFT model
pi_ref     := copy of SFT model, frozen forever
V_phi      := SFT model (or reward model) body + a fresh scalar head
r          := separately trained in stage 1, frozen
```

**Memory cost.** The two trained models need parameters, gradients, and optimizer
state (Adam keeps two moments, so roughly 2 extra copies each). The two frozen models
need parameters only, no gradients, no optimizer state. A rough accounting for a model
with `P` parameters in mixed precision:

```
pi_theta:   weights + grads + Adam m,v + fp32 master copy   ~ 16 bytes/param
V_phi:      same                                            ~ 16 bytes/param
pi_ref:     weights only                                    ~  2 bytes/param
r:          weights only                                    ~  2 bytes/param
```

So the trained models dominate. The frozen ones are comparatively cheap, and both can
be sharded, offloaded, or served remotely.

**Which are the same architecture?** All four are usually the same base architecture
and tokenizer. `pi_theta`, `pi_ref` are literally identical models at different points
in time. `V_phi` and `r` share the body but have scalar heads instead of LM heads. The
reward model is the only one that is not a copy of this lineage — it is the sole
carrier of external human preference information in the loop.

## 4.2 The three policies

Distinct from the four models: within the objective there are **three policies**, two
of which are snapshots of the same lineage.

```
pi_theta       CURRENT weights, live, differentiable, changes every step
pi_theta_old   SNAPSHOT taken at generation time, refreshed each iteration
pi_ref         SNAPSHOT taken at step 0, never refreshed
```

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

```
ratio_t  =  pi_theta(y_t|...)  /  pi_theta_old(y_t|...)        <- clipping term
kl_t     =  log pi_theta(y_t|...)  -  log pi_ref(y_t|...)      <- penalty term
```

`pi_theta` is in the numerator of both, and it is the **only one carrying gradients**.
The other two are stored constants at update time.

**The critical distinction — time horizon:**

```
pi_theta_old   a MOVING reference, always ~1 iteration behind.
               Answers: "am I taking too big a step RIGHT NOW?"
               Purpose: OPTIMIZATION STABILITY.

pi_ref         a FIXED reference, thousands of steps behind and never moving.
               Answers: "how far have I wandered in TOTAL?"
               Purpose: ALIGNMENT / anti-drift.
```

**Why the fixed one is indispensable.** With only the ratio, every individual step
looks fine while the policy slowly walks somewhere terrible:

```
step    drift from SFT       ratio vs pi_theta_old
----    ------------------   ---------------------
1       negligible           ~1.0    looks fine
100     noticeable           ~1.0    looks fine
1000    unrecognizable,      ~1.0    STILL looks fine
        reward-hacked
```

The ratio has no memory beyond one iteration, so it cannot detect this. `pi_ref` can:
as drift accumulates, `log pi_theta - log pi_ref` grows and the penalty grows with it.
The lecture's remark that "nowadays, KL divergence is with respect to ref (base model)"
is precisely this point — small steps alone do not prevent a long slow walk to a bad
place.

**A useful sanity check.** If you set `ppo_epochs = 1`, then `pi_theta = pi_theta_old`
exactly at gradient time, so `ratio = 1.0` everywhere and clipping is completely inert.
The `pi_ref` penalty still matters enormously. Any behavior you see change under that
setting was attributable to clipping; anything unchanged was attributable to the KL
anchor.

**Worked numbers at one token position** (the model choosing `" not"`):

```
                  p(" not")     log p
pi_ref              0.05        -3.00     SFT thought this unlikely
pi_theta_old        0.30        -1.20     policy at generation time
pi_theta            0.36        -1.02     policy now, mid-update

ratio = 0.36/0.30 = 1.20     -> exactly at the eps=0.2 clip boundary: stop pushing
kl    = -1.02 - (-3.00) = 1.98  -> far above SFT here: penalize
```

Two independent readings from one token, on two different timescales.

---

## 4.3 Step 1: rollout (generation)

**Input:** a batch of prompts from `D`.
**Output:** sampled responses, plus the log-probs recorded during generation.

### The generation loop in detail

```
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
        logits = logits / T                    # temperature; T=1.0 for PPO
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
`log pi_theta_old`, the denominator of the ratio. If you recomputed them later, after
the weights had moved, the ratio would be 1.0 by construction and clipping would be
meaningless. Note you record the log-prob of the token **actually sampled**, not the
max — one number per position, not a full distribution.

**The KV cache.** Without it, generating token `t` would re-process the whole context,
making generation `O(T^2)` in forward passes. The cache stores the attention keys and
values for previous positions so each new token costs one incremental pass. This is
pure inference optimization and does not affect the math.

**Sampling must be stochastic.** Covered in Section 1.12: greedy decoding destroys
exploration and breaks the Monte Carlo estimator.

**Temperature is part of the objective's definition.** Whatever `T` you generate at
defines the distribution `pi_theta` that the rest of the math refers to. See Section
5.6.

**Multiple responses per prompt.** How many depends on the algorithm:

```
PPO   typically 1 response per prompt, with a large batch of DIFFERENT prompts
      (e.g. 512-1024 prompts). Variance reduction comes from the value model.

GRPO  MUST sample a group, typically 8-64 per prompt, because the baseline
      is the within-group mean reward.
```

**This step dominates cost.** Generation is sequential and memory-bandwidth bound,
usually more than half of wall-clock time. Hence the common architecture of handing
rollouts to a dedicated inference engine (vLLM, SGLang) and syncing weights back —
which is also the origin of the bug in Section 5.6.

**Left-padding for batched generation.** When batching prompts of different lengths,
pad on the **left** so that all sequences' "next token" positions align at the right
edge. Right-padding would put pad tokens between the prompt and the generation.

---

## 4.4 Step 2: scoring

**Input:** the `(x, y)` pairs from step 1.
**Output:** one scalar per response, plus reference log-probs and value predictions.

### 2a. Reward model

```
score = r(x, y)          ONE scalar for the ENTIRE response
```

Details:

- The reward model sees the full concatenated prompt and response, formatted with the
  **same chat template** used in training. A template mismatch here silently corrupts
  the scores — a common and hard-to-find bug.
- The score is read from the final token's hidden state (for decoder-only reward
  models). Which "final token" matters: it should be the last real token, not a pad.
- This is the **central awkwardness of RLHF**: the reward is *sequence-level*, but the
  policy makes *token-level* decisions. Steps 3 and 4 exist entirely to bridge that gap.

### 2b. Reference log-probs

```
for each position t:   log pi_ref(y_t | x, y_<t)
```

This is a **single forward pass**, not generation — you already know all the tokens, so
you can process them in parallel and read off the log-prob of each actual token. Cheap
relative to step 1.

### 2c. Value predictions

```
for each position t:   V_phi(s_t)
```

Also one forward pass, producing a scalar per position.

**Everything in step 2 is inference only.** No gradients are needed yet. All three
sub-steps can run in `no_grad` mode, and 2b and 2c can be batched together with the
policy's own forward pass if the models are colocated.

---

## 4.5 Step 3: per-token reward construction

**Input:** the sequence-level score, the policy log-probs, the reference log-probs.
**Output:** a per-token reward array `R_t`.

This is where the sequence-level reward is turned into something an RL algorithm can
use, and where the KL penalty is physically inserted.

```
for t = 1 .. T:
    kl_t = log pi_theta_old(y_t|...) - log pi_ref(y_t|...)
    R_t  = - beta * kl_t

# the reward model's score lands on the FINAL token only
R_T = R_T + r(x, y)
```

Concretely, for a 5-token response:

```
position:      1        2        3        4        5 (last)
kl_t:         0.10     0.05     0.80     0.02     0.03
-beta*kl_t:  -0.010   -0.005   -0.080   -0.002   -0.003     (beta = 0.1)
r(x,y):         -        -        -        -      +2.500
             ------   ------   ------   ------   -------
R_t:         -0.010   -0.005   -0.080   -0.002   +2.497
```

### Details worth understanding

**Why the KL is per-token but the reward is terminal.** The KL is a per-token quantity
by construction — it is defined on each next-token distribution, so it can be assessed
locally at every position. The reward model, by contrast, only knows how to judge a
complete response. There is nothing to attribute to token 3 in isolation.

**Notice position 3 above.** It has a large KL (0.80), meaning the policy has drifted
substantially from the reference at that specific position. It receives a
correspondingly larger penalty. The KL penalty is thus *targeted*: it pushes back
exactly where the drift is, token by token.

**This is the objective, rearranged.** The Ouyang objective is
`r(x,y) - beta*KL(sequence)`. Since the sequence KL is the sum of per-token KLs,
distributing the penalty across tokens and putting `r` at the end gives a per-token
reward whose *total* equals the original objective. Nothing has been changed
mathematically; it has been reshaped into a form GAE can consume.

**Which log-probs to use for the KL.** Implementations differ subtly on whether to use
`pi_theta_old` (fixed during the inner epochs) or the live `pi_theta`. Using
`pi_theta_old` keeps `R_t` constant across the inner epochs, which is simpler and
standard. An alternative treats the KL as a differentiable term added directly to the
loss rather than baked into the reward; both appear in practice.

**Sign conventions.** `R_t` is a reward to be *maximized*, so the KL penalty enters
with a minus sign. Getting this sign backwards produces a model that actively runs
away from the reference, which is a spectacular and instructive failure.

---

## 4.6 Step 4: advantage estimation

**Input:** `R_t` from step 3, `V_phi(s_t)` from step 2c.
**Output:** advantages `A_t` and value targets `returns_t`.

Apply GAE (Section 2.7) with a single reverse scan:

```
A_next = 0
for t = T down to 1:
    V_next  = 0 if t == T else V[t+1]
    delta   = R[t] + gamma * V_next - V[t]
    A[t]    = delta + gamma * lambda * A_next
    A_next  = A[t]

returns = A + V                  # regression targets for the value model
```

Then whiten the advantages across the batch (Section 5.2):

```
A = (A - mean(A)) / (std(A) + 1e-8)
```

### Full numerical example

Take the 5-token response above, with `gamma = 1.0`, `lambda = 0.95`, and value
predictions `V = [1.8, 1.9, 2.0, 2.3, 2.4]`:

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

All advantages are positive here, meaning this response did better than the value
model expected, so every token gets pushed up — more strongly at the start, where the
accumulated future advantage is largest.

Note how the reverse scan propagates the terminal reward backwards. The good final
score raises the advantage of *every* preceding token, which is how a
sequence-level reward reaches token 1. That is the credit assignment mechanism.

### The sign is the learning signal

```
A_t > 0   this token was better than expected   ->  make it MORE likely
A_t < 0   this token was worse than expected    ->  make it LESS likely
A_t = 0   exactly as expected                   ->  no change
```

Everything downstream just implements "move probability in the direction of the
advantage, but not too fast."

---

## 4.7 Step 5: the probability ratio

**Input:** the stored tokens, the stored `log pi_theta_old`.
**Output:** `ratio_t` for each position.

Now gradients begin. Run the **current** policy over the stored `(x, y)` tokens — one
forward pass, **no sampling**, because the tokens are already fixed:

```
log pi_theta(y_t | x, y_<t)        for all t, differentiable

log_ratio_t = log pi_theta(y_t|...) - log pi_theta_old(y_t|...)
ratio_t     = exp( log_ratio_t )
```

### Details

**Computed as a difference of logs, then exponentiated.** Never as a quotient of
probabilities — that would risk underflow and lose precision (Section 1.11).

**It starts at exactly 1.0.** On the first gradient step of the first inner epoch,
`pi_theta == pi_theta_old`, so `log_ratio = 0` and `ratio = 1`. It drifts away as the
inner epochs proceed. A useful debugging check: if `ratio != 1.0` on the very first
inner step, something is inconsistent between your generation and training paths
(Section 5.6).

**Only `pi_theta` carries gradients.** `log pi_theta_old` is a stored constant. So

```
d(ratio_t)/d(theta)  =  ratio_t * d(log pi_theta(y_t|...))/d(theta)
```

and the backward pass reduces to the familiar score function of Section 1.17.

**No generation in this step.** This is worth emphasizing because it is a common
misconception. Sampling happened once, in step 1. From here on, the tokens are data.
Every subsequent forward pass is a parallel teacher-forced pass over known tokens,
which is fast.

**Interpretation.** `ratio_t` answers: *how much more (or less) likely is this exact
token now, compared to when I generated it?*

```
ratio = 1.0    unchanged
ratio = 1.3    the policy now finds this token 30% more likely
ratio = 0.7    30% less likely
ratio = 50     something has gone badly wrong
```

---

## 4.8 Step 6: clipping (the heart of PPO)

**The clipped surrogate objective:**

```
L_clip  =  mean over t of  min(  ratio_t * A_t ,
                                 clip(ratio_t, 1-eps, 1+eps) * A_t  )
```

where

```
clip(z, lo, hi) = lo   if z < lo
                  hi   if z > hi
                  z    otherwise
```

and `eps` is typically 0.2, giving the band `[0.8, 1.2]`.

### The full case analysis

This deserves careful treatment because the `min` behaves asymmetrically depending on
the sign of `A_t`. Remember we are **maximizing** `L_clip`.

**Case A: `A_t > 0`** (good token — we want to increase its probability)

```
ratio     unclipped      clipped        min(...)        gradient?
-------   ------------   ------------   -------------   ------------------
0.5       0.5*A          0.8*A          0.5*A          YES (unclipped term)
1.0       1.0*A          1.0*A          1.0*A          YES
1.1       1.1*A          1.1*A          1.1*A          YES
1.2       1.2*A          1.2*A          1.2*A          boundary
1.5       1.5*A          1.2*A          1.2*A          NO  (clipped, constant)
3.0       3.0*A          1.2*A          1.2*A          NO
```

Once `ratio > 1+eps`, the objective is stuck at `1.2*A`. Increasing the probability
further yields no gain, so the gradient through this token is **zero**. PPO says: *you
have boosted this token enough for now; stop.*

But note the asymmetry at low ratios: at `ratio = 0.5`, the `min` picks the
**unclipped** `0.5*A`, which still has gradient. So if the policy has moved a good
token's probability *down* too far, PPO will happily push it back up. The clip does not
block corrective moves.

**Case B: `A_t < 0`** (bad token — we want to decrease its probability)

Careful: `A_t` is negative, so multiplying flips comparisons.

```
Let A = -1 for concreteness.

ratio     unclipped      clipped        min(...)        gradient?
-------   ------------   ------------   -------------   ------------------
0.3       -0.3           -0.8           -0.8           NO  (clipped)
0.5       -0.5           -0.8           -0.8           NO
0.8       -0.8           -0.8           -0.8           boundary
0.9       -0.9           -0.9           -0.9           YES
1.0       -1.0           -1.0           -1.0           YES
2.0       -2.0           -1.2           -2.0           YES (unclipped is smaller!)
```

Once `ratio < 1-eps`, the objective is pinned at `-0.8` and the gradient vanishes:
*you have suppressed this token enough; stop.*

And again the asymmetry works in the corrective direction: at `ratio = 2.0`, the `min`
selects the unclipped `-2.0`, which retains gradient, so the policy is pushed to bring
that bad token's probability back down.

### The summary that captures it

```
A > 0:   gradient is KILLED when ratio > 1+eps      (stop boosting)
A < 0:   gradient is KILLED when ratio < 1-eps      (stop suppressing)

In BOTH cases the gradient SURVIVES in the direction that CORRECTS
an overshoot. The min() makes the objective pessimistic:
it always takes the LESS optimistic of the two estimates.
```

That pessimism is the design. PPO never lets an optimistic importance-weighted
estimate justify a large step, but it always permits a step that undoes one.

### Why this works — three framings

**As variance control (Section 1.16).** The ratio is an importance weight, and
importance weights have unbounded variance. Clipping bounds them, trading bias for a
finite-variance estimator.

**As an implicit trust region.** The original TRPO enforced a hard KL constraint via a
constrained optimization with second-order machinery. PPO achieves a similar effect
with a first-order clip that any autodiff framework handles. This is the entire
selling point of the paper: TRPO-like reliability, SGD-like simplicity.

**As "Proximal".** The name says it. Keep the new policy *proximal* (near) to the old
one.

### Two terminology warnings from the lecture

```
1.  L_clip is an OBJECTIVE to MAXIMIZE, not a loss to minimize.
    Implementations negate it before calling backward().

2.  The `r` in `ratio` is NOT the reward. The literature overloads `r`
    for both the reward and the ratio. Here `ratio_t` is used to avoid it.
```

---

## 4.9 Step 7: the value loss

The value model is trained by regression onto the returns computed in step 4:

```
L_value  =  mean over t of  ( V_phi(s_t) - returns_t )^2
```

This is the lecture's "trained jointly with policy" and "label = reward".

**The clipped variant**, used by most implementations for the same
stability reason as the policy clip:

```
V_clipped   =  V_old + clip( V_phi - V_old, -eps_v, +eps_v )

L_value     =  0.5 * mean( max( (V_phi     - returns)^2 ,
                                (V_clipped - returns)^2 ) )
```

Note this uses `max`, not `min`, because the value term is a **loss being minimized**
whereas `L_clip` is an objective being maximized. Both are being pessimistic; the
direction of pessimism just flips with the sign convention.

**Why the value model is a source of trouble.** Its target is `returns`, which depends
on the current policy's behavior. As the policy changes, the targets move. The value
model is therefore permanently chasing a non-stationary objective — it is never fully
converged, its predictions are biased, and that bias flows straight into the
advantages via `delta_t`. This is one of the strongest arguments for GRPO, which
deletes the value model and uses an empirical group mean instead.

**Whether to share parameters.** Two designs exist:

```
SEPARATE   two full models. More memory, no interference. Standard for LLM RLHF.
SHARED     one body with two heads (LM + value). Less memory, but the two
           objectives can fight over the shared representation.
```

For LLMs, separate is the norm, because the value head's gradients can otherwise
damage the language modeling representation.

---

## 4.10 Step 8: entropy bonus and total loss

Assemble the final scalar to minimize:

```
L_total  =  - L_clip  +  c1 * L_value  -  c2 * H(pi_theta)
            \_______/    \___________/    \______________/
            policy       value            entropy bonus
            (negated     regression       (negated because
             to become                     more entropy is
             a loss)                       DESIRABLE)
```

Typical weights: `c1` around 0.5–1.0, `c2` around 0.0–0.01 (often exactly 0 for LLM
RLHF, since the KL penalty already resists collapse).

**The entropy term** (Section 1.14) is computed over the full next-token distribution
at each position:

```
H_t  =  - sum_{i=1..V}  p_i * log p_i
H    =  mean over t of H_t
```

Its job is to resist **mode collapse**. Without pressure toward uncertainty, a policy
that finds one high-reward response can concentrate all probability on it, at which
point sampling returns identical text, exploration dies, and learning stops.

**Signs are the most common bug here.** Track them carefully:

```
L_clip     we want it LARGE  ->  enters L_total with a MINUS
L_value    we want it SMALL  ->  enters L_total with a PLUS
H          we want it LARGE  ->  enters L_total with a MINUS
```

---

## 4.11 Step 9: the optimizer step

```
L_total.backward()
clip_grad_norm_(parameters, max_norm=1.0)
optimizer.step()
optimizer.zero_grad()
```

**Details that matter:**

**Gradient norm clipping** (distinct from PPO's ratio clipping — same word, unrelated
mechanism) rescales the whole gradient vector if its norm exceeds a threshold:

```
if ||g|| > max_norm:
    g <- g * max_norm / ||g||
```

This is generic deep learning hygiene against occasional huge gradients, and it is
essentially mandatory here.

**Optimizer.** Adam or AdamW, with a much smaller learning rate than SFT — typically
around `1e-6` to `1e-5` for the policy, versus `1e-5` to `1e-4` for SFT. The policy is
already good; PPO is making small corrections against a noisy signal, and a large
learning rate destroys it quickly.

**Separate optimizers.** The policy and value model usually get their own optimizers,
often with different learning rates (the value model can tolerate a larger one).

**Gradient accumulation.** PPO batches are large, so a batch is typically split into
minibatches with gradients accumulated before stepping.

**Early stopping on KL.** Many implementations check the KL between `pi_theta` and
`pi_theta_old` after each inner epoch and **break out of the inner loop** if it exceeds
a threshold. This is a safety valve for when clipping alone is not holding the update
in check.

---

## 4.12 The complete loop in pseudocode

```
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
        scores      = r(prompts, responses)          # one scalar per response
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

Three nested levels of repetition, and it is worth being explicit about how many times
each runs, because the answer is "few" at every level:

```
LEVEL 1   inner gradient passes over one rollout batch (`ppo_epochs`)
          typically 1 to 4.
          This is exactly why clipping exists: by pass 2+, the data is stale.
          With ppo_epochs=1, PPO is strictly on-policy and clipping is inert.

LEVEL 2   passes over the prompt dataset
          typically ONE, occasionally two. Runs are usually described in
          episodes or steps, and frequently stop before a full pass.

LEVEL 3   the reward model's own training (stage 1)
          ONE epoch. It overfits beyond that.
```

**So the lifetime of a single prompt is short:** generate one (or a few) responses,
score them, contribute to one batch, receive 1–4 gradient steps' worth of influence,
and then be retired — often never revisited.

**Why so few?** Section 1.22. The reward model is a proxy, and optimizing a proxy hard
makes it worse as a proxy. Practitioners typically do not fix an epoch count at all;
they monitor KL from the reference as a budget and stop when it is exhausted, or run
periodic evaluations and stop when true quality plateaus while reward is still
climbing.

## 4.13 Hyperparameters

Typical values, with the reasoning:

```
name              typical        notes
---------------   ------------   -------------------------------------------------
learning rate     1e-6 .. 1e-5   much lower than SFT; the signal is noisy
beta (KL coef)    0.01 .. 0.1    the main knob for the alignment/drift tradeoff
eps (clip)        0.2            remarkably robust; rarely needs tuning
gamma             1.0            no reason to discount within one response
lambda (GAE)      0.95           mostly Monte Carlo, mildly smoothed
ppo_epochs        1 .. 4         higher = more reuse, more staleness
c1 (value coef)   0.5 .. 1.0
c2 (entropy)      0.0 .. 0.01    often 0; KL penalty already resists collapse
batch size        512 .. 1024    prompts per iteration
minibatch size    32 .. 128
max_new_tokens    512 .. 2048    directly drives rollout cost
temperature       1.0            MUST match what the log-probs assume
top_p             1.0 (off)      truncation biases the gradient estimate
grad norm clip    1.0
target KL         3 .. 10        early-stopping threshold vs pi_ref
```

The lecture's warning about "many hyperparameters to tune" is well earned: the
interactions are real. In particular `beta`, `learning rate`, and `ppo_epochs` all
influence effective step size, so tuning them independently is misleading.

<!-- CONTINUES -->



# Question Bank

Open questions to revisit. Detailed context for each lives in
[`ppo-rlhf-complete-guide.md`](./ppo-rlhf-complete-guide.md), Part X.

---

## Q1. Why so few epochs in PPO, per prompt?

*Raised 2026-08-30. Context: CME 295 Lecture 5 (RLHF / PPO).*

**Working answer.** Reward hacking / Goodhart's law. The reward model is a learned
proxy fitted on roughly 10,000 comparisons, and it is only accurate near the SFT
model's output distribution. PPO is an optimizer, so it actively seeks the regions
where the proxy scores highest — which are disproportionately the regions where the
proxy is *wrong*. Train longer and reward keeps climbing while true quality falls.

The three nested repetition levels:

```
inner gradient passes over one rollout batch (ppo_epochs)   1 to 4
passes over the prompt dataset                              usually 1, sometimes 2
the reward model's own training                             exactly 1 (overfits beyond)
```

So a single prompt often gets generated once, scored once, and retired.

**Still open:**

- How is the KL budget threshold chosen in practice — tuned per task, or are there
  transferable defaults?
- Empirically, at what KL from the reference does true quality start degrading, and
  how does that scale with model size?
- How do `ppo_epochs` and clipping interact quantitatively? Is strictly on-policy
  (`ppo_epochs = 1`, clipping inert) better when you can afford the generation cost?
- Does iterative RLHF — refreshing the reward model on the current policy's outputs —
  actually buy meaningfully longer training?

---

## Q2. Credit assignment over long multi-step trajectories

*Raised 2026-08-30. Context: tool use / agentic RL.*

When a twenty-step tool-using trajectory ends in a single pass/fail signal, how is
credit assigned to the individual steps? The token-level value model degrades over
long branching trajectories, which motivates sequence-level group baselines.

**Still open:**

- What actually works for long-horizon agentic RL?
- How do process rewards (scoring intermediate steps) compare against outcome-only
  rewards?

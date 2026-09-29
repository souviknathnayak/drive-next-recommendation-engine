# Governance and deployment controls

## System boundary

The ranker accepts product metadata, consented preference fields, and behavioural events. It deliberately removes gender, age, ethnicity/race, religion, disability, and demographic labels before scoring. Protected attributes can be handled in a separately access-controlled offline audit dataset, never in online ranking.

The agent may generate a natural-language rationale, but product identifiers must come from the catalog tool result. A failed grounding check blocks automated delivery and raises `human_review_required`.

## Required operating procedure

1. Confirm purpose and whether the deployment is a high-risk AI use under EU AI Act Annex I/III with legal/compliance counsel.
2. Keep consent, retention, deletion, access control, DPIA, and lawful-basis evidence outside this repository.
3. Version catalog, ranker configuration, prompts, evaluation data, and every release decision.
4. Review monitor alerts daily; investigate grounding failures immediately and parity gaps above 0.15 before rollout.
5. Use a trained reviewer to approve remediation, model changes, and any edge case producing potentially harmful results.
6. Conduct pre-release and periodic adversarial and cohort evaluations; retain results and incidents for the formal technical documentation.

## Risk register starter

| Risk | Control | Signal | Owner |
|---|---|---|---|
| Invented product/reason | catalog allow-list + grounding | `grounding_failures` | ML owner |
| Intent drift | high-information clarifying question | `intent_shift` | Product |
| Disparate outcomes | cohort parity audit | `parity_gap` | Responsible AI |
| Prompt injection | treat user text as data; tools have fixed schemas | adversarial suite | Security |
| Runaway cost | per-request estimated-token monitoring | `estimated_tokens` | Platform |
| Harmful deployment | human review and conditional classification | review events | Compliance |

This is engineering guidance, not legal advice or a declaration of conformity. The high-risk requirements named in the service reflect [EU AI Act Regulation (EU) 2024/1689](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689), including Articles 9–17 and post-market monitoring under Article 72.

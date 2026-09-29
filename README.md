# DriveNext — Agentic Recommendation Engine

A privacy-conscious product recommendation prototype that combines a deterministic recommender with an LLM-ready agent layer. It is inspired by [Microsoft RecAI](https://github.com/microsoft/recai)'s recommender-agent pattern: the agent plans and explains, while catalog retrieval remains a bounded tool.

## What it does

- **Active learning:** detects preference/intent drift and asks a single high-information question or safely explores a new category.
- **Grounded recommendations:** ranks only products in the supplied catalog; explanations cite observed behaviour and preference signals.
- **Fairness controls:** protected attributes are excluded from ranking. An offline group parity audit detects disparate recommendation outcomes across gender and demographic cohorts.
- **Safety/evaluation:** catalog grounding checks, prompt-injection resistance, adversarial test cases, and a review gate for failures.
- **Operational monitoring:** per-request latency, estimated tokens, grounding/hallucination signals, recommendation diversity and fairness snapshots.
- **EU AI Act readiness:** a practical checklist for a conditional high-risk assessment. A retail recommender is not automatically an Annex III high-risk system; do not represent this prototype as legal conformity or CE-marked.

## Run

Requires Python 3.9+ and no third-party packages:

```powershell
py -m app.server
```

Open `http://localhost:8080`. The dashboard runs a demo shopper through the engine and displays the resulting evidence, monitor events, and governance status.

Run the test/evaluation suite:

```powershell
py -m unittest discover -s tests -v
```

## API

`POST /api/recommend`

```json
{
  "profile": {"user_id": "u-14", "preferences": ["trail", "sustainable"], "behaviour": [{"category": "outdoor", "event": "view"}]},
  "session_events": [{"category": "travel", "event": "search"}],
  "catalog": [{"id": "p1", "name": "Trail Pack", "category": "outdoor", "tags": ["trail", "sustainable"], "price": 79, "in_stock": true}]
}
```

The response includes `recommendations`, an optional `active_learning`, an `explanation`, `guardrails`, and a `trace_id`. Demographic fields may be provided only to the audit endpoint and are not accepted by the ranking model.

## EU AI Act readiness scope

The `conformity` response maps the engine's evidence to high-risk obligations if the deployment falls under Annex I/III (for example, a consequential eligibility, employment, education, credit, or essential-service decision). It covers risk management (Art. 9), data governance/bias examination (Art. 10), technical documentation (Art. 11), event logging (Art. 12), transparency/instructions (Art. 13), human oversight (Art. 14), accuracy/robustness/cybersecurity (Art. 15), quality management (Art. 17), and post-market monitoring (Art. 72). Legal classification and formal conformity assessment remain provider responsibilities.

See `docs/GOVERNANCE.md` for deployment controls and `docs/EVALUATION.md` for test acceptance thresholds.

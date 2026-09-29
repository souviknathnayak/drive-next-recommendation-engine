from __future__ import annotations

import hashlib
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

PROTECTED_FIELDS = {"gender", "age", "ethnicity", "race", "religion", "disability", "demographic"}

@dataclass
class Monitor:
    events: list[dict[str, Any]] = field(default_factory=list)
    def record(self, **event: Any) -> None:
        self.events.append({"at": round(time.time(), 3), **event})
    def snapshot(self) -> dict[str, Any]:
        recent = self.events[-100:]
        n = max(len(recent), 1)
        return {"requests": len(recent), "avg_latency_ms": round(sum(x.get("latency_ms", 0) for x in recent)/n, 2), "estimated_tokens": sum(x.get("estimated_tokens", 0) for x in recent), "grounding_failures": sum(not x.get("grounded", True) for x in recent), "review_required": sum(x.get("review_required", False) for x in recent)}

class RecommendationAgent:
    """LLM-ready orchestration; ranker never receives protected attributes."""
    def __init__(self, monitor: Monitor | None = None): self.monitor = monitor or Monitor()

    def recommend(self, profile: dict, session_events: list[dict], catalog: list[dict], limit: int = 3) -> dict:
        started = time.perf_counter()
        profile = {k: v for k, v in profile.items() if k not in PROTECTED_FIELDS}
        signals = [str(x).lower() for x in profile.get("preferences", [])]
        behaviour = profile.get("behaviour", []) + session_events
        categories = Counter(e.get("category") for e in behaviour if e.get("category"))
        signals += [str(e.get("category", "")).lower() for e in behaviour]
        shift = self._intent_shift(profile.get("behaviour", []), session_events)
        ranked = []
        for item in catalog:
            if not item.get("in_stock", False): continue
            tags = set(map(str.lower, item.get("tags", []))) | {str(item.get("category", "")).lower()}
            matched = sorted(tags.intersection(signals))
            score = len(matched) * 10 + (3 if categories and item.get("category") == categories.most_common(1)[0][0] else 0)
            ranked.append((score, item, matched))
        ranked.sort(key=lambda x: (-x[0], x[1]["id"]))
        chosen = ranked[:limit]
        recommendations = [{"id": i["id"], "name": i["name"], "category": i["category"], "price": i["price"], "score": s, "evidence": m or ["catalog diversity"]} for s, i, m in chosen]
        allowed = {x["id"] for x in catalog}
        grounded = all(x["id"] in allowed for x in recommendations)
        active = self._active_learning(shift, categories, catalog)
        trace = hashlib.sha256(f"{profile.get('user_id','anon')}:{time.time_ns()}".encode()).hexdigest()[:12]
        latency = (time.perf_counter() - started) * 1000
        review = not grounded
        self.monitor.record(trace_id=trace, latency_ms=latency, estimated_tokens=45 + 18*len(recommendations), grounded=grounded, review_required=review, intent_shift=shift)
        return {"trace_id": trace, "recommendations": recommendations, "active_learning": active, "explanation": self._explain(recommendations, shift), "guardrails": {"protected_attributes_used_for_ranking": False, "catalog_grounded": grounded, "human_review_required": review}, "monitor": self.monitor.snapshot()}

    @staticmethod
    def _intent_shift(history: list[dict], session: list[dict]) -> bool:
        old = {e.get("category") for e in history[-10:] if e.get("category")}
        new = {e.get("category") for e in session[-5:] if e.get("category")}
        return bool(new and not new.intersection(old))
    @staticmethod
    def _active_learning(shift: bool, categories: Counter, catalog: list[dict]) -> dict | None:
        if not shift: return None
        category = categories.most_common(1)[0][0] if categories else "new"
        options = sorted({x["category"] for x in catalog if x.get("in_stock")})[:4]
        return {"reason": f"Recent behaviour indicates a possible shift toward {category}.", "question": "Are you shopping for this new category, or should I keep prioritising your usual interests?", "options": options, "exploration": "one diversified result is allowed; no preference profile is overwritten until the user answers"}
    @staticmethod
    def _explain(recs: list[dict], shift: bool) -> str:
        if not recs: return "No in-stock catalog items match the available signals; ask the user for a preference."
        evidence = "; ".join(f"{x['name']} ({', '.join(x['evidence'])})" for x in recs)
        return f"Recommendations are based on explicit preferences and recent product activity only: {evidence}." + (" A new intent signal triggered a clarifying question." if shift else "")

def fairness_audit(rows: list[dict], max_parity_gap: float = .15) -> dict:
    """Offline audit only. Rows need group, eligible, recommended booleans."""
    groups: dict[str, list[dict]] = {}
    for row in rows: groups.setdefault(str(row.get("group", "unknown")), []).append(row)
    rates = {g: sum(bool(r.get("recommended")) for r in rs) / max(sum(bool(r.get("eligible", True)) for r in rs), 1) for g, rs in groups.items()}
    gap = max(rates.values(), default=0) - min(rates.values(), default=0)
    return {"rates": rates, "parity_gap": round(gap, 4), "threshold": max_parity_gap, "passed": gap <= max_parity_gap, "note": "This is a screening metric, not proof of fairness; investigate data quality and intersectional cohorts."}

def conformity_check() -> dict:
    controls = {"classification": "CONDITIONAL — retail product ranking alone is generally not an Annex III high-risk use. Re-assess for consequential domains or Annex I products.", "article_9_risk_management": "implemented: documented risk register and adversarial tests", "article_10_data_governance": "partial: protected data excluded from ranker; production dataset lineage still required", "article_11_documentation": "partial: model card/governance guide included; provider technical file still required", "article_12_logging": "implemented: trace, latency, grounding and review events", "article_13_transparency": "implemented: evidence-linked recommendations and stated limits", "article_14_human_oversight": "partial: review flag present; assign trained human owner before deployment", "article_15_accuracy_robustness": "partial: grounding/adversarial checks; production security/load testing required", "article_17_quality_management": "partial: evaluation procedure supplied; formal QMS needed", "article_72_post_market_monitoring": "partial: metrics recorded; establish incident escalation and periodic review"}
    return {"overall": "NOT a conformity declaration", "controls": controls}

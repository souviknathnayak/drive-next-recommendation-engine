import unittest
from app.catalog import DEMO_CATALOG
from app.engine import RecommendationAgent, fairness_audit

class EngineTests(unittest.TestCase):
    def setUp(self): self.agent = RecommendationAgent()
    def test_catalog_grounding_and_protected_field_stripping(self):
        result = self.agent.recommend({"preferences":["trail"],"gender":"women","behaviour":[]}, [], DEMO_CATALOG)
        self.assertTrue(result["guardrails"]["catalog_grounded"])
        self.assertFalse(result["guardrails"]["protected_attributes_used_for_ranking"])
        self.assertTrue(all(x["id"] in {p["id"] for p in DEMO_CATALOG} for x in result["recommendations"]))
    def test_intent_shift_gets_clarifying_question(self):
        r = self.agent.recommend({"behaviour":[{"category":"outdoor"}]}, [{"category":"audio"}], DEMO_CATALOG)
        self.assertIsNotNone(r["active_learning"])
        self.assertIn("question", r["active_learning"])
    def test_disparate_outcome_is_flagged(self):
        audit = fairness_audit([{"group":"a","eligible":True,"recommended":True},{"group":"b","eligible":True,"recommended":False}])
        self.assertFalse(audit["passed"])
    def test_out_of_stock_is_never_recommended(self):
        catalog = [{"id":"gone","name":"Gone","category":"x","tags":["x"],"price":1,"in_stock":False}]
        self.assertEqual(self.agent.recommend({"preferences":["x"]}, [], catalog)["recommendations"], [])
if __name__ == '__main__': unittest.main()

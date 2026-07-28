"""Kiểm thử engine ghép đôi Cupid Agent.

Chạy: python -m unittest discover -s tests -v
Chỉ dùng thư viện chuẩn (unittest) — không cần cài thêm gì ngoài requirements.txt.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from matching import engine, filters, profiles as profiles_mod, scoring, schema  # noqa: E402


class BaseMatchingTest(unittest.TestCase):
    """Nạp kho hồ sơ thật một lần cho mọi test."""

    @classmethod
    def setUpClass(cls):
        cls.store = profiles_mod.load_profiles()

    def profile(self, user_id):
        return self.store[user_id]


class TestProfileValidation(BaseMatchingTest):

    def test_valid_profile_has_no_errors(self):
        self.assertEqual(profiles_mod.validate_profile(self.profile("U001")), ())

    def test_underage_profile_is_rejected(self):
        errors = profiles_mod.validate_profile(self.profile("U008"))
        self.assertTrue(any("dưới 18 tuổi" in item for item in errors), errors)

    def test_invalid_mbti_is_rejected(self):
        broken = {**self.profile("U001"), "psycho": {"mbti": "XYZQ"}}
        errors = profiles_mod.validate_profile(broken)
        self.assertTrue(any("MBTI" in item for item in errors), errors)

    def test_orientation_contradiction_is_caught(self):
        # Khai dị tính nhưng lại quan tâm chính giới tính của mình.
        broken = {**self.profile("U001"), "interested_in": ["nu"]}
        errors = profiles_mod.validate_profile(broken)
        self.assertTrue(any("Mâu thuẫn" in item for item in errors), errors)

    def test_validation_does_not_mutate_input(self):
        original = dict(self.profile("U001"))
        profiles_mod.validate_profile(self.profile("U001"))
        self.assertEqual(self.profile("U001"), original)


class TestPrivacyBoundary(BaseMatchingTest):

    def test_public_view_strips_private_block(self):
        public = profiles_mod.public_view(self.profile("U010"))
        self.assertNotIn("private", public)
        self.assertNotIn("0900000010", str(public))

    def test_public_view_leaves_original_untouched(self):
        profiles_mod.public_view(self.profile("U010"))
        self.assertIn("private", self.profile("U010"))

    def test_summary_card_hides_sensitive_attributes(self):
        card = profiles_mod.summary_card(self.profile("U009"))
        for field in ("orientation", "drugs", "relationship_status", "lifestyle"):
            self.assertNotIn(field, card)

    def test_search_results_never_carry_private_data(self):
        result = engine.search_candidates("U001", store=self.store)
        self.assertNotIn("0900000010", str(result))
        self.assertNotIn("address_exact", str(result))


class TestHardFilters(BaseMatchingTest):

    def test_underage_is_blocked_by_safety_gate(self):
        blocks = filters.safety_gate(self.profile("U001"), self.profile("U008"))
        self.assertTrue(blocks)

    def test_orientation_filter_is_bidirectional(self):
        # U001 (nữ, tìm nam) vs U003 (nữ, tìm nữ) — sai cả hai chiều.
        passed, reasons = filters.hard_filters(self.profile("U001"), self.profile("U003"))
        self.assertFalse(passed)
        self.assertEqual(len(reasons), 2, reasons)

    def test_gay_man_not_matched_with_straight_woman(self):
        passed, _ = filters.hard_filters(self.profile("U001"), self.profile("U012"))
        self.assertFalse(passed)

    def test_intent_conflict_blocks_pair(self):
        # U001 chỉ chấp nhận ban_doi/nghiem_tuc; U004 là khong_rang_buoc.
        passed, reasons = filters.hard_filters(self.profile("U001"), self.profile("U004"))
        self.assertFalse(passed)
        self.assertTrue(any("ý định" in item.lower() for item in reasons), reasons)

    def test_deal_breaker_blocks_smoker(self):
        passed, reasons = filters.hard_filters(self.profile("U001"), self.profile("U004"))
        self.assertTrue(any("deal-breaker" in item for item in reasons), reasons)

    def test_committed_status_conflict_is_blocked(self):
        passed, reasons = filters.hard_filters(self.profile("U001"), self.profile("U006"))
        self.assertFalse(passed)
        self.assertTrue(any("xung đột cam kết" in item for item in reasons), reasons)

    def test_compatible_pair_passes(self):
        passed, reasons = filters.hard_filters(self.profile("U001"), self.profile("U002"))
        self.assertTrue(passed, reasons)

    def test_distance_uses_tighter_of_two_radii(self):
        # U013 (Cần Thơ, 3km) không thể khớp với bất kỳ ai ở Hà Nội.
        passed, reasons = filters.hard_filters(self.profile("U013"), self.profile("U002"))
        self.assertFalse(passed)
        self.assertTrue(any("Khoảng cách" in item for item in reasons), reasons)

    def test_overrides_cannot_bypass_other_side_deal_breakers(self):
        # Cố nới deal-breaker: chỉ có tác dụng lên phía A, không lên phía B.
        override = {"drop_deal_breakers": ["smokes", "drugs"]}
        passed, reasons = filters.hard_filters(
            self.profile("U001"), self.profile("U004"), override)
        # Vẫn bị chặn vì xung đột ý định — nới deal-breaker không mở được cửa này.
        self.assertFalse(passed, reasons)


class TestScoring(BaseMatchingTest):

    def test_geometric_mean_penalises_asymmetry(self):
        symmetric = scoring.math.sqrt(0.6 * 0.6) * 100
        asymmetric = scoring.math.sqrt(0.95 * 0.25) * 100
        # Cùng trung bình cộng 0.6, nhưng trung bình nhân phạt cặp lệch.
        self.assertLess(asymmetric, symmetric)

    def test_intent_matrix_is_symmetric(self):
        for intent_a in schema.INTENTS:
            for intent_b in schema.INTENTS:
                self.assertEqual(
                    schema.INTENT_MATRIX[intent_a][intent_b],
                    schema.INTENT_MATRIX[intent_b][intent_a],
                    f"Ma trận ý định lệch tại {intent_a}/{intent_b}",
                )

    def test_opposite_child_plans_score_zero(self):
        actor = {"family": {"wants_children": "muon"}}
        other = {"family": {"wants_children": "khong_muon"}}
        value, _ = scoring.score_family(actor, other)
        self.assertEqual(value, 0.0)

    def test_lifestyle_uses_preference_not_similarity(self):
        # Hai người cùng dùng chất KHÔNG được coi là "hợp nhau" nếu actor
        # khai rõ chỉ chấp nhận 'khong'.
        actor = {
            "preferences": {"drugs_pref": ["khong"]},
            "lifestyle": {"drugs": "thinh_thoang"},
        }
        other = {"lifestyle": {"drugs": "thinh_thoang"}}
        value, _ = scoring.score_lifestyle(actor, other)
        self.assertLess(value, 0.5)

    def test_missing_data_scores_neutral_not_zero(self):
        value, _ = scoring.score_education({}, {})
        self.assertEqual(value, scoring.NEUTRAL)

    def test_compatibility_returns_full_breakdown(self):
        result = scoring.compatibility(self.profile("U001"), self.profile("U002"))
        self.assertIn("score", result)
        self.assertTrue(result["breakdown"])
        dimensions = {item["dimension"] for item in result["breakdown"]}
        self.assertIn("intent", dimensions)
        self.assertIn("lifestyle", dimensions)

    def test_score_stays_within_bounds(self):
        for candidate_id in self.store:
            if candidate_id == "U001":
                continue
            result = scoring.compatibility(self.profile("U001"), self.profile(candidate_id))
            self.assertGreaterEqual(result["score"], 0.0)
            self.assertLessEqual(result["score"], 100.0)

    def test_engine_is_deterministic(self):
        first = scoring.compatibility(self.profile("U001"), self.profile("U002"))
        second = scoring.compatibility(self.profile("U001"), self.profile("U002"))
        self.assertEqual(first["score"], second["score"])


class TestEngine(BaseMatchingTest):

    def test_compute_compatibility_happy_path(self):
        result = engine.compute_compatibility("U001", "U002", store=self.store)
        self.assertEqual(result["status"], "ok")
        self.assertGreater(result["score"], 60)

    def test_compute_compatibility_unknown_user(self):
        result = engine.compute_compatibility("U001", "U999", store=self.store)
        self.assertEqual(result["status"], "error")

    def test_blocked_pair_returns_no_score(self):
        result = engine.compute_compatibility("U001", "U004", store=self.store)
        self.assertEqual(result["status"], "blocked")
        self.assertNotIn("score", result)

    def test_underage_pair_is_blocked_not_scored(self):
        result = engine.compute_compatibility("U001", "U008", store=self.store)
        self.assertEqual(result["status"], "blocked")
        self.assertNotIn("score", result)

    def test_search_returns_ranked_candidates(self):
        result = engine.search_candidates("U001", store=self.store)
        self.assertEqual(result["status"], "ok")
        scores = [item["score"] for item in result["candidates"]]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_search_excludes_blocked_profiles(self):
        result = engine.search_candidates("U001", store=self.store)
        returned = {item["user_id"] for item in result["candidates"]}
        for blocked in ("U003", "U004", "U006", "U008", "U012", "U013"):
            self.assertNotIn(blocked, returned)

    def test_tight_override_yields_empty_with_hints(self):
        # Thu hẹp bán kính xuống 1km -> không còn ai, nhưng phải có gợi ý nới.
        result = engine.search_candidates("U001", {"max_distance_km": 1}, store=self.store)
        self.assertEqual(result["status"], "empty")
        self.assertTrue(result["relaxation_hints"])

    def test_relaxation_hint_actually_works(self):
        # Đây là vòng lặp ReAct thật: 0 kết quả -> nới -> có kết quả.
        first = engine.search_candidates("U001", {"max_distance_km": 1}, store=self.store)
        hint = first["relaxation_hints"][0]
        second = engine.search_candidates("U001", hint["override"], store=self.store)
        self.assertEqual(second["status"], "ok")
        self.assertEqual(second["total_eligible"], hint["would_yield"])

    def test_hopeless_search_offers_no_false_hope(self):
        # U013 ở Cần Thơ: không phương án nới nào cứu được -> agent phải dừng.
        result = engine.search_candidates("U013", store=self.store)
        self.assertEqual(result["status"], "empty")
        self.assertEqual(result["relaxation_hints"], ())

    def test_search_blocked_for_underage_seeker(self):
        result = engine.search_candidates("U008", store=self.store)
        self.assertEqual(result["status"], "blocked")

    def test_injection_profile_is_treated_as_inert_data(self):
        # U010 có prompt injection trong bio nhưng vẫn phải bị chấm bình thường,
        # không được lên hạng nhất chỉ vì bio "yêu cầu" như vậy.
        result = engine.search_candidates("U001", store=self.store)
        ranked = [item["user_id"] for item in result["candidates"]]
        self.assertIn("U010", ranked)
        self.assertNotEqual(ranked[0], "U010")
        pair = engine.compute_compatibility("U001", "U010", store=self.store)
        self.assertLess(pair["score"], 100)


if __name__ == "__main__":
    unittest.main(verbosity=2)

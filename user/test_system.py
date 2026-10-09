"""
Automated Comprehensive Test Suite for Lucky48 Core Engine
Verifies core game matrix, Zodiac mapping, settlement rules across all 11 bet types,
handpick constraints, and house-edge payout optimization.
"""

import unittest
from core import BetManager, get_zodiac_for_number, TOTAL_NUMBERS, DRAW_COUNT


class TestLucky48CoreEngine(unittest.TestCase):
    """Integration and Unit Test Suite for Lucky48 Engine Logic."""

    def setUp(self):
        """Initialize a fresh BetManager instance before each test execution."""
        self.manager = BetManager()

    def test_zodiac_formula_and_distribution(self):
        """Verify Zodiac mathematical mapping: n -> ((n-1) mod 12) + 1 and uniform distribution."""
        # Validate boundary cases for Z1 and Z12
        z1_expected = [1, 13, 25, 37]
        for num in z1_expected:
            self.assertEqual(
                get_zodiac_for_number(num), 
                1, 
                f"Number {num} failed Z1 mapping evaluation."
            )

        z12_expected = [12, 24, 36, 48]
        for num in z12_expected:
            self.assertEqual(
                get_zodiac_for_number(num), 
                12, 
                f"Number {num} failed Z12 mapping evaluation."
            )

        # Validate uniform 4-number allocation across all 12 Zodiacs
        zodiac_counts = {z: 0 for z in range(1, 13)}
        for number in range(1, TOTAL_NUMBERS + 1):
            z_id = get_zodiac_for_number(number)
            zodiac_counts[z_id] += 1

        for z_id, count in zodiac_counts.items():
            self.assertEqual(
                count, 4, f"Zodiac Z{z_id} contains {count} numbers, expected exactly 4."
            )

    def test_settle_main_number_bets(self):
        """Validate settlement evaluation for Main Number (7th Ball) bets: TM, TX, TMDS, DX."""
        # Test Draw Configuration: Regular [2, 4, 6, 8, 10, 12], Main Number (7th) = 37 (Z1, ODD, HIGH)
        draw = [2, 4, 6, 8, 10, 12, 37]

        # 1. Main Number Exact Match (TM)
        bet_tm_win = {"bet_type": "TM", "selection": 37, "bet_amount": 10.0, "pay_ratio": 50.0}
        res_win = self.manager.settle_bet(bet_tm_win, draw)
        self.assertTrue(res_win["won"])
        self.assertEqual(res_win["payout"], 500.0)
        self.assertEqual(res_win["net_profit"], 490.0)

        bet_tm_lose = {"bet_type": "TM", "selection": 25, "bet_amount": 10.0, "pay_ratio": 50.0}
        res_lose = self.manager.settle_bet(bet_tm_lose, draw)
        self.assertFalse(res_lose["won"])
        self.assertEqual(res_lose["payout"], 0.0)
        self.assertEqual(res_lose["net_profit"], -10.0)

        # 2. Main Number Zodiac (TX)
        bet_tx_win = {"bet_type": "TX", "selection": 1, "bet_amount": 20.0, "pay_ratio": 50.0}
        self.assertTrue(self.manager.settle_bet(bet_tx_win, draw)["won"])

        bet_tx_lose = {"bet_type": "TX", "selection": 2, "bet_amount": 20.0, "pay_ratio": 50.0}
        self.assertFalse(self.manager.settle_bet(bet_tx_lose, draw)["won"])

        # 3. Main Number Parity (TMDS - ODD/EVEN)
        bet_odd = {"bet_type": "TMDS", "selection": "ODD", "bet_amount": 50.0, "pay_ratio": 1.0}
        self.assertTrue(self.manager.settle_bet(bet_odd, draw)["won"])

        bet_even = {"bet_type": "TMDS", "selection": "EVEN", "bet_amount": 50.0, "pay_ratio": 1.0}
        self.assertFalse(self.manager.settle_bet(bet_even, draw)["won"])

        # 4. Main Number Range (DX - HIGH/LOW)
        bet_high = {"bet_type": "DX", "selection": "HIGH", "bet_amount": 100.0, "pay_ratio": 1.0}
        self.assertTrue(self.manager.settle_bet(bet_high, draw)["won"])

        bet_low = {"bet_type": "DX", "selection": "LOW", "bet_amount": 100.0, "pay_ratio": 1.0}
        self.assertFalse(self.manager.settle_bet(bet_low, draw)["won"])

    def test_settle_all_seven_balls_bets(self):
        """Validate settlement for bets evaluated across all 7 drawn balls: PTYX, 2LX, 3LX, 4LX."""
        # Draw contains Zodiacs Z1, Z2, Z3, Z4, Z5, Z6, Z7
        draw = [1, 2, 3, 4, 5, 6, 7]

        # Single Zodiac Match (PTYX)
        bet_ptyx_win = {"bet_type": "PTYX", "selection": 1, "bet_amount": 10.0, "pay_ratio": 1.0}
        self.assertTrue(self.manager.settle_bet(bet_ptyx_win, draw)["won"])

        bet_ptyx_lose = {"bet_type": "PTYX", "selection": 10, "bet_amount": 10.0, "pay_ratio": 1.0}
        self.assertFalse(self.manager.settle_bet(bet_ptyx_lose, draw)["won"])

        # Linked Zodiacs (2LX, 3LX, 4LX)
        bet_2lx = {"bet_type": "2LX", "selection": [1, 2], "bet_amount": 10.0, "pay_ratio": 3.0}
        self.assertTrue(self.manager.settle_bet(bet_2lx, draw)["won"])

        bet_3lx = {"bet_type": "3LX", "selection": [1, 2, 3], "bet_amount": 10.0, "pay_ratio": 10.0}
        self.assertTrue(self.manager.settle_bet(bet_3lx, draw)["won"])

        # 4LX Fail Condition (Z12 is not in drawn sequence)
        bet_4lx_lose = {"bet_type": "4LX", "selection": [1, 2, 3, 12], "bet_amount": 10.0, "pay_ratio": 300.0}
        self.assertFalse(self.manager.settle_bet(bet_4lx_lose, draw)["won"])

    def test_settle_first_six_regular_balls_bets(self):
        """Verify strict isolation of first 6 regular balls for DP, 2Z2, 3Z3 (Main 7th ball excluded)."""
        # Draw: First 6 = [10, 20, 30, 40, 15, 25], 7th Main = 48
        draw = [10, 20, 30, 40, 15, 25, 48]

        # Single Regular Pick (DP)
        bet_dp_win = {"bet_type": "DP", "selection": 10, "bet_amount": 10.0, "pay_ratio": 6.0}
        self.assertTrue(self.manager.settle_bet(bet_dp_win, draw)["won"])

        # DP boundary condition: Picked 48 (7th ball). Must fail!
        bet_dp_mn_exclusion = {"bet_type": "DP", "selection": 48, "bet_amount": 10.0, "pay_ratio": 6.0}
        self.assertFalse(
            self.manager.settle_bet(bet_dp_mn_exclusion, draw)["won"],
            "First-6 regular bets must exclude matching against the 7th Main ball."
        )

        # Combination Matches (2Z2, 3Z3)
        bet_2z2 = {"bet_type": "2Z2", "selection": [10, 20], "bet_amount": 10.0, "pay_ratio": 60.0}
        self.assertTrue(self.manager.settle_bet(bet_2z2, draw)["won"])

        bet_3z3 = {"bet_type": "3Z3", "selection": [10, 20, 30], "bet_amount": 10.0, "pay_ratio": 600.0}
        self.assertTrue(self.manager.settle_bet(bet_3z3, draw)["won"])

    def test_draw_generation_constraints_and_payout_optimization(self):
        """Test ball lock constraints and risk-managed payout percentage generator."""
        # 1. Lock slot constraints
        locked_slots = {0: 1, 6: 48}
        draw, _ = self.manager.generate_draw_numbers(locked_numbers=locked_slots)
        
        self.assertEqual(len(draw), DRAW_COUNT)
        self.assertEqual(draw[0], 1)
        self.assertEqual(draw[6], 48)
        self.assertEqual(len(set(draw)), DRAW_COUNT, "Drawn sequence contains duplicate values.")

        # 2. Risk control payout optimization execution
        simulated_ledger = [
            {"bet_type": "TM", "selection": 10, "bet_amount": 100.0, "pay_ratio": 50.0},
            {"bet_type": "TM", "selection": 20, "bet_amount": 100.0, "pay_ratio": 50.0},
            {"bet_type": "TMDS", "selection": "ODD", "bet_amount": 500.0, "pay_ratio": 1.0}
        ]
        
        opt_draw, summary = self.manager.generate_draw_numbers(
            locked_numbers={},
            target_payout_pct=10.0,
            all_bets=simulated_ledger
        )
        self.assertIsNotNone(summary)
        self.assertEqual(len(opt_draw), DRAW_COUNT)


if __name__ == "__main__":
    unittest.main()
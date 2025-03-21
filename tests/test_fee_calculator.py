import unittest
from src.services.fee_calculator import FeeCalculator

class TestFeeCalculator(unittest.TestCase):

    def setUp(self):
        self.fee_calculator = FeeCalculator()
        self.inboundFee_base = -1000
        self.inboundFee_ratio = [1.2, 1.1, 1, 1, 1]
        self.LocalFee_ratio = [0.4, 0.6, 0.8, 1, 1.2]

    def test_calculate_inbound_fee(self):
        local_balance = 5000
        capacity = 10000
        expected_fee = self.inboundFee_base * self.inboundFee_ratio[2]  # Assuming 50% ratio
        calculated_fee = self.fee_calculator.calculate_inbound_fee(local_balance, capacity)
        self.assertEqual(calculated_fee, expected_fee)

    def test_calculate_local_fee(self):
        amboss_fee = 100
        local_balance = 8000
        capacity = 10000
        expected_fee = amboss_fee * self.LocalFee_ratio[3]  # Assuming 80% ratio
        calculated_fee = self.fee_calculator.calculate_local_fee(local_balance, capacity, amboss_fee)
        self.assertEqual(calculated_fee, expected_fee)

    def test_adjust_local_fee(self):
        current_local_fee = 100
        local_balance_ratio = 0.55  # 55%
        adjusted_fee = self.fee_calculator.adjust_local_fee(current_local_fee, local_balance_ratio)
        self.assertEqual(adjusted_fee, current_local_fee * 0.9)  # Should decrease by 10%

    def test_fee_calculation_with_fixed_channels(self):
        fixed_channels = [("channel1", "id1", 50), ("channel2", "id2", 100)]
        for channel in fixed_channels:
            channel_name, channel_id, fee = channel
            calculated_fee = self.fee_calculator.calculate_fixed_fee(channel_name, fee)
            self.assertEqual(calculated_fee, fee)  # Fixed fee should remain the same

if __name__ == '__main__':
    unittest.main()
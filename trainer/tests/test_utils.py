import unittest
from datetime import datetime
from trainer.utils import free_slots

class TestFreeSlotsFunction(unittest.TestCase):

    def setUp(self):
        self.trainer_slots = [
            (datetime(2025, 1, 2, 9, 0), datetime(2025, 1, 2, 12, 0)),
            (datetime(2025, 1, 2, 13, 0), datetime(2025, 1, 2, 15, 0))
        ]
        self.booked_slots = []
        self.training_time = 30
        self.interval = 15

    def test_free_slots_basic(self):
        expected_result = [
            datetime(2025, 1, 2, 9, 0),
            datetime(2025, 1, 2, 9, 15),
            datetime(2025, 1, 2, 9, 30),
            datetime(2025, 1, 2, 9, 45),
            datetime(2025, 1, 2, 10, 00),
            datetime(2025, 1, 2, 10, 15),
            datetime(2025, 1, 2, 10, 30),
            datetime(2025, 1, 2, 10, 45),
            datetime(2025, 1, 2, 11, 00),
            datetime(2025, 1, 2, 11, 15),
            datetime(2025, 1, 2, 11, 30),
            datetime(2025, 1, 2, 13, 00),
            datetime(2025, 1, 2, 13, 15),
            datetime(2025, 1, 2, 13, 30),
            datetime(2025, 1, 2, 13, 45),
            datetime(2025, 1, 2, 14, 00),
            datetime(2025, 1, 2, 14, 15),
            datetime(2025, 1, 2, 14, 30),
        ]
        result = free_slots(self.trainer_slots, self.booked_slots, self.training_time, self.interval)
        self.assertEqual(result, expected_result)

    def test_free_slots_no_available_slots(self):
        booked_slots = [
            (datetime(2025, 1, 2, 9, 0), datetime(2025, 1, 2, 12, 0)),
            (datetime(2025, 1, 2, 13, 0), datetime(2025, 1, 2, 15, 0)),
        ]
        result = free_slots(self.trainer_slots, booked_slots, self.training_time, self.interval)
        self.assertEqual(result, [])

    def test_free_slots_with_booking(self):
        booked_slots = [
            (datetime(2025, 1, 2, 9, 0), datetime(2025, 1, 2, 9, 45)),
            (datetime(2025, 1, 2, 10, 30), datetime(2025, 1, 2, 11, 00))
        ]
        expected_result = [
            datetime(2025, 1, 2, 9, 45),
            datetime(2025, 1, 2, 10, 00),
            datetime(2025, 1, 2, 11, 00),
            datetime(2025, 1, 2, 11, 15),
            datetime(2025, 1, 2, 11, 30),
            datetime(2025, 1, 2, 13, 00),
            datetime(2025, 1, 2, 13, 15),
            datetime(2025, 1, 2, 13, 30),
            datetime(2025, 1, 2, 13, 45),
            datetime(2025, 1, 2, 14, 00),
            datetime(2025, 1, 2, 14, 15),
            datetime(2025, 1, 2, 14, 30),
        ]

        result = free_slots(self.trainer_slots, booked_slots, self.training_time, self.interval)
        self.assertEqual(result, expected_result)

    def test_free_slots_continuous_booking(self):
        booked_slots = [
            (datetime(2025, 1, 2, 9, 0), datetime(2025, 1, 2, 9, 45)),
            (datetime(2025, 1, 2, 9, 45), datetime(2025, 1, 2, 11, 00)),
            (datetime(2025, 1, 2, 11, 00), datetime(2025, 1, 2, 11, 45))
        ]
        expected_results= [
            datetime(2025, 1, 2, 13, 00),
            datetime(2025, 1, 2, 13, 15),
            datetime(2025, 1, 2, 13, 30),
            datetime(2025, 1, 2, 13, 45),
            datetime(2025, 1, 2, 14, 00),
            datetime(2025, 1, 2, 14, 15),
            datetime(2025, 1, 2, 14, 30),
        ]
        result = free_slots(self.trainer_slots, booked_slots, self.training_time, self.interval)
        self.assertEqual(result, expected_results)

    def test_free_slots_edge_case(self):
        trainer_slots = [
            (datetime(2025, 1, 2, 9, 0), datetime(2025, 1, 2, 9, 15))
        ]
        booked_slots = []
        training_time = 15
        expected_results = [
            datetime(2025, 1, 2, 9, 0)
        ]
        result = free_slots(trainer_slots, booked_slots, training_time, self.interval)
        self.assertEqual(result, expected_results)

    def test_free_slots_training60(self):
        training_time = 60
        expected_result = [
            datetime(2025, 1, 2, 9, 0),
            datetime(2025, 1, 2, 9, 15),
            datetime(2025, 1, 2, 9, 30),
            datetime(2025, 1, 2, 9, 45),
            datetime(2025, 1, 2, 10, 00),
            datetime(2025, 1, 2, 10, 15),
            datetime(2025, 1, 2, 10, 30),
            datetime(2025, 1, 2, 10, 45),
            datetime(2025, 1, 2, 11, 00),
            datetime(2025, 1, 2, 13, 00),
            datetime(2025, 1, 2, 13, 15),
            datetime(2025, 1, 2, 13, 30),
            datetime(2025, 1, 2, 13, 45),
            datetime(2025, 1, 2, 14, 00),
        ]
        result = free_slots(self.trainer_slots, self.booked_slots, training_time, self.interval)
        self.assertEqual(result, expected_result)

    def test_free_slots_training60_interval60(self):
        training_time = 60
        interval = 60
        expected_result = [
            datetime(2025, 1, 2, 9, 0),
            datetime(2025, 1, 2, 10, 00),
            datetime(2025, 1, 2, 11, 00),
            datetime(2025, 1, 2, 13, 00),
            datetime(2025, 1, 2, 14, 00),
        ]
        result = free_slots(self.trainer_slots, self.booked_slots, training_time, interval)
        self.assertEqual(result, expected_result)

    def test_free_slots_training60_interval60_booking(self):
        training_time = 60
        interval = 60
        booked_slots =   [
            (datetime(2025, 1, 2, 9, 17), datetime(2025, 1, 2, 11, 1)),
            ]
        expected_result = [
            datetime(2025, 1, 2, 13, 00),
            datetime(2025, 1, 2, 14, 00),
        ]
        result = free_slots(self.trainer_slots, booked_slots, training_time, interval)
        self.assertEqual(result, expected_result)
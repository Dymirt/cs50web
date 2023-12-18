from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from .models import Counter, Reading


class ReadingModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )
        self.counter = Counter.objects.create(
            user=self.user, title="Test Counter", unit="units"
        )
        self.reading = Reading.objects.create(
            counter=self.counter, date=date(2023, 7, 1), value=10.0
        )
        self.reading1 = Reading.objects.create(
            counter=self.counter, date=date(2023, 8, 1), value=20.0
        )
        self.reading2 = Reading.objects.create(
            counter=self.counter, date=date(2023, 9, 1), value=40.0
        )

    def test_reading_creation(self):
        self.assertEqual(self.reading.counter, self.counter)
        self.assertEqual(self.reading.date, date(2023, 7, 1))
        self.assertEqual(self.reading.value, 10.0)
        self.assertEqual(Reading.objects.count(), 3)

    def test_get_previous_reading(self):
        self.assertEqual(self.reading1.get_previous_reading(), self.reading)
        self.assertEqual(self.reading2.get_previous_reading(), self.reading1)

    def test_usage_in_units(self):
        self.assertEqual(self.reading.usage, 0)
        self.assertEqual(self.reading1.usage, 10)
        self.assertEqual(self.reading2.usage, 20)

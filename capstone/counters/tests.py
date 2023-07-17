from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from .models import Counter, Reading

User = get_user_model()


class ModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )
        self.counter = Counter.objects.create(
            user=self.user,
            title="Test Counter",
            consumable=True,
            unit="units",
            price_per_unit=2.5,
            fixed_price=10.0,
        )

        self.reading1 = Reading.objects.create(
            counter=self.counter, date=date(2023, 7, 1), value=10.0
        )
        self.reading2 = Reading.objects.create(
            counter=self.counter, date=date(2023, 7, 15), value=20.0
        )

    def test_get_previous_reading(self):
        self.assertEqual(self.reading2.get_previous_reading(), self.reading1)
        self.assertEqual(self.reading1.get_previous_reading(), None)

    def test_usage_in_units(self):
        self.assertEqual(self.reading2.usage_in_units(), self.reading2.value - self.reading1.value)
        self.assertEqual(self.reading1.usage_in_units(), None)

    def test_payment_consumable_with_usage(self):
        payment = self.reading2.payment()
        expected_payment = 10.0 * 2.5 + 10.0  # (usage * price_per_unit) + fixed_price
        self.assertEqual(payment, expected_payment)

    def test_payment_consumable_without_usage(self):
        self.reading3 = Reading.objects.create(
            counter=self.counter, date=date(2023, 7, 30), value=20.0
        )
        payment = self.reading3.payment()
        expected_payment = 10.0  # fixed_price only
        self.assertEqual(payment, expected_payment)

    def test_payment_non_consumable(self):
        self.counter.consumable = False
        self.counter.save()
        self.assertEqual(self.reading2.payment(), self.counter.fixed_price)
        self.assertEqual(self.reading1.payment(), None)

    def test_reading_validation(self):
        self.reading3 = Reading.objects.create(
            counter=self.counter, date=date(2023, 7, 30), value=30.0
        )


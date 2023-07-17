from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from django.urls import reverse
from django.contrib.auth.models import User
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
        self.assertEqual(self.reading2.usage_in_units(), 10)
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


class AddCounterReadingViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.counter = Counter.objects.create(user=self.user, title='Test Counter')
        self.url = reverse('counters:reading-create')
        self.client.login(username='testuser', password='testpassword')

    def test_valid_reading_addition(self):
        data = {'counter': self.counter.pk, 'date': '2023-07-28', 'value': 20}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after a successful addition
        self.assertEqual(Reading.objects.count(), 1)
        self.assertRedirects(response, reverse('counters:readings-list'))

    def test_invalid_counter_ownership(self):
        another_user = User.objects.create_user(username='anotheruser', password='testpassword')
        another_counter = Counter.objects.create(user=another_user, title='Another User Counter')
        data = {'counter': another_counter.pk, 'date': '2023-07-28', 'value': 20}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)  # Form is invalid, stays on the same page
        self.assertEqual(Reading.objects.count(), 0)

    def test_reading_addition_with_one_previous_reading(self):
        Reading.objects.create(counter=self.counter, date='2023-07-01', value=10)
        data = {'counter': self.counter.pk, 'date': '2023-07-28', 'value': 20}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after a successful addition
        self.assertEqual(Reading.objects.count(), 2)

    def test_reading_addition_with_multiple_previous_readings_same_month(self):
        Reading.objects.create(counter=self.counter, date='2023-07-01', value=10)
        Reading.objects.create(counter=self.counter, date='2023-07-15', value=15)
        data = {'counter': self.counter.pk, 'date': '2023-07-28', 'value': 20}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after a successful addition
        self.assertEqual(Reading.objects.count(), 2)

    def test_reading_addition_with_multiple_previous_readings_different_months(self):
        Reading.objects.create(counter=self.counter, date='2023-07-01', value=10)
        Reading.objects.create(counter=self.counter, date='2023-08-15', value=15)
        data = {'counter': self.counter.pk, 'date': '2023-09-28', 'value': 20}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after a successful addition
        self.assertEqual(Reading.objects.count(), 3)


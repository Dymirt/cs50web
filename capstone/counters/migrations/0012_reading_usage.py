# Generated by Django 4.0 on 2023-07-30 13:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("counters", "0011_payment_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="reading",
            name="usage",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]

# Generated by Django 4.0 on 2023-07-29 16:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("counters", "0008_alter_payment_reading"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="reading",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payment",
                to="counters.reading",
            ),
        ),
    ]

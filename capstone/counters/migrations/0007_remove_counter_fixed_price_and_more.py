# Generated by Django 4.0 on 2023-07-29 16:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('counters', '0006_alter_reading_value'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='counter',
            name='fixed_price',
        ),
        migrations.RemoveField(
            model_name='counter',
            name='price_per_unit',
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('price_per_unit', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('price_per_month', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('counter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='counters.counter')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('counter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='counters.counter')),
                ('reading', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='counters.counter')),
            ],
        ),
    ]

# Generated by Django 4.0.1 on 2022-03-05 06:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_alter_budget_unique_together_alter_budget_fplan_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyflowsheet',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]

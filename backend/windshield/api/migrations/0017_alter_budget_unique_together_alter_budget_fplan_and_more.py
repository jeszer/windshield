# Generated by Django 4.0.1 on 2022-03-04 16:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_rename_ds_id_dailyflow_df_id'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='budget',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='budget',
            name='fplan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to='api.financialstatementplan'),
        ),
        migrations.AlterField(
            model_name='budget',
            name='id',
            field=models.CharField(max_length=24, primary_key=True, serialize=False),
        ),
    ]
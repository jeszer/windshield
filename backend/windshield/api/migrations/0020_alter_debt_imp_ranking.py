# Generated by Django 4.0.1 on 2022-03-05 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_alter_asset_bsheet_id_alter_debt_bsheet_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debt',
            name='imp_ranking',
            field=models.IntegerField(default=0),
        ),
    ]

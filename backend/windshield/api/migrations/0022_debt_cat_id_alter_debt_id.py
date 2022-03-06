# Generated by Django 4.0.1 on 2022-03-06 05:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_asset_cat_id_alter_asset_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='debt',
            name='cat_id',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, to='api.category'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='debt',
            name='id',
            field=models.CharField(max_length=17, primary_key=True, serialize=False),
        ),
    ]

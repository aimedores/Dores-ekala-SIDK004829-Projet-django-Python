# Generated by Django 3.0 on 2022-04-08 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commande', '0002_auto_20220408_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='panier',
            name='quantite',
            field=models.IntegerField(default=0, verbose_name='Quantité'),
        ),
    ]

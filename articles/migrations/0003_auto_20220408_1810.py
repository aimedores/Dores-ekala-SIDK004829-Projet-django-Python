# Generated by Django 3.0 on 2022-04-08 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_article_quantite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='quantite',
            field=models.IntegerField(default=1, verbose_name='Quantité'),
        ),
    ]

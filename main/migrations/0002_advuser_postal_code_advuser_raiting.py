# Generated by Django 5.0.7 on 2024-08-03 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='advuser',
            name='postal_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='advuser',
            name='raiting',
            field=models.IntegerField(default=0, verbose_name='Rating'),
        ),
    ]

# Generated by Django 2.1.2 on 2018-12-02 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entrant',
            name='seed',
        ),
        migrations.AlterField(
            model_name='entrant',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='Name'),
        ),
    ]
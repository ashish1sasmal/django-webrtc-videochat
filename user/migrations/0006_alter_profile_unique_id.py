# Generated by Django 3.2.5 on 2021-12-24 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_alter_profile_unique_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='unique_id',
            field=models.CharField(default='6c670bad', max_length=8),
        ),
    ]
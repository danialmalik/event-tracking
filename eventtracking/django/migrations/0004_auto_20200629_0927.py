# Generated by Django 2.2.13 on 2020-06-29 09:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eventtracking_django', '0003_regexpfilter_is_enabled'),
    ]

    operations = [
        migrations.RenameField(
            model_name='regexpfilter',
            old_name='reg_exp_lists',
            new_name='regular_expressions',
        ),
    ]
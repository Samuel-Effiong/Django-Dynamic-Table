# Generated by Django 4.2.7 on 2023-12-19 08:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_dynamic_table', '0002_alter_tablecolumn_column_data_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cellvalue',
            old_name='column',
            new_name='table_column',
        ),
    ]

# Generated by Django 4.2.7 on 2023-12-18 22:21

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CellValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='DynamicTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_name', models.CharField(max_length=255, unique=True, verbose_name='Table Name')),
                ('table_description', models.TextField(blank=True, verbose_name='Table Description')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date Created')),
            ],
            options={
                'ordering': ('-date_created',),
            },
        ),
        migrations.CreateModel(
            name='TableRow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row_cells', models.ManyToManyField(blank=True, to='django_dynamic_table.cellvalue')),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_dynamic_table.dynamictable')),
            ],
        ),
        migrations.CreateModel(
            name='TableColumn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('column_name', models.CharField(max_length=255, unique=True)),
                ('column_data_type', models.CharField(max_length=15)),
                ('column_cells', models.ManyToManyField(blank=True, to='django_dynamic_table.cellvalue')),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_dynamic_table.dynamictable')),
            ],
        ),
        migrations.AddField(
            model_name='dynamictable',
            name='table_columns',
            field=models.ManyToManyField(blank=True, to='django_dynamic_table.tablecolumn'),
        ),
        migrations.AddField(
            model_name='dynamictable',
            name='table_rows',
            field=models.ManyToManyField(blank=True, to='django_dynamic_table.tablerow'),
        ),
        migrations.AddField(
            model_name='cellvalue',
            name='column',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_dynamic_table.tablecolumn'),
        ),
        migrations.AddField(
            model_name='cellvalue',
            name='table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_dynamic_table.dynamictable'),
        ),
        migrations.AddField(
            model_name='cellvalue',
            name='table_row',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='django_dynamic_table.tablerow'),
        ),
    ]

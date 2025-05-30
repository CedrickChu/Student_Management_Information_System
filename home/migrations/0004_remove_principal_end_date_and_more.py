# Generated by Django 5.1.3 on 2024-12-01 15:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_alter_teacher_status_principal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='principal',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='principal',
            name='start_date',
        ),
        migrations.AddField(
            model_name='principal',
            name='school_years',
            field=models.ManyToManyField(related_name='principals', to='home.schoolyear'),
        ),
        migrations.AlterField(
            model_name='principal',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='principal',
            name='teacher',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='home.teacher'),
        ),
    ]

# Generated by Django 5.2.3 on 2025-06-19 06:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mosqueapp', '0002_adminprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonthlyPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField()),
                ('month', models.PositiveSmallIntegerField(choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')])),
                ('amount', models.PositiveIntegerField()),
                ('paid', models.BooleanField(default=False)),
                ('paid_on', models.DateField(blank=True, null=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mosqueapp.member')),
            ],
            options={
                'ordering': ['-year', '-month'],
                'unique_together': {('member', 'year', 'month')},
            },
        ),
    ]

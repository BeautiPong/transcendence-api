# Generated by Django 4.2.14 on 2024-08-09 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friend', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='status',
            field=models.CharField(choices=[('AC', 'Accept'), ('RF', 'Refuse'), ('BL', 'Block'), ('PN', 'Pend'), ('SD', 'Send')], max_length=2),
        ),
    ]

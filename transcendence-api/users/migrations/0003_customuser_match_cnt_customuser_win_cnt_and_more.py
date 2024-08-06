

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_userid'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='match_cnt',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customuser',
            name='win_cnt',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='score',
            field=models.IntegerField(default=1000),
        ),
    ]

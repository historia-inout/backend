# Generated by Django 2.2.6 on 2019-10-19 12:50

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20191019_1229'),
    ]

    operations = [
        migrations.CreateModel(
            name='textDB',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summary', models.TextField()),
                ('sourceUrl', models.TextField()),
                ('dateTime', models.DateTimeField(default=datetime.datetime(2019, 10, 19, 12, 50, 38, 904606, tzinfo=utc))),
            ],
        ),
        migrations.AlterField(
            model_name='imagedb',
            name='dateTime',
            field=models.DateTimeField(default=datetime.datetime(2019, 10, 19, 12, 50, 38, 861191, tzinfo=utc)),
        ),
    ]

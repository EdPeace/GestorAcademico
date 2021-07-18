# Generated by Django 3.2.3 on 2021-07-15 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_academico', '0003_alter_ofertaacademica_periodo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ofertaacademica',
            name='anio',
            field=models.IntegerField(choices=[(2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021)], default=2021),
        ),
    ]

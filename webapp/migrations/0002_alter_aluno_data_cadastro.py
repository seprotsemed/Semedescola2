# Generated by Django 5.0.8 on 2024-08-22 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aluno',
            name='data_cadastro',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

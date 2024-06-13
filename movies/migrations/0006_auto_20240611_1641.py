# Generated by Django 2.2.28 on 2024-06-11 16:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0005_moviecomment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moviecomment',
            name='parent_comment_id',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='movies.MovieComment'),
        ),
    ]
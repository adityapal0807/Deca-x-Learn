# Generated by Django 5.0.1 on 2024-01-31 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0003_mindspace_conversation"),
    ]

    operations = [
        migrations.CreateModel(
            name="Image_conversation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("user_query", models.CharField(max_length=3000)),
            ],
        ),
        migrations.AddField(
            model_name="book",
            name="upload_path",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]

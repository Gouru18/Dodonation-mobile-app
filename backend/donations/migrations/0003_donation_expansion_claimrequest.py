import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("donations", "0002_donation_is_accepted"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="donation",
            name="category",
            field=models.CharField(
                choices=[
                    ("food", "Food"),
                    ("clothing", "Clothing"),
                    ("medical", "Medical"),
                    ("books", "Books"),
                    ("furniture", "Furniture"),
                    ("electronics", "Electronics"),
                    ("other", "Other"),
                ],
                default="other",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="donation",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="donation",
            name="description",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="donation",
            name="donor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="donations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="donation",
            name="expiry_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="donation",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="donations/"),
        ),
        migrations.AddField(
            model_name="donation",
            name="quantity",
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name="donation",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("claimed", "Claimed"),
                    ("completed", "Completed"),
                    ("expired", "Expired"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="donation",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="donation",
            name="title",
            field=models.CharField(max_length=200),
        ),
        migrations.RemoveField(
            model_name="donation",
            name="is_accepted",
        ),
        migrations.CreateModel(
            name="ClaimRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("message", models.TextField(blank=True, null=True)),
                ("date_requested", models.DateTimeField(auto_now_add=True)),
                ("date_responded", models.DateTimeField(blank=True, null=True)),
                (
                    "donation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="claim_requests",
                        to="donations.donation",
                    ),
                ),
                (
                    "receiver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="claim_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-date_requested"],
                "unique_together": {("donation", "receiver")},
            },
        ),
        migrations.AlterModelOptions(
            name="donation",
            options={"ordering": ["-created_at"]},
        ),
    ]

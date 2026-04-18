import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("donations", "0003_donation_expansion_claimrequest"),
        ("meetings", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="meeting",
            name="claim_request",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="meeting",
                to="donations.claimrequest",
            ),
        ),
        migrations.AddField(
            model_name="meeting",
            name="meeting_address",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="meeting",
            name="meeting_latitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name="meeting",
            name="meeting_longitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name="meeting",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("confirmed", "Confirmed"),
                    ("completed", "Completed"),
                    ("cancelled", "Cancelled"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="meeting",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name="meeting",
            name="donation",
        ),
        migrations.RemoveField(
            model_name="meeting",
            name="donor",
        ),
        migrations.RemoveField(
            model_name="meeting",
            name="ngo",
        ),
        migrations.RemoveField(
            model_name="meeting",
            name="is_accepted",
        ),
        migrations.AlterModelOptions(
            name="meeting",
            options={"ordering": ["-scheduled_time"]},
        ),
    ]

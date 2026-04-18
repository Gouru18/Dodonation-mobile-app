from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0002_meeting_workflow_updates"),
    ]

    operations = [
        migrations.AddField(
            model_name="meeting",
            name="google_meet_space_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="meeting",
            name="location_pinned_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="meeting",
            name="online_meeting_completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="meeting",
            name="physical_meeting_completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="meeting",
            name="status",
            field=models.CharField(
                choices=[
                    ("online_scheduled", "Online Meeting Scheduled"),
                    ("online_completed", "Online Meeting Completed"),
                    ("location_pinned", "Physical Meeting Point Pinned"),
                    ("physical_completed", "Physical Meeting Completed"),
                    ("cancelled", "Cancelled"),
                ],
                default="online_scheduled",
                max_length=20,
            ),
        ),
    ]

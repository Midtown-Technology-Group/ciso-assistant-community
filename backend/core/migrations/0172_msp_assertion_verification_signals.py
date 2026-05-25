from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0171_msp_provider_domain_boundary"),
    ]

    operations = [
        migrations.AddField(
            model_name="mspcontrolassertion",
            name="verification_source",
            field=models.CharField(
                blank=True,
                help_text="System or workflow that last verified this assertion.",
                max_length=200,
                null=True,
                verbose_name="Verification source",
            ),
        ),
        migrations.AddField(
            model_name="mspcontrolassertion",
            name="verification_reference",
            field=models.CharField(
                blank=True,
                help_text="External run, execution, or evidence reference for the last verification.",
                max_length=255,
                null=True,
                verbose_name="Verification reference",
            ),
        ),
        migrations.AddField(
            model_name="mspcontrolassertion",
            name="verification_summary",
            field=models.TextField(
                blank=True,
                help_text="Short machine-generated summary of the latest technical verification.",
                null=True,
                verbose_name="Verification summary",
            ),
        ),
        migrations.AddField(
            model_name="mspcontrolassertion",
            name="verification_payload",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Structured non-secret details from the latest technical verification.",
                verbose_name="Verification payload",
            ),
        ),
        migrations.AddField(
            model_name="mspcontrolassertion",
            name="last_verified_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Last verified at",
            ),
        ),
    ]

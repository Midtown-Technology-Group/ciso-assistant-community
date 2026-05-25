import uuid

import django.db.models.deletion
import iam.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0169_tasktemplate_filtering_labels"),
        ("iam", "0021_fix_auditee_iam_groups"),
    ]

    operations = [
        migrations.CreateModel(
            name="MSPControlAssertion",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                (
                    "is_published",
                    models.BooleanField(default=False, verbose_name="published"),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Name")),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="Description"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("degraded", "Degraded"),
                            ("in_progress", "In progress"),
                            ("expired", "Expired"),
                        ],
                        default="active",
                        max_length=32,
                        verbose_name="Status",
                    ),
                ),
                (
                    "result",
                    models.CharField(
                        choices=[
                            ("covered", "Covered"),
                            ("partially_covered", "Partially covered"),
                            ("not_covered", "Not covered"),
                            ("not_applicable", "Not applicable"),
                        ],
                        default="covered",
                        max_length=32,
                        verbose_name="Result",
                    ),
                ),
                (
                    "scope",
                    models.TextField(
                        blank=True,
                        help_text="What the MSP-operated control covers for target domains.",
                        null=True,
                        verbose_name="Coverage scope",
                    ),
                ),
                (
                    "evidence_note",
                    models.TextField(
                        blank=True,
                        help_text="Where customers and auditors should look for shared evidence.",
                        null=True,
                        verbose_name="Evidence note",
                    ),
                ),
                (
                    "effective_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="Effective date"
                    ),
                ),
                (
                    "expiry_date",
                    models.DateField(blank=True, null=True, verbose_name="Expiry date"),
                ),
                (
                    "applied_control",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="msp_assertions",
                        to="core.appliedcontrol",
                        verbose_name="Provider applied control",
                    ),
                ),
                (
                    "folder",
                    models.ForeignKey(
                        default=iam.models.Folder.get_root_folder_id,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_folder",
                        to="iam.folder",
                    ),
                ),
                (
                    "reference_control",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="msp_assertions",
                        to="core.referencecontrol",
                        verbose_name="Reference control",
                    ),
                ),
                (
                    "standards_folder",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="msp_standard_assertions",
                        to="iam.folder",
                        verbose_name="Standards domain",
                    ),
                ),
                (
                    "target_folders",
                    models.ManyToManyField(
                        blank=True,
                        related_name="inherited_msp_control_assertions",
                        to="iam.folder",
                        verbose_name="Covered customer domains",
                    ),
                ),
            ],
            options={
                "verbose_name": "MSP control assertion",
                "verbose_name_plural": "MSP control assertions",
            },
        ),
        migrations.AddConstraint(
            model_name="mspcontrolassertion",
            constraint=models.UniqueConstraint(
                fields=("folder", "applied_control", "name"),
                name="unique_msp_control_assertion_name",
            ),
        ),
    ]

import django.db.models.deletion
from django.db import migrations, models


def copy_folder_to_provider_folder(apps, schema_editor):
    MSPControlAssertion = apps.get_model("core", "MSPControlAssertion")
    for assertion in MSPControlAssertion.objects.all().only("id", "folder_id"):
        assertion.provider_folder_id = assertion.folder_id
        assertion.save(update_fields=["provider_folder"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0170_msp_control_assertions"),
        ("iam", "0021_fix_auditee_iam_groups"),
    ]

    operations = [
        migrations.AddField(
            model_name="mspcontrolassertion",
            name="provider_folder",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="msp_provider_assertions",
                to="iam.folder",
                verbose_name="Service provider domain",
            ),
        ),
        migrations.RunPython(
            copy_folder_to_provider_folder,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="mspcontrolassertion",
            name="provider_folder",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="msp_provider_assertions",
                to="iam.folder",
                verbose_name="Service provider domain",
            ),
        ),
        migrations.RemoveField(
            model_name="mspcontrolassertion",
            name="standards_folder",
        ),
    ]

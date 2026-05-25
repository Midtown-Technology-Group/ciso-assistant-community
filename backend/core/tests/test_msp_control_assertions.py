from datetime import date, timedelta

import pytest
from django.utils import timezone

from core.models import (
    AppliedControl,
    ComplianceAssessment,
    Framework,
    MSPControlAssertion,
    Perimeter,
    ReferenceControl,
    RequirementAssessment,
    RequirementNode,
)
from core.serializers import MSPControlAssertionWriteSerializer
from iam.models import Folder


@pytest.fixture
def msp_domains():
    root = Folder.objects.get(content_type=Folder.ContentType.ROOT)
    provider = Folder.objects.create(
        parent_folder=root,
        name="MTG MSP",
        description="MSP provider domain",
    )
    internal = Folder.objects.create(
        parent_folder=root,
        name="MTG Internal",
        description="MTG internal compliance domain",
    )
    customer = Folder.objects.create(
        parent_folder=provider,
        name="Customer A",
        description="Customer domain",
    )
    sibling_customer = Folder.objects.create(
        parent_folder=provider,
        name="Customer B",
        description="Customer domain",
    )
    return {
        "root": root,
        "provider": provider,
        "internal": internal,
        "customer": customer,
        "sibling_customer": sibling_customer,
    }


@pytest.fixture
def msp_control(msp_domains):
    reference_control = ReferenceControl.objects.create(
        folder=msp_domains["provider"],
        name="Disk encryption",
        ref_id="CIS-3.11",
        urn="urn:mtg:reference-control:disk-encryption",
        category="technical",
    )
    applied_control = AppliedControl.objects.create(
        folder=msp_domains["provider"],
        name="MTG managed disk encryption",
        ref_id="MTG-MSP-DISK-ENCRYPTION",
        reference_control=reference_control,
    )
    return {
        "reference_control": reference_control,
        "applied_control": applied_control,
    }


@pytest.fixture
def customer_requirement_assessment(msp_domains, msp_control):
    framework = Framework.objects.create(
        folder=msp_domains["provider"],
        name="CIS IG1",
        urn="urn:mtg:framework:cis-ig1",
    )
    requirement = RequirementNode.objects.create(
        folder=msp_domains["provider"],
        framework=framework,
        name="Encrypt endpoint disks",
        urn="urn:mtg:requirement:encrypt-endpoint-disks",
        ref_id="CIS-3.11",
        assessable=True,
        order_id=1,
        implementation_groups=["IG1"],
    )
    requirement.reference_controls.add(msp_control["reference_control"])
    perimeter = Perimeter.objects.create(
        folder=msp_domains["customer"],
        name="Customer estate",
    )
    assessment = ComplianceAssessment.objects.create(
        folder=msp_domains["customer"],
        perimeter=perimeter,
        framework=framework,
        name="Customer CIS IG1",
        min_score=0,
        max_score=100,
    )
    return RequirementAssessment.objects.create(
        folder=msp_domains["customer"],
        compliance_assessment=assessment,
        requirement=requirement,
    )


@pytest.mark.django_db
def test_msp_assertion_inherits_reference_control_from_applied_control(
    msp_domains, msp_control
):
    assertion = MSPControlAssertion.objects.create(
        folder=msp_domains["provider"],
        provider_folder=msp_domains["provider"],
        applied_control=msp_control["applied_control"],
        name="Disk encryption is centrally enforced",
    )

    assert assertion.reference_control == msp_control["reference_control"]


@pytest.mark.django_db
def test_msp_assertion_serializer_requires_customer_children(
    msp_domains, msp_control
):
    serializer = MSPControlAssertionWriteSerializer(
        data={
            "folder": str(msp_domains["provider"].id),
            "provider_folder": str(msp_domains["provider"].id),
            "applied_control": str(msp_control["applied_control"].id),
            "name": "Disk encryption is centrally enforced",
            "target_folders": [str(msp_domains["internal"].id)],
        }
    )

    assert not serializer.is_valid()
    assert "target_folders" in serializer.errors


@pytest.mark.django_db
def test_msp_assertion_serializer_accepts_provider_children(
    msp_domains, msp_control
):
    serializer = MSPControlAssertionWriteSerializer(
        data={
            "folder": str(msp_domains["provider"].id),
            "provider_folder": str(msp_domains["provider"].id),
            "applied_control": str(msp_control["applied_control"].id),
            "name": "Disk encryption is centrally enforced",
            "target_folders": [str(msp_domains["customer"].id)],
        }
    )

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_msp_assertion_records_bifrost_verification_signal(
    msp_domains, msp_control
):
    verified_at = timezone.now()
    assertion = MSPControlAssertion.objects.create(
        folder=msp_domains["provider"],
        provider_folder=msp_domains["provider"],
        applied_control=msp_control["applied_control"],
        name="Disk encryption is centrally enforced",
        result=MSPControlAssertion.CoverageResult.PARTIALLY_COVERED,
        status=MSPControlAssertion.CoverageStatus.DEGRADED,
        verification_source="Bifrost",
        verification_reference="workflow-run:disk-encryption:123",
        verification_summary="42 of 43 managed devices reported encrypted disks.",
        verification_payload={"encrypted": 42, "total": 43},
        last_verified_at=verified_at,
    )
    assertion.target_folders.add(msp_domains["customer"])

    assertion.refresh_from_db()

    assert assertion.verification_source == "Bifrost"
    assert assertion.verification_reference == "workflow-run:disk-encryption:123"
    assert assertion.verification_payload == {"encrypted": 42, "total": 43}
    assert assertion.last_verified_at == verified_at
    assert (
        assertion.to_requirement_assessment_result()
        == RequirementAssessment.Result.PARTIALLY_COMPLIANT
    )


@pytest.mark.django_db
def test_inherited_for_folder_returns_current_targeted_assertions_only(
    msp_domains, msp_control
):
    current = MSPControlAssertion.objects.create(
        folder=msp_domains["provider"],
        provider_folder=msp_domains["provider"],
        applied_control=msp_control["applied_control"],
        name="Current disk encryption coverage",
    )
    current.target_folders.add(msp_domains["customer"])
    expired = MSPControlAssertion.objects.create(
        folder=msp_domains["provider"],
        provider_folder=msp_domains["provider"],
        applied_control=msp_control["applied_control"],
        name="Expired disk encryption coverage",
        expiry_date=date.today() - timedelta(days=1),
    )
    expired.target_folders.add(msp_domains["customer"])
    future = MSPControlAssertion.objects.create(
        folder=msp_domains["provider"],
        provider_folder=msp_domains["provider"],
        applied_control=msp_control["applied_control"],
        name="Future disk encryption coverage",
        effective_date=date.today() + timedelta(days=1),
    )
    future.target_folders.add(msp_domains["customer"])
    status_expired = MSPControlAssertion.objects.create(
        folder=msp_domains["provider"],
        provider_folder=msp_domains["provider"],
        applied_control=msp_control["applied_control"],
        name="Status-expired disk encryption coverage",
        status=MSPControlAssertion.CoverageStatus.EXPIRED,
    )
    status_expired.target_folders.add(msp_domains["customer"])
    other_customer = MSPControlAssertion.objects.create(
        folder=msp_domains["provider"],
        provider_folder=msp_domains["provider"],
        applied_control=msp_control["applied_control"],
        name="Other customer disk encryption coverage",
    )
    other_customer.target_folders.add(msp_domains["sibling_customer"])

    coverage = MSPControlAssertion.inherited_for_folder(msp_domains["customer"])

    assert list(coverage) == [current]


@pytest.mark.django_db
def test_inherited_for_requirement_assessment_matches_reference_control(
    msp_domains, msp_control, customer_requirement_assessment
):
    assertion = MSPControlAssertion.objects.create(
        folder=msp_domains["provider"],
        provider_folder=msp_domains["provider"],
        applied_control=msp_control["applied_control"],
        name="Disk encryption satisfies customer requirement",
        scope="MTG enforces endpoint disk encryption through central management.",
    )
    assertion.target_folders.add(msp_domains["customer"])

    coverage = MSPControlAssertion.inherited_for_requirement_assessment(
        customer_requirement_assessment
    )

    assert list(coverage) == [assertion]


@pytest.mark.django_db
def test_sync_to_applied_controls_uses_inherited_msp_coverage(
    msp_domains, msp_control, customer_requirement_assessment
):
    assertion = MSPControlAssertion.objects.create(
        folder=msp_domains["provider"],
        provider_folder=msp_domains["provider"],
        applied_control=msp_control["applied_control"],
        name="Disk encryption satisfies customer requirement",
    )
    assertion.target_folders.add(msp_domains["customer"])
    assessment = customer_requirement_assessment.compliance_assessment

    changes = assessment.sync_to_applied_controls(dry_run=True)

    assert changes[str(customer_requirement_assessment.id)]["changes"] == [
        {
            "current": RequirementAssessment.Result.NOT_ASSESSED,
            "new": RequirementAssessment.Result.COMPLIANT,
        }
    ]
    customer_requirement_assessment.refresh_from_db()
    assert customer_requirement_assessment.result == RequirementAssessment.Result.NOT_ASSESSED

    assessment.sync_to_applied_controls(dry_run=False)
    customer_requirement_assessment.refresh_from_db()

    assert customer_requirement_assessment.result == RequirementAssessment.Result.COMPLIANT


@pytest.mark.django_db
def test_sync_to_applied_controls_preserves_local_control_authority(
    msp_domains, msp_control, customer_requirement_assessment
):
    assertion = MSPControlAssertion.objects.create(
        folder=msp_domains["provider"],
        provider_folder=msp_domains["provider"],
        applied_control=msp_control["applied_control"],
        name="Inherited disk encryption coverage",
    )
    assertion.target_folders.add(msp_domains["customer"])
    local_control = AppliedControl.objects.create(
        folder=msp_domains["customer"],
        name="Customer-managed disk encryption exception",
        ref_id="CUSTOMER-DISK-ENCRYPTION",
        reference_control=msp_control["reference_control"],
        status=AppliedControl.Status.DEPRECATED,
    )
    customer_requirement_assessment.applied_controls.add(local_control)
    assessment = customer_requirement_assessment.compliance_assessment

    assessment.sync_to_applied_controls(dry_run=False)
    customer_requirement_assessment.refresh_from_db()

    assert (
        customer_requirement_assessment.result
        == RequirementAssessment.Result.NON_COMPLIANT
    )


@pytest.mark.django_db
def test_sync_to_applied_controls_maps_degraded_msp_coverage_to_partial(
    msp_domains, msp_control, customer_requirement_assessment
):
    assertion = MSPControlAssertion.objects.create(
        folder=msp_domains["provider"],
        provider_folder=msp_domains["provider"],
        applied_control=msp_control["applied_control"],
        name="Degraded disk encryption coverage",
        status=MSPControlAssertion.CoverageStatus.DEGRADED,
    )
    assertion.target_folders.add(msp_domains["customer"])
    assessment = customer_requirement_assessment.compliance_assessment

    assessment.sync_to_applied_controls(dry_run=False)
    customer_requirement_assessment.refresh_from_db()

    assert (
        customer_requirement_assessment.result
        == RequirementAssessment.Result.PARTIALLY_COMPLIANT
    )

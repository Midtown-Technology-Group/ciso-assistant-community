from datetime import date, timedelta

import pytest

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
from iam.models import Folder


@pytest.fixture
def msp_domains():
    root = Folder.objects.get(content_type=Folder.ContentType.ROOT)
    provider = Folder.objects.create(
        parent_folder=root,
        name="MTG Provider",
        description="MSP provider domain",
    )
    standards = Folder.objects.create(
        parent_folder=root,
        name="MTG Global MSP Standards",
        description="Global MSP standards domain",
    )
    customer = Folder.objects.create(
        parent_folder=root,
        name="Customer A",
        description="Customer domain",
    )
    sibling_customer = Folder.objects.create(
        parent_folder=root,
        name="Customer B",
        description="Customer domain",
    )
    return {
        "root": root,
        "provider": provider,
        "standards": standards,
        "customer": customer,
        "sibling_customer": sibling_customer,
    }


@pytest.fixture
def msp_control(msp_domains):
    reference_control = ReferenceControl.objects.create(
        folder=msp_domains["standards"],
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
        folder=msp_domains["standards"],
        name="CIS IG1",
        urn="urn:mtg:framework:cis-ig1",
    )
    requirement = RequirementNode.objects.create(
        folder=msp_domains["standards"],
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
        standards_folder=msp_domains["standards"],
        applied_control=msp_control["applied_control"],
        name="Disk encryption is centrally enforced",
    )

    assert assertion.reference_control == msp_control["reference_control"]


@pytest.mark.django_db
def test_inherited_for_folder_returns_current_targeted_assertions_only(
    msp_domains, msp_control
):
    current = MSPControlAssertion.objects.create(
        folder=msp_domains["provider"],
        standards_folder=msp_domains["standards"],
        applied_control=msp_control["applied_control"],
        name="Current disk encryption coverage",
    )
    current.target_folders.add(msp_domains["customer"])
    expired = MSPControlAssertion.objects.create(
        folder=msp_domains["provider"],
        standards_folder=msp_domains["standards"],
        applied_control=msp_control["applied_control"],
        name="Expired disk encryption coverage",
        expiry_date=date.today() - timedelta(days=1),
    )
    expired.target_folders.add(msp_domains["customer"])
    future = MSPControlAssertion.objects.create(
        folder=msp_domains["provider"],
        standards_folder=msp_domains["standards"],
        applied_control=msp_control["applied_control"],
        name="Future disk encryption coverage",
        effective_date=date.today() + timedelta(days=1),
    )
    future.target_folders.add(msp_domains["customer"])
    other_customer = MSPControlAssertion.objects.create(
        folder=msp_domains["provider"],
        standards_folder=msp_domains["standards"],
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
        standards_folder=msp_domains["standards"],
        applied_control=msp_control["applied_control"],
        name="Disk encryption satisfies customer requirement",
        scope="MTG enforces endpoint disk encryption through central management.",
    )
    assertion.target_folders.add(msp_domains["customer"])

    coverage = MSPControlAssertion.inherited_for_requirement_assessment(
        customer_requirement_assessment
    )

    assert list(coverage) == [assertion]

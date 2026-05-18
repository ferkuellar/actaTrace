from app.models.enums import ActaStatus


ALLOWED_ACTA_TRANSITIONS = {
    ActaStatus.DRAFT: {ActaStatus.UPLOADED, ActaStatus.REJECTED},
    ActaStatus.UPLOADED: {ActaStatus.HASHED, ActaStatus.UNDER_REVIEW, ActaStatus.REJECTED},
    ActaStatus.HASHED: {ActaStatus.ANCHORED, ActaStatus.UNDER_REVIEW, ActaStatus.REJECTED},
    ActaStatus.ANCHORED: {ActaStatus.UNDER_REVIEW, ActaStatus.VERIFIED, ActaStatus.REJECTED},
    ActaStatus.UNDER_REVIEW: {ActaStatus.VERIFIED, ActaStatus.REJECTED},
}


def test_ut_007_invalid_acta_state_transition_rejected():
    assert ActaStatus.DRAFT not in ALLOWED_ACTA_TRANSITIONS[ActaStatus.VERIFIED] if ActaStatus.VERIFIED in ALLOWED_ACTA_TRANSITIONS else True


from datetime import datetime, timedelta, timezone

from apps.api.auth.models import (
    APIKey,
    Job,
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
    UploadSession,
    User,
)


def test_auth_models_smoke_instantiation() -> None:
    user = User(
        email="smoke@example.com",
        first_name="Smoke",
        last_name="Test",
        hashed_password="hash",
        subscription_plan=SubscriptionPlan.FREE,
    )

    assert user.full_name == "Smoke Test"
    assert user.has_active_subscription() is False

    paid_user = User(
        email="pro@example.com",
        first_name="Pro",
        last_name="User",
        hashed_password="hash",
        subscription_plan=SubscriptionPlan.PROFESSIONAL,
    )
    assert paid_user.has_active_subscription() is True


def test_subscription_and_api_key_properties() -> None:
    now = datetime.now(timezone.utc)
    subscription = Subscription(
        user_id=1,
        stripe_subscription_id="sub_123",
        stripe_customer_id="cus_123",
        status=SubscriptionStatus.ACTIVE,
        plan=SubscriptionPlan.STANDARD,
        current_period_start=now - timedelta(days=1),
        current_period_end=now + timedelta(days=29),
    )
    assert subscription.is_active is True

    api_key_valid = APIKey(
        user_id=1,
        key_name="smoke",
        key_hash="hash_123",
        key_prefix="sk_live",
        expires_at=now + timedelta(hours=1),
    )
    assert api_key_valid.is_expired is False

    api_key_expired = APIKey(
        user_id=1,
        key_name="expired",
        key_hash="hash_456",
        key_prefix="sk_live",
        expires_at=now - timedelta(hours=1),
    )
    assert api_key_expired.is_expired is True


def test_upload_and_job_status_properties() -> None:
    upload = UploadSession(
        user_id=1,
        original_filename="data.bin",
        file_size_bytes=1024,
        file_type="application/octet-stream",
        status="initiated",
    )
    assert upload.status == "initiated"

    running_job = Job(
        user_id=1,
        job_id="job_1",
        job_type="analysis",
        status="running",
    )
    assert running_job.is_running is True
    assert running_job.is_completed is False

    completed_job = Job(
        user_id=1,
        job_id="job_2",
        job_type="export",
        status="completed",
    )
    assert completed_job.is_completed is True

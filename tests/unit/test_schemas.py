import pytest
from pydantic import ValidationError

from app.schemas.client import ClientCreateSchema
from app.schemas.domain import DomainUpdateSchema
from app.schemas.forms import parse_form
from app.schemas.info import InfoUpdateSchema
from app.schemas.plan import PlanUpdateSchema
from app.schemas.user import UserCreateSchema, UserUpdateSchema


class DummyForm(dict):
    """Minimal MultiDict-like object for parse_form tests."""

    def get(self, key, default=None):  # pragma: no cover - simple proxy
        return super().get(key, default)

    def getlist(self, key):
        value = super().get(key, None)
        if isinstance(value, list):
            return value
        if value is None:
            return []
        return [value]

    def to_dict(self):  # pragma: no cover - compatibility helper
        return dict(self)


def test_domain_update_schema_normalizes_boolean_flags():
    schema = DomainUpdateSchema(
        cloudflare_status="on",
        ssl="0",
        domain_limit=10,
    )

    payload = schema.to_payload()

    assert payload["cloudflare_status"] is True
    assert payload["ssl"] is False
    assert payload["domain_limit"] == 10


def test_client_create_schema_masks_password_in_audit_payload():
    schema = ClientCreateSchema(
        username="tester",
        password="secret123",
        status="active",
    )

    audit = schema.audit_payload()

    assert "password" not in audit
    assert audit["username"] == "tester"


def test_client_create_schema_validates_object_ids():
    with pytest.raises(ValidationError):
        ClientCreateSchema(
            username="tester",
            password="secret123",
            plan_id="123",  # invalid length
        )


def test_parse_form_excludes_empty_strings():
    form = DummyForm(
        username="tester",
        password="secret123",
        plan_activation_date="",
    )

    schema, errors = parse_form(ClientCreateSchema, form)

    assert errors == []
    assert schema is not None
    assert schema.plan_activation_date is None
    assert schema.status == "active"


def test_update_form_model_excludes_unset_fields():
    schema = PlanUpdateSchema(name="Premium")

    payload = schema.to_payload()

    assert payload == {"name": "Premium"}


def test_plan_update_schema_audit_payload():
    schema = PlanUpdateSchema(name="Premium", price=99.99)

    audit = schema.audit_payload()

    assert audit == {"name": "Premium", "price": 99.99}


def test_domain_update_schema_audit_payload_masks_sensitive():
    schema = DomainUpdateSchema(
        name="example.com",
        cloudflare_api="secret_api_key",
        cloudflare_email="user@example.com",
        cloudflare_password="secret_pass",
        domain_limit=10,
    )

    audit = schema.audit_payload()

    assert "cloudflare_api" not in audit
    assert "cloudflare_email" not in audit
    assert "cloudflare_password" not in audit
    assert audit["name"] == "example.com"
    assert audit["domain_limit"] == 10


def test_info_update_schema_audit_payload_masks_sensitive():
    schema = InfoUpdateSchema(
        agencia="1234",
        conta="56789",
        senha="secret1",
        senha6="secret6",
        senha4="secret4",
        saldo=1000.0,
    )

    audit = schema.audit_payload()

    assert "senha" not in audit
    assert "senha6" not in audit
    assert "senha4" not in audit
    assert audit["agencia"] == "1234"
    assert audit["conta"] == "56789"
    assert audit["saldo"] == 1000.0


def test_user_create_schema_audit_payload_masks_password():
    schema = UserCreateSchema(username="testuser", password="secret123")

    audit = schema.audit_payload()

    assert "password" not in audit
    assert audit["username"] == "testuser"


def test_user_update_schema_audit_payload_masks_password():
    schema = UserUpdateSchema(username="testuser", password="newsecret")

    audit = schema.audit_payload()

    assert "password" not in audit
    assert audit["username"] == "testuser"
"""Unit tests for the main health-check endpoint."""

from __future__ import annotations

import pytest


@pytest.mark.unit
def test_health_endpoint_with_secret_configured(client, test_app):
    test_app.config["HELEKET_WEBHOOK_SECRET"] = "configured"

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["webhook_secret_configured"] is True
    assert "timestamp" in payload


@pytest.mark.unit
def test_health_endpoint_without_secret(client, test_app):
    test_app.config.pop("HELEKET_WEBHOOK_SECRET", None)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["webhook_secret_configured"] is False
    assert "timestamp" in payload

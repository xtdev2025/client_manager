"""Tests for the payout reconciliation CLI command."""


def test_reconcile_cli_invokes_service(runner, monkeypatch):
    captured = {}

    def _fake_schedule_pending(**kwargs):
        captured["kwargs"] = kwargs
        return {"checked": 1, "finalized": 0, "alerts": 0, "errors": 0}

    monkeypatch.setattr(
        "app.services.payout_reconciliation_service.PayoutReconciliationService.schedule_pending",
        _fake_schedule_pending,
    )

    result = runner.invoke(args=["reconcile-payouts", "--limit", "5"])

    assert result.exit_code == 0
    assert "checked=1" in result.output
    assert captured["kwargs"]["limit"] == 5

from contact_service import ContactKind, ContactRequest, route_contact


def test_donation_routes_a_receipt_to_team(monkeypatch):
    calls = []
    monkeypatch.setattr("contact_service.send_email", lambda *args: calls.append(args) or {"message_id": "m-123"})
    result = route_contact(ContactRequest("Ada", "ada@example.org", ContactKind.DONATION, "receipt please", 2500), "team@example.org")
    assert result.kind is ContactKind.DONATION
    assert result.message_id == "m-123"
    assert calls[0][0] == "team@example.org"
    assert calls[0][1] == "Donation receipt for Ada"


def test_invalid_contact_is_rejected_before_delivery(monkeypatch):
    monkeypatch.setattr("contact_service.send_email", lambda *args: (_ for _ in ()).throw(AssertionError("sent")))
    try:
        route_contact(ContactRequest("", "bad", ContactKind.VOLUNTEER, "help"), "team@example.org")
    except ValueError as exc:
        assert "valid email" in str(exc)
    else:
        raise AssertionError("expected validation error")

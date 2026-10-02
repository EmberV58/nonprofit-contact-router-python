from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from infrai_client import send_email


class ContactKind(str, Enum):
    DONATION = "donation"
    VOLUNTEER = "volunteer"
    CAMPAIGN = "campaign"


@dataclass(frozen=True)
class ContactRequest:
    name: str
    email: str
    kind: ContactKind
    message: str
    amount_cents: int | None = None


@dataclass(frozen=True)
class Delivery:
    kind: ContactKind
    message_id: str
    subject: str


def route_contact(request: ContactRequest, team_inbox: str) -> Delivery:
    if not request.name.strip() or "@" not in request.email:
        raise ValueError("name and a valid email are required")
    if request.kind is ContactKind.DONATION:
        subject = f"Donation receipt for {request.name}"
        body = f"Thank you, {request.name}. We recorded your donation inquiry."
    elif request.kind is ContactKind.VOLUNTEER:
        subject = f"Volunteer follow-up for {request.name}"
        body = f"Thanks, {request.name}. The volunteer coordinator will reply soon."
    else:
        subject = f"Campaign report request from {request.name}"
        body = f"Campaign reporting request: {request.message}"
    result = send_email(team_inbox, subject, body, f"contact-{request.kind.value}-{request.email}")
    return Delivery(request.kind, str(result["message_id"]), subject)

import json
import sys

from contact_service import ContactKind, ContactRequest, route_contact


def main() -> None:
    raw = json.load(sys.stdin)
    request = ContactRequest(
        name=raw["name"], email=raw["email"], kind=ContactKind(raw["kind"]),
        message=raw.get("message", ""), amount_cents=raw.get("amount_cents"),
    )
    delivery = route_contact(request, raw["team_inbox"])
    print(json.dumps({"kind": delivery.kind.value, "subject": delivery.subject, "message_id": delivery.message_id}))


if __name__ == "__main__":
    main()

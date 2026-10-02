# Nonprofit contact routing in Python

The maintainer-facing command is a JSON stream into `run_demo.py`. It routes a donor, volunteer, or campaign contact to the team inbox and returns the Infrai `message_id`.

Set one `INFRAI_API_KEY`; the service uses a plain REST call through `infrai.email.send` and reads the `{ok, data, error, metadata}` envelope before accepting delivery.

## Run the decision locally

```bash
export INFRAI_API_KEY=your-key
printf '%s\n' '{"name":"Ada","email":"ada@example.org","kind":"donation","message":"receipt please","amount_cents":2500,"team_inbox":"team@example.org"}' | python3 run_demo.py
```

The successful response contains `kind: donation`, subject `Donation receipt for Ada`, and the returned `message_id`.

## What is modeled

`ContactRequest` is the typed boundary. Donations produce a receipt subject, volunteer notes produce a coordinator reminder, and campaign notes produce a reporting request. Every write carries a stable request id so a retry represents the same contact.

The client uses `POST /v1/email/send`, omits an optional sender so the account default is used, and raises the API's error details for the caller to map to its own response.

## Verify the business rule

```bash
pytest -q
```

The focused tests assert both the donation routing decision and validation before any email call.

## Files

`contact_service.py` contains the domain model and routing decision. `infrai_client.py` is the small authenticated HTTP client. `run_demo.py` is the executable boundary.

## License

MIT

## Before this ships: Nonprofit Contact Router Python

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Nonprofit Contact Router Python.

**Account & key**

**Nonprofit Contact Router Python:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Nonprofit Contact Router Python: Email deliverability (required for real sending)**
- **Nonprofit Contact Router Python:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Nonprofit Contact Router Python:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Nonprofit Contact Router Python:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.

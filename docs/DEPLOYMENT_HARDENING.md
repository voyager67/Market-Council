# Deployment and security hardening

## Local development

Use a dedicated virtual environment, install `.[dev,api]`, provision users locally, and run the API on loopback. Keep provider keys outside source control.

## Container deployment

A non-root container image and a loopback-bound Docker Compose example are provided. Persistent SQLite data belongs in `/data`. Keep the application port private and terminate TLS at a separate reverse proxy. Configure the exact hostnames in `MC_ALLOWED_HOSTS`.

```bash
cp deploy/production.env.example deploy/production.env
# Edit the values using a secure secret manager; do not commit the resulting file.
docker compose -f deploy/docker-compose.yml --env-file deploy/production.env up --build -d
```

The compose sample is a single-node convenience deployment, not a hardened production reference architecture. It has no built-in WAF, rate limiting, automated backup, failover, external secrets manager, SIEM, or certificate lifecycle management. The example Nginx config shows the intended TLS and rate-limiting boundary; adapt and independently review it before deployment.

## Minimum production controls

1. TLS from browser/client to a trusted reverse proxy; prevent plaintext external access to port 8000.
2. Restrict network ingress and `MC_ALLOWED_HOSTS`; do not use wildcard allowed hosts.
3. Rate-limit authentication and registration, and disable self-registration unless controlled.
4. Store provider and testnet credentials in a secret manager; use least-privilege keys and IP allowlists where supported.
5. Back up SQLite using a consistent online backup procedure; encrypt backups and test restores.
6. Monitor authentication failures, session issuance/revocation, provider errors, storage capacity, and abnormal order volume.
7. Apply dependency updates and scan the locked deployment image; pin image digests for controlled environments.
8. Conduct independent threat modelling, penetration testing, privacy/data-retention assessment, and jurisdiction-specific financial regulatory review.
9. Keep the live-money execution boundary disabled until a separate approval process, suitability controls, risk controls, reconciliation and incident runbooks have been reviewed by qualified operators.

## Controls already in code

- Passwords use scrypt; raw bearer tokens are not stored.
- API self-registration is off by default.
- API binding defaults to loopback and the CLI requires an explicit environment acknowledgement for a non-loopback bind.
- Trusted-host middleware and security response headers are enabled.
- SQL statements use parameters; account access is filtered by user ID.
- Audit events are append-only within SQLite triggers.
- Paper orders are idempotent by user/client-order ID and cannot short-sell or overspend cash.
- Testnet execution is pinned to `testnet.binance.vision`; no mainnet adapter exists.
- Market-data URLs use a fixed HTTPS host allowlist and bounded response size/timeouts.

These safeguards reduce common risks but do not amount to a full security certification.

# OSCAR Signup Portal

A nostalgic 90s-AIM-themed self-serve signup page for
[open-oscar-server](https://github.com/mk6i/open-oscar-server) — the
self-hostable AIM/ICQ (OSCAR protocol) server. Lets people create their own
screen name without an admin provisioning each account by hand, and ships
with a plain-language install guide for getting the actual AIM client
running on modern macOS and Windows.

![Sign-up page and install guide screenshots would go here]()

## What it does

- `/` — a screen-name + password signup form, styled like a classic AIM
  "sign-on" window
- Validates screen names (3–16 chars, starts with a letter, letters/numbers/
  spaces only) and rejects duplicates by checking the live user list
- `/guide` — a permanent install walkthrough covering macOS, Windows, and
  explaining why there's no web or mobile option (AIM speaks OSCAR, not HTTP)
- Talks to open-oscar-server's Management API over your internal Docker
  network only — the signup container never touches the Management API port
  directly from the outside, so the public-facing site has no path to raw
  user administration

## Prerequisites

- A running [open-oscar-server](https://github.com/mk6i/open-oscar-server)
  instance (it has no official prebuilt image — you build it from source
  per its own README) with `DISABLE_AUTH=false` and its Management API
  reachable from this container's network, but **not** published to the
  public internet
- Docker + Docker Compose

## Quick start

If open-oscar-server is already running as a compose service named
`open-oscar-server` in some project, add this service to that same
`docker-compose.yaml`:

```yaml
  signup:
    image: ryaneford/oscar-signup-portal:latest
    container_name: oscar-signup-portal
    restart: unless-stopped
    ports:
      - "8091:8080"
    environment:
      - OSCAR_API_URL=http://open-oscar-server:8080
      - OSCAR_HOST=aim.yourdomain.com
      - OSCAR_PORT=5190
      - NETWORK_NAME=Your Network Name
    depends_on:
      - open-oscar-server
```

Then:

```bash
docker compose up -d signup
```

Or run it standalone with the included [`compose.yaml`](compose.yaml):

```bash
git clone https://github.com/ryaneford/oscar-signup-portal.git
cd oscar-signup-portal
OSCAR_API_URL=http://<your-oscar-host>:8080 \
OSCAR_HOST=aim.yourdomain.com \
OSCAR_PORT=5190 \
NETWORK_NAME="Your Network Name" \
docker compose up -d
```

Open `http://localhost:8091`.

Finally, put a reverse proxy (nginx, Caddy, NGINX Proxy Manager, etc.) in
front of port 8091 for your public domain/HTTPS.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OSCAR_API_URL` | `http://open-oscar-server:8080` | Internal URL of open-oscar-server's Management API. Keep this off the public internet — only this container should reach it. |
| `OSCAR_HOST` | `aim.example.com` | The public hostname shown to users for their AIM client's "Host" field, and used throughout the install guide. |
| `OSCAR_PORT` | `5190` | The public OSCAR port shown to users (plain, non-SSL). |
| `NETWORK_NAME` | `AIM Network` | Display name used in the sign-up page marquee and guide header. |

## Security notes

- open-oscar-server's Management API (used to create/list users) has no
  authentication of its own — it must **never** be published on a public
  port. Bind it to `127.0.0.1` on the host, or keep it internal-only on the
  Docker network, and let only this signup container reach it.
- The signup portal itself does no privileged operations beyond creating a
  user — it can't delete accounts, read passwords, or otherwise administer
  the server.

## License

MIT

## Credits

Built as a companion app for
[mk6i/open-oscar-server](https://github.com/mk6i/open-oscar-server). Not
affiliated with or endorsed by AOL.

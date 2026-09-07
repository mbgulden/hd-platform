# HDE Staging Operations Notes

## Multi-turn birth-place chart recovery

Family/beta testers often provide birth details across several Telegram turns: date/time first, then a short city/state reply such as `Provo, UT`. The guest runtime must not let that final location-only turn fall through to the LLM, because the LLM can describe a chart without creating the PDF/bodygraph artifacts the router needs to upload.

Operational rule:

- If a short city/state reply arrives and recent user turns include birth/chart context with date and time, recover the recent birth details, treat the current location as authoritative, and run deterministic chart/PDF generation.
- Provo, Utah is explicitly mapped to `America/Denver` coordinates in the guest chart tool so it does not become `UTC` or `0,0`.
- Report/PDF access is verified from inside newly provisioned guest containers by calling the host report service at `host.docker.internal:8081/api/compute` with the container-provisioned `HDE_API_KEY`.
- New bot provisioning must `chown` both the user workspace and the per-container base directory to UID/GID `1000:1000`; files from that base directory are bind-mounted into `/home/pn/.hermes`, and `active_soul.md` must remain writable after chart/PDF generation.

This protects new HDE bots provisioned from `scripts/guest_hermes_template/guest_agent_server.py` and the live guest template copied to `/home/ubuntu/guest_hermes_bot/guest_agent_server.py`.

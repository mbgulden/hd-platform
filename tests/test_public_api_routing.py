from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_fastapi_diagnostics_are_fail_closed_and_public_health_stays_open():
    policy = read("api/routes/access_policy.py")
    main = read("api/main.py")

    assert '"GET /api/health"' in policy
    assert '"POST /api/checkout/create-session"' in policy
    assert '"GET /api/checkout/session"' in policy
    assert '"GET /api/diagnostics/routes"' in policy
    assert '"GET /api/reports"' in policy
    assert "HTTP_503_SERVICE_UNAVAILABLE" in policy
    assert "HTTP_403_FORBIDDEN" in policy
    assert "CF-Access-Client-Id" in policy
    assert "CF-Access-Client-Secret" in policy
    assert "HDE_DIAGNOSTIC_TOKEN" in policy
    assert "app.include_router(access_policy_router)" in main


def test_payment_server_keeps_checkout_aliases_public():
    payment_server = read("payment/server.py")

    assert "'/api/checkout/create-session'" in payment_server
    assert "'/api/checkout/session'" in payment_server
    assert "'/api/webhooks/stripe'" in payment_server


def test_reports_server_keeps_public_report_delivery_routes_open():
    reports_server = read("reports/server.py")

    assert "elif path.startswith('/api/reports/download/'):" in reports_server
    assert "elif path == '/api/public/compute-chart':" in reports_server
    assert "elif path == '/api/public/capture-lead':" in reports_server

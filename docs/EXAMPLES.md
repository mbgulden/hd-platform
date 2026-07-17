# HD Platform API — Code Examples

Quick copy-paste snippets for the most common integrations. See `API.md` for full reference.

**Base URL:** `https://api.humandesignengine.com`
**Auth header:** `X-API-Key: hd_<your-key>`

---

## JavaScript / Node.js (fetch)

```javascript
const API = "https://api.humandesignengine.com";
const KEY = process.env.HD_API_KEY; // hd_...

async function getNatalChart(birth) {
  const r = await fetch(`${API}/v1/natal`, {
    method: "POST",
    headers: { "X-API-Key": KEY, "Content-Type": "application/json" },
    body: JSON.stringify(birth),
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}: ${await r.text()}`);
  const { data } = await r.json();
  return data;
}

const chart = await getNatalChart({
  name: "Jane Doe",
  year: 1990, month: 6, day: 15,
  hour: 14, minute: 30,
  lat: 21.3099, lon: -157.8581,
  timezone: "Pacific/Honolulu",
});
console.log(chart.type, chart.profile);
```

## JavaScript — bodygraph SVG render

```javascript
function renderBodygraph(data) {
  const svg = `<svg viewBox="0 0 440 540">
    ${data.centers.map(c => `
      <circle cx="${c.x}" cy="${c.y}" r="32"
        fill="${c.defined ? '#fff' : '#222'}"
        stroke="#888" stroke-width="2"/>
      <text x="${c.x}" y="${c.y+5}" text-anchor="middle"
        font-size="11" fill="${c.defined ? '#000' : '#888'}">
        ${c.id}
      </text>`).join('')}
    ${data.channels.map(ch => {
      const a = data.centers.find(c => c.id === ch.from);
      const b = data.centers.find(c => c.id === ch.to);
      return `<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}"
        stroke="${ch.active ? '#ff8800' : '#444'}" stroke-width="3"/>`;
    }).join('')}
  </svg>`;
  return svg;
}
```

## Python (requests)

```python
import os, requests

API = "https://api.humandesignengine.com"
H = {"X-API-Key": os.environ["HD_API_KEY"]}

def natal(birth):
    r = requests.post(f"{API}/v1/natal", json=birth, headers=H, timeout=10)
    r.raise_for_status()
    return r.json()["data"]

def transits(birth, target_date=None):
    body = {**birth, "target_date": target_date} if target_date else birth
    r = requests.post(f"{API}/v1/transits", json=body, headers=H, timeout=10)
    r.raise_for_status()
    return r.json()["data"]

def synastry(person_a, person_b):
    r = requests.post(f"{API}/v1/synastry",
                      json={"person_a": person_a, "person_b": person_b},
                      headers=H, timeout=10)
    r.raise_for_status()
    return r.json()["data"]

def bodygraph(birth, auth=True):
    path = "/v1/bodygraph" if auth else "/v1/bodygraph/noauth"
    headers = H if auth else {"Content-Type": "application/json"}
    r = requests.post(f"{API}{path}", json=birth, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()["data"]

birth = {
    "name": "Jane Doe",
    "year": 1990, "month": 6, "day": 15,
    "hour": 14, "minute": 30,
    "lat": 21.3099, "lon": -157.8581,
    "timezone": "Pacific/Honolulu",
}

chart = natal(birth)
print(f"{chart['type']} {chart['profile']}")
```

## Ruby

```ruby
require 'net/http'
require 'json'
require 'uri'

API = "https://api.humandesignengine.com"
KEY = ENV['HD_API_KEY']

def post(path, body, auth: true)
  uri = URI("#{API}#{path}")
  req = Net::HTTP::Post.new(uri, 'Content-Type' => 'application/json')
  req['X-API-Key'] = KEY if auth
  req.body = body.to_json
  res = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) { |http| http.request(req) }
  raise "HTTP #{res.code}" unless res.is_a?(Net::HTTPSuccess)
  JSON.parse(res.body).dig('data')
end

birth = { name: "Jane Doe", year: 1990, month: 6, day: 15,
          hour: 14, minute: 30, lat: 21.3099, lon: -157.8581,
          timezone: "Pacific/Honolulu" }

chart = post('/v1/natal', birth)
puts "#{chart['type']} #{chart['profile']}"
```

## PHP

```php
<?php
$api = "https://api.humandesignengine.com";
$key = getenv("HD_API_KEY");

function hd_post($path, $body, $key) {
    $ch = curl_init("https://api.humandesignengine.com$path");
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_HTTPHEADER => [
            "X-API-Key: $key",
            "Content-Type: application/json",
        ],
        CURLOPT_POSTFIELDS => json_encode($body),
    ]);
    $resp = curl_exec($ch);
    if (curl_errno($ch)) throw new Exception(curl_error($ch));
    curl_close($ch);
    $j = json_decode($resp, true);
    if (!($j['success'] ?? false)) throw new Exception($j['error'] ?? 'unknown');
    return $j['data'];
}

$birth = [
    "name" => "Jane Doe", "year" => 1990, "month" => 6, "day" => 15,
    "hour" => 14, "minute" => 30,
    "lat" => 21.3099, "lon" => -157.8581,
    "timezone" => "Pacific/Honolulu",
];
$chart = hd_post("/v1/natal", $birth, $key);
echo "{$chart['type']} {$chart['profile']}\n";
```

## cURL

```bash
API=https://api.humandesignengine.com
KEY=hd_YOUR_KEY_HERE

# Natal
curl -sX POST $API/v1/natal \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"name":"Jane Doe","year":1990,"month":6,"day":15,"hour":14,"minute":30,"lat":21.3099,"lon":-157.8581,"timezone":"Pacific/Honolulu"}' \
  | jq .data

# Transits
curl -sX POST $API/v1/transits \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"name":"Jane Doe","year":1990,"month":6,"day":15,"hour":14,"minute":30,"lat":21.3099,"lon":-157.8581,"timezone":"Pacific/Honolulu","target_date":"2026-06-20"}' \
  | jq .data.transits

# Bodygraph (no auth, rate-limited 3/day per IP)
curl -sX POST $API/v1/bodygraph/noauth \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Doe","year":1990,"month":6,"day":15,"hour":14,"minute":30,"lat":21.3099,"lon":-157.8581,"timezone":"Pacific/Honolulu"}' \
  | jq .data
```

## Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
    "os"
)

type Birth struct {
    Name     string  `json:"name"`
    Year     int     `json:"year"`
    Month    int     `json:"month"`
    Day      int     `json:"day"`
    Hour     int     `json:"hour"`
    Minute   int     `json:"minute"`
    Lat      float64 `json:"lat"`
    Lon      float64 `json:"lon"`
    Timezone string  `json:"timezone"`
}

type NatalData struct {
    Type    string `json:"type"`
    Profile string `json:"profile"`
}

type Resp struct {
    Success bool      `json:"success"`
    Data    NatalData `json:"data"`
    Error   *string   `json:"error"`
}

func main() {
    api := "https://api.humandesignengine.com/v1/natal"
    body, _ := json.Marshal(Birth{
        Name: "Jane Doe", Year: 1990, Month: 6, Day: 15,
        Hour: 14, Minute: 30, Lat: 21.3099, Lon: -157.8581,
        Timezone: "Pacific/Honolulu",
    })
    req, _ := http.NewRequest("POST", api, bytes.NewReader(body))
    req.Header.Set("X-API-Key", os.Getenv("HD_API_KEY"))
    req.Header.Set("Content-Type", "application/json")

    r, err := http.DefaultClient.Do(req)
    if err != nil { panic(err) }
    defer r.Body.Close()

    var resp Resp
    json.NewDecoder(r.Body).Decode(&resp)
    if !resp.Success { panic(*resp.Error) }
    fmt.Println(resp.Data.Type, resp.Data.Profile)
}
```

---

## Error handling pattern

Every integration should handle these cases:

```javascript
async function hdCall(path, body, key) {
  const r = await fetch(`${API}${path}`, {
    method: "POST",
    headers: key ? { "X-API-Key": key, "Content-Type": "application/json" } : { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const j = await r.json();

  if (r.status === 429) {
    // Rate-limited — back off and retry
    const retryAfter = parseInt(r.headers.get("Retry-After") || "60");
    await new Promise(r => setTimeout(r, retryAfter * 1000));
    return hdCall(path, body, key);
  }

  if (!j.success) {
    throw new Error(`[${r.status}] ${j.error}`);
  }

  return j.data;
}
```

## Webhook handler example (your server)

If you're processing Stripe webhooks on your own backend:

```python
@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Bad signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # Trigger HD Platform to generate report
        requests.post("https://api.humandesignengine.com/v1/payment/webhook",
                      json={"session_id": session["id"]},
                      headers={"Stripe-Signature": sig})
        # Then email the buyer
        send_report_email(session["customer_details"]["email"])

    return {"received": True}
```

---

## Rate-limit aware client (Python)

```python
import time
import requests
from functools import wraps

class HDClient:
    def __init__(self, api_key, base="https://api.humandesignengine.com"):
        self.base = base
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        })

    def post(self, path, body, retries=3):
        for attempt in range(retries):
            r = self.session.post(f"{self.base}{path}", json=body, timeout=10)
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 60))
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()["data"]
        raise RuntimeError(f"Rate-limited after {retries} retries on {path}")

    def natal(self, birth): return self.post("/v1/natal", birth)
    def transits(self, birth, date=None):
        return self.post("/v1/transits", {**birth, "target_date": date} if date else birth)
    def synastry(self, a, b): return self.post("/v1/synastry", {"person_a": a, "person_b": b})
    def bodygraph(self, birth): return self.post("/v1/bodygraph", birth)
```

---

See `API.md` for full endpoint reference, field validation, response schemas, and webhook payloads.

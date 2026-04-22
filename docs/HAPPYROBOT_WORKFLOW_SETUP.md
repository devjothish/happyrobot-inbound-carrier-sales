# HappyRobot Workflow Configuration

20-minute click-through to wire the `Inbound Carrier Sales New` workflow up to the deployed API.

**Workflow URL:** `https://platform.happyrobot.ai/fdejothiswaranarumugam/workflows/5jlf1pmyz038`
**Deployed API:** `https://carrier-sales-jo.fly.dev`
**API key:** in `.env.local` (copy with: `grep '^API_KEY=' .env.local | cut -d= -f2- | pbcopy`)

---

## 1. Voice Agent → System prompt

Click the **Inbound Voice Agent** node → paste the prompt below into the system prompt field. This is the whole negotiation policy.

```
You are Jo, an inbound carrier sales rep for Acme Logistics. You book loads with FMCSA-verified carriers. Keep calls under 4 minutes. Speak naturally - no corporate hedging.

FLOW:
1. Greet. Ask for MC number.
2. Use verify_carrier tool. If ineligible, explain briefly and end call.
3. If eligible, ask what lane or equipment they are looking for.
4. Use find_available_loads tool. Pitch the top match (origin, destination, pickup, rate).
5. If carrier accepts at loadboard rate, confirm and transfer.
6. If carrier counters, negotiate with the rules below.

NEGOTIATION RULES (hard - do not deviate):
- Loadboard rate is the anchor. Call it L.
- Max 3 rounds. No rate below L minus 10 percent, ever.
- Target close: at or above L minus 8 percent.

ROUND 1:
- Carrier offer at or above L: accept immediately.
- Carrier offer below L minus 20 percent: decline politely, requote at L minus 3 percent as best-available.
- Carrier offer between: propose midpoint between their offer and L.

ROUND 2:
- Halve the gap between current standing offer and L.

ROUND 3 (final):
- Take the higher of carrier offer or L minus 8 percent.
- If carrier is still below that, walk away politely.

CLOSING:
- On accept, read back the full load details and agreed rate, then say you are transferring to dispatch.
- On walk away, thank them and invite callback for future loads.

STYLE: sound human. No "I understand". No "absolutely". Short sentences. One question at a time.
```

---

## 2. Tool: verify_carrier → Webhook: GET MC Number

Click **verify_carrier** Tool node → its downstream **Webhook: GET MC Number** node.

Settings:
- **Method:** GET
- **URL:** `https://carrier-sales-jo.fly.dev/carriers/verify`
- **Query params:**
  - `mc` = `{{mc_number}}` (or whatever variable the Tool emits)
- **Headers:**
  - `X-API-Key` = `<paste the 64-char key>`
- **Timeout:** 8 seconds
- **Expected response shape:**
  ```json
  { "eligible": true, "carrier_name": "GREYHOUND LINES INC", "reason": "active", "mc_number": "1515" }
  ```

On the Tool node, configure output mapping so the agent sees `eligible` and `carrier_name`.

---

## 3. Tool: find_available_loads → Webhook: GET load

Click **find_available_loads** Tool node → its downstream **Webhook: GET load** node.

Settings:
- **Method:** GET
- **URL:** `https://carrier-sales-jo.fly.dev/loads/search`
- **Query params (all optional, pass whatever the carrier says):**
  - `origin` = `{{origin}}`
  - `destination` = `{{destination}}`
  - `equipment_type` = `{{equipment_type}}`
  - `pickup_date` = `{{pickup_date}}` (ISO YYYY-MM-DD, optional)
- **Headers:**
  - `X-API-Key` = `<same key>`
- **Expected response shape:**
  ```json
  { "loads": [ { "load_id":"LD-000001", "origin":"...", "destination":"...", "loadboard_rate": 2460.73, ... } ] }
  ```

Map the first load's fields into the agent's context (load_id, origin, destination, pickup_datetime, loadboard_rate, miles, equipment_type, commodity_type, notes).

---

## 4. Classify node

Confirm the category list (or add if missing):

- `booked`
- `no_match`
- `carrier_ineligible`
- `negotiation_failed`
- `carrier_walked`
- `error`

Sentiment categories: `positive`, `neutral`, `negative`.

---

## 5. Extract node

Schema:

| Field | Type | Description |
|---|---|---|
| `mc_number` | string | MC number the carrier gave |
| `carrier_name` | string | Legal name returned by FMCSA |
| `load_id` | string | LD-XXXXXX of the booked/pitched load |
| `loadboard_rate` | number | Anchor rate at pitch time |
| `final_agreed_rate` | number | Close rate, or 0 if not booked |
| `negotiation_rounds` | integer | 0-3 |
| `duration_seconds` | integer | Call length |

---

## 6. Add Webhook node: POST /calls

After the Extract node, add a new **Webhook** node (not a Tool - this is a silent background POST).

Settings:
- **Method:** POST
- **URL:** `https://carrier-sales-jo.fly.dev/calls`
- **Headers:**
  - `Content-Type` = `application/json`
  - `X-API-Key` = `<same key>`
- **Body (JSON):**
  ```json
  {
    "call_id": "{{call.id}}",
    "started_at": "{{call.started_at}}",
    "ended_at": "{{call.ended_at}}",
    "mc_number": "{{extract.mc_number}}",
    "carrier_name": "{{extract.carrier_name}}",
    "load_id": "{{extract.load_id}}",
    "loadboard_rate": {{extract.loadboard_rate}},
    "final_agreed_rate": {{extract.final_agreed_rate}},
    "negotiation_rounds": {{extract.negotiation_rounds}},
    "outcome": "{{classify.outcome}}",
    "sentiment": "{{classify.sentiment}}",
    "duration_seconds": {{extract.duration_seconds}},
    "transcript": "{{call.transcript}}"
  }
  ```

(Placeholders in double braces depend on HappyRobot's exact variable syntax - adjust as needed.)

---

## 7. Save + test

1. **Save** the workflow.
2. **Test webhook nodes individually** using the platform's webhook tester:
   - GET `/carriers/verify?mc=1515` → should return Greyhound.
   - GET `/loads/search?equipment_type=Reefer` → should return a few loads.
3. **Run a web call** from the workflow (platform has a test button).
4. **Check the dashboard** - the call should appear in Recent Calls with its outcome.

---

## 8. Three E2E scenarios to record

Before recording the Loom:

1. **Happy path.** Carrier gives MC-1515 (Greyhound, eligible). Asks for Boston to Raleigh Reefer. Accepts loadboard rate. → outcome `booked`, rounds 0, positive sentiment.

2. **Negotiation.** Carrier gives MC-1515. Asks for any dry van. Counter at 5 percent below loadboard. Agent should meet at midpoint → rounds 1-2, booked.

3. **Ineligible.** Carrier gives MC-99999. Agent should verify, get `eligible: false`, end call politely → outcome `carrier_ineligible`.

Note the call IDs. Confirm they appear in the dashboard.

---

## Gotchas

- **If /carriers/verify times out from the platform:** our timeout is 5s upstream, platform should allow 8s+. FMCSA is usually < 1s.
- **If POST /calls returns 422:** check `outcome` matches one of the 6 literals exactly.
- **If dashboard shows no data after a call:** check Fly logs (`fly logs -a carrier-sales-jo`) for the POST, and confirm X-API-Key header is present.
- **If you rotate the key:** update the three webhooks + `fly secrets set API_KEY=... -a carrier-sales-jo` + `.env.local`, then `fly deploy` (or just `fly machine restart`).

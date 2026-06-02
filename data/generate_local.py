"""Generate synthetic Lumera Books dataset (pure stdlib) -> CSV files.

Three raw source tables for the "Smart Upgrade" case study:
  - subscriptions.csv     (one row per business)
  - transactions.csv      (monthly financial snapshots per business)
  - telemetry_events.csv  (clickstream; intentionally dirty)

Seeded patterns: ~5% of all businesses are Mid-tier "power users" with
elevated invoice volume AND elevated friction errors (LIMIT_EXCEEDED /
FEATURE_LOCKED). Dirtiness in telemetry: ~1.5% exact duplicates, ~1% null
user_id, ~2% null/malformed device, naturally out-of-order timestamps.
"""
import csv, os, random
from datetime import date, datetime, timedelta

random.seed(42)

OUT = "/tmp/sds/out"
os.makedirs(OUT, exist_ok=True)

N_BUSINESSES = 10000
END = datetime(2026, 6, 3, 0, 0, 0)
TELEMETRY_DAYS = 180

NAME1 = ["Acme","Globex","Initech","Umbra","Nova","Vertex","Stellar","Quantum",
         "Cedar","Summit","Harbor","Pioneer","Apex","Bright","Iron","Cobalt"]
NAME2 = ["Labs","Trading","Logistics","Bakery","Studios","Consulting","Retail",
         "Foods","Builders","Health","Media","Auto","Supply","Group","Works","Partners"]
PAGES = ["dashboard","invoices","payroll","reports","expenses","settings","upgrade"]
EVT_NON_ERR = ["login","page_load","click","feature_use","logout"]
DEVICES = ["web-chrome","web-safari","web-firefox","mobile-ios","mobile-android"]
ERR_POWER = ["LIMIT_EXCEEDED","FEATURE_LOCKED","LIMIT_EXCEEDED","FEATURE_LOCKED","TIMEOUT"]
ERR_OTHER = ["TIMEOUT","VALIDATION","SERVER_500","VALIDATION","TIMEOUT"]

# ----------------------------------------------------------------------------
# 1. SUBSCRIPTIONS (master)
# ----------------------------------------------------------------------------
subs = []
for n in range(N_BUSINESSES):
    bid = f"BUS-{n:06d}"
    r = random.random()
    if r < 0.55:
        tier = "Free"
    elif r < 0.85:
        tier = "Mid"
    else:
        tier = "Premium"

    if tier == "Free":
        seats = 1 + random.randint(0, 2)
        mrr = 0.0
    elif tier == "Mid":
        seats = 3 + random.randint(0, 14)
        mrr = round(30 + random.random() * 70, 2)
    else:
        seats = 10 + random.randint(0, 89)
        mrr = round(150 + random.random() * 600, 2)

    age = random.randint(30, 1110)
    signup = END - timedelta(days=age)
    cycles = (age // 365) + 1
    renewal = signup + timedelta(days=cycles * 365)
    is_power = (tier == "Mid" and random.random() < 0.17)

    subs.append({
        "business_id": bid,
        "business_name": f"{random.choice(NAME1)} {random.choice(NAME2)}",
        "plan_tier": tier,
        "seats": seats,
        "mrr": mrr,
        "signup_date": signup.date().isoformat(),
        "renewal_date": renewal.date().isoformat(),
        "is_power_user_seed": is_power,
    })

with open(f"{OUT}/subscriptions.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(subs[0].keys()))
    w.writeheader()
    w.writerows(subs)
print(f"subscriptions: {len(subs)}")
n_power = sum(1 for s in subs if s["is_power_user_seed"])
print(f"  power users: {n_power} ({n_power/len(subs)*100:.1f}% of all)")

# ----------------------------------------------------------------------------
# 2. TRANSACTIONS (6 monthly snapshots per business)
# ----------------------------------------------------------------------------
months = [date(2026, 6, 1)]
for k in range(1, 6):
    m = 6 - k
    months.append(date(2026, m, 1))
months = sorted(months)

tx_rows = 0
with open(f"{OUT}/transactions.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["business_id", "txn_month", "invoice_count", "payroll_runs", "revenue"])
    for s in subs:
        tier = s["plan_tier"]
        seats = s["seats"]
        pw = s["is_power_user_seed"]
        base_inv = {"Premium": 80, "Mid": 25, "Free": 5}[tier]
        base_pay = {"Premium": 4, "Mid": 2, "Free": 0}[tier]
        base_rev = {"Premium": 50000, "Mid": 12000, "Free": 2000}[tier]
        for mo in months:
            inv = int(max(0, round(base_inv * (1 + seats / 50.0) *
                                   (2.5 if pw else 1.0) *
                                   (0.7 + random.random() * 0.6))))
            pay = int(round(base_pay * (0.5 + random.random())))
            rev = round(base_rev * (1 + seats / 40.0) *
                        (1.8 if pw else 1.0) *
                        (0.6 + random.random() * 0.8), 2)
            w.writerow([s["business_id"], mo.isoformat(), inv, pay, rev])
            tx_rows += 1
print(f"transactions: {tx_rows}")

# ----------------------------------------------------------------------------
# 3. TELEMETRY EVENTS (clickstream; dirty)
# ----------------------------------------------------------------------------
ev_rows = 0
dups = 0
with open(f"{OUT}/telemetry_events.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["event_id", "business_id", "user_id", "event_ts", "session_id",
                "event_type", "page", "error_code", "device"])
    for s in subs:
        tier = s["plan_tier"]
        seats = s["seats"]
        pw = s["is_power_user_seed"]
        base = {"Premium": 200, "Mid": 90, "Free": 30}[tier]
        n_events = int(max(5, round(base * (2.0 if pw else 1.0) * (0.5 + random.random()))))
        err_p = 0.18 if pw else 0.04
        for e in range(n_events):
            secs = random.randint(0, TELEMETRY_DAYS * 86400)
            ts = END - timedelta(seconds=secs)
            # user_id (~1% null)
            if random.random() < 0.01:
                uid = ""
            else:
                uid = f"{s['business_id']}-U{1 + random.randint(0, max(0, seats - 1))}"
            # event_type / error
            if random.random() < err_p:
                etype = "error"
                err = random.choice(ERR_POWER if pw else ERR_OTHER)
            else:
                etype = random.choice(EVT_NON_ERR)
                err = ""
            # device (~2% null, ~1% malformed)
            dr = random.random()
            if dr < 0.02:
                dev = ""
            elif dr < 0.03:
                dev = "unknown/??"
            else:
                dev = random.choice(DEVICES)
            sess = f"SESS-{s['business_id']}-{ts.strftime('%Y%m%d')}-{random.randint(0,5)}"
            row = [f"EVT-{s['business_id']}-{e:05d}", s["business_id"], uid,
                   ts.strftime("%Y-%m-%d %H:%M:%S"), sess, etype,
                   random.choice(PAGES), err, dev]
            w.writerow(row)
            ev_rows += 1
            # ~1.5% exact duplicate (same event_id) -> dedup exercise
            if random.random() < 0.015:
                w.writerow(row)
                ev_rows += 1
                dups += 1
print(f"telemetry_events: {ev_rows} (incl. {dups} duplicates)")
print("DONE")

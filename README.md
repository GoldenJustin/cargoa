# 🚚 Logistics Management — Frappe / ERPNext App

A complete **Hub‑and‑Spoke freight & logistics management** app for Frappe / ERPNext.

> **The Freight Trip is the Hub.** Waybills, Trip Expenses and Revenue are the spokes. Every shilling and every litre rolls up to the Freight Trip to give you a **real‑time Profit & Loss for each journey** — fully wired into the ERPNext accounting books.

Built for the realities of East‑African / Tanzanian trucking (fuel‑theft control, posho, weighbridge fines, toll gates, hired trucks & sub‑contract drivers), but currency‑agnostic and configurable for any company.

---

## 📑 Table of Contents
1. [What this app does](#-what-this-app-does)
2. [What was added beyond the original brief](#-what-was-added-beyond-the-original-brief)
3. [Architecture (Hub & Spoke)]#-architecture-hub--spoke)
4. [Installation](#-installation)
5. [First‑time setup](#-first-time-setup)
6. [Master data](#-master-data)
7. [Daily workflow (step by step)](#-daily-workflow-step-by-step)
8. [Cost roll‑up & real‑time P&L](#-cost-roll-up--real-time-pl)
9. [Anti‑theft & cost control](#-anti-theft--cost-control)
10. [💰 The Accounting / Money‑Flow chain](#-the-accounting--money-flow-chain)
11. [Trip Settlement — closing a journey](#-trip-settlement--closing-a-journey)
12. [Roles & permissions](#-roles--permissions)
13. [Reports & insights](#-reports--insights)
14. [Troubleshooting & FAQ](#-troubleshooting--faq)
15. [Extending the app](#-extending-the-app)

---

## 🎯 What this app does

| Business need | How the app handles it |
|---|---|
| Know if a journey made or lost money **while it's still on the road** | Freight Trip auto‑sums all Trip Expenses → live Profit & Margin |
| Stop fuel theft & inflated allowances | Freight Route benchmarks; trip flags excess litres & posho in red |
| Drivers can be staff **or** hired | `Driver` master supports *Own Employee* and *Hired Contractor* |
| Trucks can be owned **or** hired | `Transport Vehicle` master supports *Owned* and *Hired* (paid via Purchase Invoice) |
| Tie every trip to the books | One‑click creation of Sales Invoice, Purchase Invoice, Journal Entries, Payment Entries — all linked back to the trip |
| See the full Invoice→Payment chain on one screen | `Trip Settlement` reconciliation document |

---

## ✨ What was added beyond the original brief

Your spec defined 4 doctypes (Freight Route, Waybill, Trip Expense, Freight Trip). To make it a **full logistics business** and to wire in the money‑flow chain, the app adds:

1. **`Driver`** master — *Own Employee* (links to ERPNext **Employee**) or *Hired Contractor* (links to a **Supplier**), with license tracking.
2. **`Transport Vehicle`** master — *Owned* or *Hired* (links the owner as a **Supplier**); covers **both Prime Movers and Trailers**.
3. **`Logistics Settings`** — the bridge to your Chart of Accounts: maps every logistics concept (fuel, allowance, fines, truck hire, income, bank, payable) to a ledger account.
4. **`Trip Settlement`** — a reconciliation document that lays out the complete money‑flow chain and reconciles **accrual profit vs. actual cash**.
5. **Accounting automation** — a **Freight Trip** custom field is auto‑added to **Sales Invoice, Purchase Invoice, Journal Entry and Payment Entry** so every accounting voucher traces back to its journey.
6. **Two roles** — `Logistics Manager` and `Logistics User`.
7. **A `Logistics` workspace** for one‑click access.

---

## 🏗 Architecture (Hub & Spoke)

```
                         ┌───────────────────────────────────────────────┐
                         │                FREIGHT  TRIP  (HUB)            │
                         │  Route • Vehicle(s) • Driver • Waybill         │
                         │  ┌────────────┬─────────────┬───────────────┐  │
   ┌──────────────┐      │  │  REVENUE   │    COSTS    │ PROFITABILITY │  │      ┌──────────────┐
   │   WAYBILL    │─────▶│  │ (Customer  │ (rolled up  │  Profit &     │  │─────▶│  SALES INV   │
   │ cargo/weight │      │  │  rate×wt)  │  from       │  Margin %     │  │      │  → Payment   │
   └──────────────┘      │  │            │  expenses)  │  (live)       │  │      └──────────────┘
                         │  └────────────┴─────────────┴───────────────┘  │
                         └───────────────────────────────────────────────┘
                                          ▲                            ▲
                  ┌───────────────────────┘                            │
                  │                                                    │
          ┌──────────────┐                                    ┌──────────────────┐
          │ TRIP EXPENSE │  (Fuel, Posho, Fines, Tolls, …)     │ HIRED TRUCK/DRIVER│
          │   → Journal  │                                    │ → Purchase Inv /  │
          │     Entry    │                                    │   Payment Entry   │
          └──────────────┘                                    └──────────────────┘
```

All spokes feed the Hub. The Hub feeds the accounting chain.

---

## 📦 Installation

**Requirements:** a working `bench` with Frappe v14/v15 and ERPNext installed.

```bash
# 1. Put the app folder inside your bench's apps directory
cd ~/frappe-bench/apps
# (copy/clone the 'logistics_management' folder here)

# 2. Install the python package
bench pip install -e apps/logistics_management

# 3. Install the app on your site
bench --site <your-site> install-app logistics_management

# 4. Migrate (syncs doctypes, custom fields, workspace)
bench --site <your-site> migrate
```

On install the app automatically:
- creates the **Logistics Manager** and **Logistics User** roles,
- grants them access to every Logistics doctype,
- adds the **Freight Trip** link field to Sales/Purchase Invoice, Journal & Payment Entry,
- creates a **Logistics Settings** record seeded with your company's default accounts,
- creates two service **Items**: *Freight Charges* and *Truck Hire*.

---

## ⚙️ First‑time setup

Open **Logistics → Logistics Settings** and confirm the mappings to your Chart of Accounts (these drive all the auto‑posting):

| Section | Field | What it controls |
|---|---|---|
| Defaults | Default Company, Default Cost Center | Where trips & vouchers are posted |
| Accounting Defaults | Freight Income Item & Account | The line on the **Sales Invoice** |
| | Truck Hire Item | The line on the **Purchase Invoice** to a truck owner |
| Expense Accounts | Fuel / Driver Allowance / Fines & Tolls / Repairs / Loading‑Offloading / Truck Hire / Other | Which ledger each **Trip Expense** category is debited to |
| Payment Accounts | Payable / Bank / Cash | Credit side of Journal Entries & source of Payment Entries |
| Controls | Auto‑submit accounting, Warn on negative margin, Allow zero‑revenue trips | Behaviour toggles |

> Tip: the installer pre‑fills these from your Company's defaults. Just review and adjust.

---

## 🗂 Master data

### 1) Freight Route (benchmark)
*Examples: `Dar es Salaam - Mwanza`, `Dar - Kigoma`, `Mlandizi - Dodoma`.*

- **Total Distance (km)**, **Trip Type** (One‑Way / Round Trip)
- **Standard Fuel Allocation (L)** — the benchmark. Trips drawing more than this are flagged for **fuel theft / excess**.
- **Standard Driver Allowance** — expected posho. Trips claiming more are flagged.
- **Estimated Duration (Hours)**.

### 2) Driver (Own Employee *or* Hired Contractor)
| Type | What to fill | How they get paid |
|---|---|---|
| **Own Employee** | Linked **Employee** | Through ERPNext **Payroll / Salary Slip** |
| **Hired Contractor** | Linked **Supplier** (the driver/crew) | Through **Payment Entry** (one click from the trip) |

Also tracks phone, NIDA, license number/class/expiry (warns when expired).

### 3) Transport Vehicle (Owned *or* Hired; Prime Mover *or* Trailer)
| Type | What to fill | Cost handling |
|---|---|---|
| **Owned** | — | Only running costs (fuel, service) |
| **Hired** | Owner as **Supplier** | Set **Agreed Truck Hire Rate** on the trip → a **Purchase Invoice** is raised to the owner |

Set **Vehicle Type** = *Prime Mover* for tractors and *Trailer* for trailers — both link into the Freight Trip.

### Standard ERPNext masters you will also use
**Customer** (who you haul for), **Supplier** (fuel stations, garages, truck owners, hired drivers), **Employee** (own drivers), **Item**, **UOM**, **Cost Center**.

---

## 🛣 Daily workflow (step by step)

> **Worked example:** Hauling **30 Tons of cement** for **Twiga Cement** on the **Dar es Salaam → Mwanza** route, using a **hired Scania** owned by *Mzee Trans Ltd*, driven by hired contractor *Juma*.

### Step 1 — Create the Waybill (proof of cargo)
**Logistics → Waybill → Add Waybill**
- Customer: *Twiga Cement*
- Cargo: *Cement*, Weight: **30**, UOM: *Ton*
- Loading Point: *Dar es Salaam*, Offloading Point: *Mwanza*
- Status: *Loaded*
- Save → **Submit** (it becomes the consignment note; upload the stamped POD when delivered).

### Step 2 — Create the Freight Trip (the Hub)
**Logistics → Freight Trip → Add Freight Trip**
- Company, Trip Date, Cost Center
- Route: **Dar es Salaam - Mwanza** *(Distance, Expected Fuel & Standard Allowance auto‑fill)*
- Prime Mover: *the Scania* *(Truck Ownership auto‑shows "Hired")*
- Trailer: *the trailer*
- Driver: *Juma* *(Driver Type auto‑shows "Hired Contractor")*
- Waybill: *the waybill from Step 1* *(Customer, Cargo & Weight auto‑fill)*
- Agreed Rate per Ton: e.g. **TZS 120,000**

➡️ **Total Revenue auto‑calculates = 30 × 120,000 = TZS 3,600,000.**

### Step 3 — Log costs as they happen (Trip Expenses)
**Logistics → Trip Expense → Add Trip Expense** — one row per spend:

| Expense | Category | Qty (L) | Amount | Paid By | Supplier |
|---|---|---|---|---|---|
| Diesel at Morogoro | Fuel | 250 | 1,000,000 | Company | PUMA Energy |
| Driver food | Driver Allowance (Posho) | – | 150,000 | Driver Pocket | – |
| Mikumi weighbridge | Weighbridge Fine | – | 30,000 | Company | – |
| Tanga toll gate | Toll Gate | – | 5,000 | Driver Pocket | – |
| Burst tyre repair | En-route Repair | – | 220,000 | Company | TyrePro Garage |

On **Submit**, each *Company‑paid* expense **auto‑creates a Journal Entry** (debits the category's expense account, credits Payable/Bank), and the **Freight Trip's cost & profit figures refresh instantly**.

### Step 4 — Submit the Freight Trip
Review the live P&L, then **Submit**. Status becomes **Completed**. The **Create ▾** button now offers the accounting actions.

### Step 5 — Run the accounting chain (see next section)
Use the **Create** menu on the submitted trip to bill the customer, pay the truck owner, and pay the driver.

### Step 6 — Close out with a Trip Settlement
Reconcile cash received vs. cash paid (see [Trip Settlement](#-trip-settlement--closing-a-journey)).

---

## 🧮 Cost roll‑up & real‑time P&L

The Freight Trip groups every **submitted** Trip Expense by category into read‑only buckets:

| Category entered | Rolls into trip field |
|---|---|
| Fuel | Total Fuel Cost (+ actual litres) |
| Driver Allowance (Posho) | Total Allowances |
| Weighbridge Fine, Toll Gate | Total Fines & Tolls |
| En‑route Repair | Total En‑route Repairs |
| Offloading Fee, Loading Fee | Total Loading / Offloading |
| Truck Hire | Total Truck Hire |
| Other | Total Other |

Then:
```
Total Trip Cost   = sum of all buckets
Trip Profit       = Total Revenue − Total Trip Cost
Profit Margin %   = Trip Profit ÷ Total Revenue × 100
Fuel Variance (L) = Actual Fuel Drawn − Standard Fuel Allocation
```
These recalculate **every time** a Trip Expense is submitted or cancelled — even after the trip itself is already submitted — so your P&L is always live.

---

## 🛡 Anti‑theft & cost control

When you save a Freight Trip, the app warns you in **orange/red** if:
- ⛽ **Fuel drawn exceeds the route's standard allocation** (possible theft/siphoning),
- 💵 **Driver allowances exceed the route's standard posho**,
- 📉 **The trip has a negative profit margin**.

Set realistic benchmarks on each **Freight Route** and these become automatic trip‑audits.

---

## 💰 The Accounting / Money‑Flow chain

This is the heart of the integration. Everything below is created with **one click** from the submitted Freight Trip's **Create ▾** menu, and **every voucher is stamped with the Freight Trip** so you can trace money end‑to‑end.

```
                                    MONEY IN
            ┌──────────────────────────────────────────────────────┐
            │  Freight Trip  ──(Create ▸ Sales Invoice)──▶  SALES INVOICE  (Debtors/Customer)
            │                                                       │
            │                                  (standard ERPNext)   ▼
            │                                              PAYMENT ENTRY  "Receive"  ──▶ Bank
            └──────────────────────────────────────────────────────┘

                                    MONEY OUT
            ┌──────────────────────────────────────────────────────┐
 Hired truck│  Freight Trip  ──(Create ▸ Truck Hire Invoice)──▶  PURCHASE INVOICE  (Creditor/Owner)
            │                                                          │
            │                                  (standard ERPNext)      ▼
            │                                                 PAYMENT ENTRY  "Pay"  ◀── Bank
            └──────────────────────────────────────────────────────┘
 Hired driver│ Freight Trip  ──(Create ▸ Pay Driver)──────▶  PAYMENT ENTRY  "Pay" (to driver's Supplier)  ◀── Bank
            └──────────────────────────────────────────────────────┘
 Expenses   │ Each Trip Expense (Company‑paid) ──auto──▶  JOURNAL ENTRY
            │        Debit: expense account (Fuel/Allowance/…)
            │        Credit: Payable (if Supplier) OR Bank/Cash
            └──────────────────────────────────────────────────────┘
 Own driver │ Driver linked to Employee  ──▶  ERPNext PAYROLL  (Salary Slip)   ◀── handled by Payroll
```

### The invoice → payment chain, made explicit

**REVENUE — collecting from the customer**
1. On the submitted trip: **Create ▾ → Sales Invoice** → a draft Sales Invoice is created for `Total Revenue`, linked to the trip & customer.
2. Submit the Sales Invoice (it now books **Debtors Dr / Sales Income Cr**).
3. When the customer pays, the standard ERPNext flow applies: open the Sales Invoice → **Create ▸ Payment** → a **Payment Entry** (Receive) is created against that invoice. The invoice is now **Paid**.

> The Sales Invoice and the Payment Entry both carry the **Freight Trip** reference, so you can filter "all money for trip TRIP-2026-0001".

**HIRED TRUCK — paying the owner**
1. Set **Agreed Truck Hire Rate** on the trip (only visible when the truck is *Hired*).
2. **Create ▾ → Truck Hire Invoice** → a draft **Purchase Invoice** to the truck owner (Supplier).
3. Submit it (**Expense Dr / Creditor Cr**).
4. When you pay the owner: Purchase Invoice → **Create ▸ Payment** → **Payment Entry** (Pay). Done.

**HIRED DRIVER — paying posho/allowance**
1. The driver's `Driver Type = Hired Contractor` and a **Supplier** is linked.
2. **Create ▾ → Pay Driver** → a **Payment Entry** (Pay) is created for the trip's `Total Allowances` to that Supplier.

**EXPENSES — running costs**
Each *Company‑paid* **Trip Expense** auto‑posts a **Journal Entry** on submit. If the expense names a Supplier (e.g. a fuel station), it credits **Accounts Payable** (so you later pay via Purchase/Payment); otherwise it credits **Bank/Cash** directly.

**OWN EMPLOYEE DRIVERS**
Allowances booked against an *Own Employee* driver are a company cost (Journal Entry), and their salary flows through **ERPnext Payroll** (Salary Slip → Salary Structure → Payroll Entry → Payment). No double handling.

### How the books stay balanced
Every operation above is standard double‑entry. The Logistics Settings simply decides **which account** each side hits. Nothing is posted "off‑book" — the Logistics P&L you see on the trip equals what the General Ledger will report.

---

## 🧾 Trip Settlement — closing a journey

**Logistics → Trip Settlement → Add Trip Settlement**
- Pick the **Freight Trip** — the summary (customer, revenue, cost, profit margin, linked invoices) is pulled in automatically.
- Enter **Amount Actually Received** (cash from customer so far) and **Amounts Paid Out** (cash disbursed).
- The doc computes:
  - **Customer Balance Outstanding** = Revenue − Received
  - **Costs Still Outstanding** = Total Cost − Paid Out
  - **Net Profit (Accrual)** = Revenue − Cost
  - **Net Cash Position** = Received − Paid Out
- Submit it to **Settled** — the journey is reconciled and locked.

It's the one screen that shows the *whole invoice→payment chain* and the cash reality of the trip.

---

## 👥 Roles & permissions

| Role | Can do |
|---|---|
| **Logistics Manager** | Full access: create, edit, submit, cancel, amend, delete, reports, settings |
| **Logistics User** | Day‑to‑day operations: create/edit/submit trips, waybills, expenses; **read‑only** on settings; no delete/amend |
| **System Manager** | Everything (auto) |
| Accounts roles | Access to the invoices/entries the trips generate |

*Created automatically on install. Assign them from **User → Roles**.*

---

## 📊 Reports & insights

Use the built‑in **List + Report** builder on each doctype. Quick wins:
- **Freight Trip** list → group by *Driver* / *Prime Mover* / *Route* to see who/what is profitable.
- **Trip Expense** → pivot by *Expense Category* to find your biggest cost driver.
- **Driver/Vehicle profitability** → join Freight Trip report by driver/vehicle & sum `Trip Profit`.
- (Optional) add a custom **Query Report** for *"Trips with fuel variance > 0"*.

---

## 🛠 Troubleshooting & FAQ

**Q: The "Create ▾ → Sales Invoice" button doesn't appear.**
A: It only shows on a **submitted** trip that has a **Customer** and a **Total Revenue > 0**.

**Q: No Journal Entry is created for my Trip Expense.**
A: It must be **Paid By = Company** *and* the matching **expense account + payable/bank** must be set in **Logistics Settings**. The app warns you if so.

**Q: The truck hire / driver pay buttons are missing.**
A: They appear only when the **Prime Mover is Hired** (hire invoice) or the **Driver is a Hired Contractor** with a linked Supplier (pay driver). Set those on the master records.

**Q: Revenue field is read‑only.**
A: Revenue auto‑computes from `Cargo Weight × Agreed Rate`. Tick **Flat Rate** to type it manually.

**Q: Costs didn't update after I cancelled an expense.**
A: Click **Recalculate P&L** on the trip, or it will refresh on the next save.

**Q: Can one trip carry multiple consignments?**
A: The trip links one primary Waybill. For consolidated loads, create one Waybill per consignment and either link the main one or extend the trip with a child table (see *Extending*).

**Q: Currency?**
A: All amounts use the company's default currency (e.g. TZS). Fully multi‑currency‑capable through ERPNext's standard settings.

---

## 🔧 Extending the app

- **Multi‑consignment trips:** add a child table `Trip Waybill Item` (Link → Waybill) on Freight Trip and sum revenue in `calculate_revenue`.
- **Container/tank tracking:** add fields to `Transport Vehicle` and a child table on Waybill.
- **GPS/telematics import:** add a DocType that ingests device data and writes actual km into the trip.
- **Custom reports:** add a folder `logistics_management/report/<name>/` with a `.json` + `.py` query report.
- **Print formats:** design a branded Waybill / Freight Trip POD under each doctype's Print Format.

---

## 📁 App structure

```
logistics_management/
├── setup.py, requirements.txt, license.txt, MANIFEST.in
└── logistics_management/                       (package)
    ├── hooks.py                                (install hooks, accounting link on cancel)
    ├── modules.txt  →  "Logistics Management"
    └── logistics_management/                   (module)
        ├── setup.py                            (roles, permissions, custom fields, defaults)
        ├── api.py                              (create Sales/Purchase Invoice, Payments)
        ├── workspace/logistics/logistics.json  (Logistics workspace)
        └── doctype/
            ├── freight_route/        (master + benchmark)
            ├── driver/               (Own Employee / Hired Contractor)
            ├── transport_vehicle/    (Owned / Hired; Prime Mover / Trailer)
            ├── logistics_settings/   (Chart‑of‑Accounts mapping)
            ├── waybill/              (consignment note, submittable)
            ├── trip_expense/         (auto Journal Entry)
            ├── freight_trip/         (THE HUB — P&L engine)
            └── trip_settlement/      (cash reconciliation)
```

---

## 📜 License
MIT — free to use, modify and distribute.

*Built for operators who move goods by road and want every trip's profit — and every shilling — accounted for, from the weighbridge to the bank.*

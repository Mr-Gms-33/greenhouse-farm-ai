# Greenhouse Farm Management Platform — MVP Product Specification

**Status:** Approved for implementation
**Version:** 1.0
**Approved:** 2026-11-15
**Farm location:** Agadir, Morocco
**Specification language:** English
**Application languages:** English and Arabic
**Currency:** Moroccan dirham (MAD)
**Farm timezone:** Africa/Casablanca

## 1. Purpose

This document defines the behavior and acceptance criteria for the first
demonstrable release. It must be approved before application code is written.

This specification supersedes two decisions in the earlier brainstorming brief:

- The application languages are **English and Arabic**, not English and German.
- The only AI feature in the MVP is **financial analysis**. The farming
  assistant, irrigation prediction, and production forecasting are not in the
  MVP.

## 2. Problem

The farm operates 5–10 greenhouses in Agadir and grows tomatoes, peppers,
zucchini, and cucumbers. Operational and financial records can become separated,
which makes it difficult for the owner to answer:

- What was harvested from each greenhouse and crop cycle?
- What revenue and expenses were recorded for a period?
- Which greenhouse or crop was profitable?
- How are revenue, expenses, and profit changing?
- What does the available history suggest about the next financial period?

The system will connect basic production records to sales and expenses, provide
authoritative financial totals, and generate a traceable financial forecast.
It is a decision-support and record-keeping system, not certified accounting,
tax, banking, or autonomous financial advice software.

## 3. MVP outcome

The MVP is successful when:

1. An authorized user signs in.
2. The Owner or Farm Manager records a greenhouse, crop cycle, and harvest.
3. The Owner or Accountant records sales and expenses.
4. The system calculates revenue, expenses, profit, margin, and scoped
   profitability from persisted records.
5. The Owner or Accountant generates a financial analysis that clearly
   separates recorded facts from forecast estimates and links back to source
   records.
6. Each role sees an appropriate dashboard in English or Arabic.

## 4. Users and permissions

The MVP is a single-farm system. A user has exactly one role.

### 4.1 Farm Owner / Administrator

- Full access to operational and financial records.
- Create, activate, and deactivate users.
- Assign one of the three supported roles.
- Generate and view financial analyses.
- View the audit history.

### 4.2 Farm Manager

- Create and update greenhouses, crop cycles, and harvest records.
- View operational dashboards and operational source data.
- Cannot create, update, or delete sales or expenses.
- Cannot generate or view financial analyses or farm-wide financial totals.
- Cannot manage users.

### 4.3 Accountant / Finance Manager

- View greenhouse, crop-cycle, and harvest reference data.
- Create and update sales and expenses.
- View financial dashboards and generate financial analyses.
- Cannot create or update greenhouses, crop cycles, or harvests.
- Cannot manage users.

### 4.4 Authorization rules

- Every protected operation is authorized by the backend; hiding a frontend
  control is not sufficient.
- An unauthenticated request to protected data is rejected.
- An authenticated but unauthorized request is rejected without disclosing the
  protected record.
- Deactivated users cannot start a new session.

## 5. In-scope functional requirements

### 5.1 Authentication and user administration

- Users sign in with email and password and can sign out.
- Email matching is case-insensitive and each email is unique.
- Passwords are never stored or logged in plain text.
- The Owner can create a user, choose a role, and deactivate or reactivate the
  user.
- The system must always retain at least one active Owner account.

### 5.2 Greenhouses

Each greenhouse has:

- A unique name or code.
- Area in square metres, greater than zero.
- Status: active or inactive.
- Optional notes.

An inactive greenhouse remains visible in historical records but cannot receive
a new crop cycle.

### 5.3 Crop cycles

Each crop cycle belongs to one greenhouse and has:

- Crop: tomato, pepper, zucchini, or cucumber.
- Planting date.
- Optional expected end date.
- Status: planned, active, completed, or cancelled.

Rules:

- A greenhouse can have at most one active crop cycle at a time.
- The expected end date cannot be earlier than the planting date.
- A completed or cancelled cycle cannot receive a new harvest.
- Historical cycles remain available after a greenhouse is made inactive.

### 5.4 Harvests

Each harvest belongs to an active crop cycle and has:

- Harvest date.
- Quantity in kilograms, greater than zero.
- Optional quality grade and notes.

The harvest date cannot be earlier than the crop-cycle planting date or later
than the current farm date. The system shows total harvested kilograms by
greenhouse, crop, and selected period.

### 5.5 Customers and sales

A customer has a name and an optional contact reference. Sensitive customer
details are not required for the MVP.

Each sale has:

- Sale date.
- Customer.
- Crop cycle, which connects the sale to a greenhouse and crop.
- Quantity in kilograms, greater than zero.
- Unit price in MAD per kilogram, zero or greater.
- Computed total equal to quantity multiplied by unit price.
- Optional sales channel: wholesaler, market, distributor, or other.
- Optional external reference and notes.

Rules:

- Money is stored and calculated with decimal arithmetic, never binary
  floating-point arithmetic.
- User-entered MAD values support two decimal places. Multiplication results and
  report totals use round-half-up to two decimal places.
- A sale quantity cannot exceed the unsold harvested quantity for its crop
  cycle.
- A harvest cannot be reduced or removed when that would make its crop cycle's
  active sales quantity exceed active harvested quantity.
- A sale can reference a completed crop cycle.
- The application displays the computed total before the record is submitted.

### 5.6 Expenses

Each expense has:

- Expense date.
- Category: seeds/plants, fertilizer, water, energy, labor, equipment,
  maintenance, transport, packaging, or other.
- Amount in MAD, greater than zero.
- Scope: whole farm, greenhouse, or crop cycle.
- The referenced greenhouse or crop cycle when the selected scope requires it.
- Optional supplier/reference and notes.

A crop-cycle expense inherits its greenhouse. Whole-farm expenses contribute to
farm-wide profit but are not silently allocated to individual greenhouse or crop
profitability.

### 5.7 Corrections and audit history

- Owner, Manager, and Accountant changes are limited by their role permissions.
- Records used in reports are corrected through an update or soft deletion; no
  business record is physically removed in the MVP.
- Every create, update, deactivation, and soft deletion records actor, time,
  entity type, entity identifier, and changed field names.
- Audit data does not store passwords, tokens, or unnecessary before/after
  customer or financial values.
- Existing financial-analysis snapshots are immutable. If source records change,
  the snapshot is marked stale and a new analysis can be generated.

### 5.8 Deterministic financial reporting

For a selected inclusive date range, the system calculates:

- **Revenue:** sum of active sale totals in the range.
- **Expenses:** sum of active expense amounts in the range.
- **Profit:** revenue minus expenses.
- **Profit margin:** profit divided by revenue multiplied by 100. If revenue is
  zero, margin is displayed as not applicable rather than infinity or zero.
- Revenue, expenses, and profit grouped by month.
- Revenue and directly scoped expenses by crop and greenhouse.

Profitability views must disclose that whole-farm expenses are included only in
farm-wide profit unless an explicit allocation feature is added in a later
release.

### 5.9 AI financial analysis

The feature consists of verified financial calculations, trend analysis, and an
interpretable machine-learning forecast. A language model is not allowed to
calculate authoritative financial values.

#### Analysis request

The Owner or Accountant selects an analysis end month. The system uses only
complete calendar months in the farm timezone up to that cutoff.

#### Recorded facts

The analysis contains:

- Revenue, expenses, profit, and margin for the selected historical period.
- Month-over-month and period-over-period changes where comparable periods
  exist.
- Highest revenue crop/greenhouse and largest expense categories.
- Data coverage: first and last included dates, complete month count, and source
  record counts.

#### Forecast

- Forecast targets are monthly revenue, monthly expenses, and monthly profit.
- The horizon is the next three complete calendar months.
- At least six consecutive complete calendar months are required. A zero-activity
  month within an otherwise established history is retained as zero rather than
  silently removed.
- The model is an interpretable time-trend regression baseline. Training uses
  chronological data only; future data must never leak into training.
- When at least eight complete months are available, the most recent two months
  are used as a chronological validation window. The validation model is fitted
  only on earlier months, and mean absolute error is reported for each target.
  After validation, the production forecast model may be refitted on all
  available complete months.
- With six or seven months, a forecast may be shown but validation error is
  marked unavailable and confidence is low.
- With fewer than six complete months, the result is `insufficient_data`; no
  numeric forecast is generated.
- Forecasts include model version, generation time, forecast horizon,
  uncertainty/data-quality label, and a visible “estimate, not recorded fact”
  label.
- A forecast may be negative when the learned trend supports it, but forecast
  revenue and expenses are floored at zero. Profit may be negative.

#### Explanation and traceability

- The narrative states only facts and estimates present in the structured
  analysis result.
- English and Arabic narratives communicate the same facts.
- The result links to the included sales and expense lists and stores the source
  cutoff, source record identifiers or reproducible source hash, model version,
  and structured outputs.
- If narrative generation fails, a deterministic localized template renders the
  structured result; the financial analysis remains available.
- The application never describes a forecast as guaranteed and never initiates
  a payment, sale, purchase, or record modification from an analysis.

### 5.10 Role-specific dashboards

**Owner dashboard**

- Current-period revenue, expenses, profit, and margin.
- Active greenhouses and crop cycles.
- Recent harvest, sale, and expense activity.
- Latest financial-analysis state and forecast, when available.

**Farm Manager dashboard**

- Active greenhouses and crop cycles.
- Harvest totals and recent operational activity.
- No sales values, expense values, profit, margin, or forecast values.

**Accountant dashboard**

- Current-period revenue, expenses, profit, and margin.
- Recent sales and expenses.
- Data sufficiency and latest financial-analysis state.

Empty dashboards explain which first record the authorized user should add.

### 5.11 English and Arabic

- Every MVP page, navigation item, field label, validation message, empty state,
  status, and analysis explanation is available in English and Arabic.
- English uses left-to-right direction. Arabic uses right-to-left direction,
  including navigation order, alignment, and directional icons.
- The selected language persists for the user between sessions.
- Domain values are stored language-neutral and translated only for display.
- Dates use the Gregorian calendar and locale-aware formatting.
- English displays MAD values with an English currency label; Arabic displays an
  Arabic currency label. Stored numeric values do not change with locale.
- Mixed content such as email addresses and identifiers remains readable in
  Arabic layouts.

## 6. Out of scope for the MVP

- AI farming assistant or chatbot.
- AI irrigation recommendations.
- AI production or harvest forecasting.
- Weather API integration.
- Irrigation and water-usage management.
- Fertilization and soil management.
- Indoor sensor or IoT integration.
- Employee scheduling and daily task management.
- Inventory, materials, and equipment management.
- Formal invoices, accounts receivable, payment reconciliation, tax, payroll,
  banking, and regulatory accounting.
- Automated financial decisions or autonomous actions.
- Multiple farms/tenants.
- Offline-first operation or a native mobile application.
- Currencies other than MAD.

These items belong in the public post-MVP backlog and must not be silently added
to implementation issues for this release.

## 7. Non-functional requirements

### 7.1 Security and privacy

- All production traffic uses HTTPS.
- Passwords use an established adaptive password hash.
- Authentication tokens/cookies use secure production settings and expire.
- Secrets are supplied through environment/secret stores and never committed.
- Logs, metrics, and traces exclude passwords, tokens, customer names/contact
  details, notes, external references, transaction amounts, and model input
  values.
- Validation and authorization apply on the backend regardless of frontend
  behavior.

### 7.2 Accessibility and responsive behavior

- All primary workflows are keyboard operable.
- Inputs have programmatic labels and errors are associated with their fields.
- Status is not communicated through color alone.
- Text and primary controls meet WCAG 2.1 AA contrast targets.
- MVP workflows remain usable at 360 CSS pixels width and on a desktop viewport.

### 7.3 Reliability and performance

- Persisted records remain after application restart.
- Duplicate submissions caused by a repeated request must not create duplicate
  financial records when the same idempotency key is supplied.
- For the demo dataset, 95% of non-analysis API requests complete within 500 ms
  and financial-analysis requests within 2 seconds, excluding network latency.
- A failed forecast or narrative must not corrupt or hide authoritative
  financial totals.

### 7.4 Observability

- The key journey is `generate traceable financial analysis successfully`.
- Browser, API, database, calculation, and forecast signals carry a correlatable
  trace identifier.
- Structured logs, traces, and metrics expose journey success/failure, latency,
  insufficient-data results, and deterministic fallback usage without exposing
  protected financial data.
- A user-impact alert detects a sustained analysis failure rate or excessive
  latency.

### 7.5 Operability and quality

- A fresh clone starts the connected frontend, backend, and PostgreSQL database
  with one documented command after environment setup.
- Unit, frontend, integration, and end-to-end tests run with one documented
  command.
- Database schema changes use versioned migrations.
- The deployed system supports automatic dev deployment, manually approved
  production promotion, and a documented, tested rollback to the previous
  application image.

## 8. Acceptance criteria

The following criteria are release gates.

### Authentication and authorization

- **AC-001:** A seeded active user for each role can sign in with valid
  credentials and sign out.
- **AC-002:** Invalid credentials return a generic error and do not reveal
  whether the email exists.
- **AC-003:** A deactivated user cannot create a new session.
- **AC-004:** The Owner can create and deactivate a Manager or Accountant, but
  the last active Owner cannot be deactivated.
- **AC-005:** Direct API attempts by the Manager to access financial totals,
  sales, expenses, or analyses are rejected.
- **AC-006:** Direct API attempts by the Accountant to modify greenhouses, crop
  cycles, or harvests are rejected.

### Operations

- **AC-007:** The Owner or Manager can create an active greenhouse with a unique
  name/code and positive area; duplicate names/codes and non-positive areas show
  validation errors.
- **AC-008:** The system prevents two active crop cycles in the same greenhouse.
- **AC-009:** The Owner or Manager can record a positive harvest for an active
  crop cycle using a valid date, and the value remains after page reload and
  application restart.
- **AC-010:** A completed, cancelled, or inactive greenhouse context cannot
  receive an invalid new crop cycle or harvest.

### Finance

- **AC-011:** The Owner or Accountant can create a sale and sees its total as
  quantity multiplied by unit price using decimal arithmetic.
- **AC-012:** A sale exceeding the crop cycle’s unsold harvested quantity is
  rejected with an actionable error, and a harvest correction that would create
  the same over-sold state is also rejected.
- **AC-013:** The Owner or Accountant can create whole-farm, greenhouse, and
  crop-cycle expenses, and required scope references are enforced.
- **AC-014:** For a fixed seeded dataset, report revenue, expenses, profit, and
  margin exactly match independently calculated expected values.
- **AC-015:** When revenue is zero, the margin is shown as not applicable.
- **AC-016:** Whole-farm expenses affect farm-wide profit but are not presented
  as greenhouse- or crop-scoped expenses.
- **AC-017:** Updating or soft-deleting a source record updates new reports,
  leaves an audit event, and marks prior affected analysis snapshots stale.

### AI financial analysis

- **AC-018:** With fewer than six complete months, analysis returns recorded
  facts and `insufficient_data` without numeric forecast values.
- **AC-019:** With six complete months, analysis returns three explicitly
  labelled monthly estimates for revenue, expenses, and profit.
- **AC-020:** With eight or more complete months, analysis reports chronological
  validation MAE for each target and proves the validation months were excluded
  from validation-model training.
- **AC-021:** Revenue and expense forecasts are never negative; profit may be
  negative.
- **AC-022:** Each saved analysis exposes cutoff, coverage, source counts or
  reproducible source hash, model version, generation time, and estimate labels.
- **AC-023:** Recorded financial totals in an analysis equal totals recomputed
  directly from the linked active source records at the snapshot cutoff.
- **AC-024:** Injecting a narrative-generation failure still returns the
  structured analysis and a localized deterministic explanation.
- **AC-025:** Neither English nor Arabic analysis text contains a monetary figure
  absent from the structured result.
- **AC-026:** The analysis performs no write to sales, expenses, harvests,
  customers, or payment systems.

### Dashboards and localization

- **AC-027:** Each role’s dashboard contains only the data permitted in Section
  5.10, including when a protected URL is entered directly.
- **AC-028:** Every MVP screen can switch between English/LTR and Arabic/RTL
  without losing unsaved form values.
- **AC-029:** The selected language survives sign-out/sign-in and a browser
  reload.
- **AC-030:** Automated checks find no untranslated visible application key on
  either locale’s MVP pages.
- **AC-031:** Currency and Gregorian dates render in the selected locale while
  their stored values remain unchanged.

### Production readiness

- **AC-032:** One documented command starts the frontend, backend, and database
  from a fresh clone, and a newly created record survives restart.
- **AC-033:** One documented test command runs passing unit, frontend,
  integration, and end-to-end tests, including AC-005, AC-006, AC-014, AC-018,
  AC-020, AC-024, and the complete core journey.
- **AC-034:** A financial-analysis request can be followed in the telemetry UI
  through correlated browser/API/database/forecast signals without financial
  values or customer data in telemetry.
- **AC-035:** The demo failure trigger causes the user-impact alert to wake the
  responder, which enables deterministic summary-only mode, verifies recovery,
  and writes an incident record without changing financial source records.
- **AC-036:** CI tests every pull request, a main-branch merge deploys dev,
  production requires manual approval, and a recorded rollback drill restores
  the previous application image.

## 9. Core end-to-end acceptance scenario

Using English, an Owner creates a Manager and Accountant. The Manager creates a
greenhouse, starts a tomato crop cycle, and records a harvest. The Accountant
records a sale against that crop cycle and records both a scoped and a whole-farm
expense. The Owner verifies the exact totals and generates a financial analysis.
The analysis identifies its recorded facts, estimates, source coverage, model
version, and data sufficiency. The user changes to Arabic; the same persisted
records and analysis appear in RTL layout with Arabic labels. After restart, all
records remain. Unauthorized cross-role API requests remain rejected.

## 10. Risks and controls

- **Little historical data:** seed clearly labelled demo history; show
  insufficient data for real history rather than fabricate a forecast.
- **Forecast mistaken for accounting truth:** separate deterministic facts from
  estimates visually and structurally.
- **Financial hallucination:** calculate figures outside any language model and
  validate narrative figures against structured output.
- **Scope growth:** keep excluded capabilities in the post-MVP tracker.
- **RTL defects:** include Arabic component and end-to-end tests from the first
  frontend slice.
- **Unauthorized financial access:** enforce and integration-test backend RBAC.
- **Profitability ambiguity:** disclose whole-farm expense treatment everywhere
  scoped profitability is shown.

## 11. Definition of specification complete

This specification is complete when the Owner accepts the MVP scope, roles,
business rules, AI behavior, exclusions, and acceptance criteria. Any later
behavioral change must update this document and the relevant public tracker issue
before its application code is changed.

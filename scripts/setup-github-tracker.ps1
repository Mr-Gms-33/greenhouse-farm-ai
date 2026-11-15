param(
    [string]$Owner = "Mr-Gms-33",
    [string]$Repository = "greenhouse-farm-ai"
)

$ErrorActionPreference = "Stop"
$repo = "$Owner/$Repository"
$milestone = "MVP v1"

function Ensure-Label {
    param(
        [string]$Name,
        [string]$Color,
        [string]$Description
    )

    gh label create $Name --repo $repo --color $Color --description $Description --force | Out-Null
}

function Ensure-Milestone {
    $existing = gh api "repos/$repo/milestones?state=all&per_page=100" |
        ConvertFrom-Json |
        Where-Object { $_.title -eq $milestone } |
        Select-Object -First 1

    if (-not $existing) {
        gh api "repos/$repo/milestones" `
            --method POST `
            -f "title=$milestone" `
            -f "description=Focused production-ready greenhouse farm MVP" |
            Out-Null
    }
}

function Ensure-Issue {
    param(
        [string]$Title,
        [string]$Body,
        [string[]]$Labels,
        [bool]$InMilestone = $true
    )

    $existing = gh issue list --repo $repo --state all --limit 100 --json number,title |
        ConvertFrom-Json |
        Where-Object { $_.title -eq $Title } |
        Select-Object -First 1

    if ($existing) {
        return [int]$existing.number
    }

    $arguments = @(
        "issue", "create",
        "--repo", $repo,
        "--title", $Title,
        "--body", $Body
    )

    foreach ($label in $Labels) {
        $arguments += @("--label", $label)
    }

    if ($InMilestone) {
        $arguments += @("--milestone", $milestone)
    }

    $url = & gh @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create issue: $Title"
    }

    return [int](($url.Trim() -split "/")[-1])
}

$labels = @(
    @("type:process", "6F42C1", "Delivery process and agent workflow"),
    @("type:feature", "1D76DB", "Product capability"),
    @("type:quality", "0E8A16", "Testing and quality gate"),
    @("type:operations", "D93F0B", "Deployment, observability, or operations"),
    @("type:epic", "5319E7", "Grouped future work"),
    @("status:needs-grooming", "FBCA04", "PM grooming required before implementation"),
    @("status:ready", "0E8A16", "Groomed and ready for implementation"),
    @("status:blocked", "B60205", "Blocked by a dependency or decision"),
    @("priority:required", "B60205", "Required for the MVP submission"),
    @("priority:future", "C5DEF5", "Explicitly deferred beyond the MVP"),
    @("area:foundation", "D4C5F9", "Repository and application foundation"),
    @("area:auth", "BFDADC", "Authentication and authorization"),
    @("area:operations", "C2E0C6", "Greenhouse and harvest operations"),
    @("area:finance", "FEF2C0", "Sales, expenses, reports, and financial AI"),
    @("area:frontend", "F9D0C4", "Dashboard, localization, and user interface"),
    @("area:platform", "D4C5F9", "Testing, containers, CI/CD, and observability")
)

foreach ($label in $labels) {
    Ensure-Label -Name $label[0] -Color $label[1] -Description $label[2]
}

Ensure-Milestone

$issue = @{}

$issue.process = Ensure-Issue `
    -Title "Establish the public delivery process" `
    -Labels @("type:process", "priority:required", "status:ready") `
    -Body @"
## Goal

Create the public, durable workflow that agents and reviewers will use before application implementation begins.

## Acceptance criteria

- [ ] The repository is public and contains the approved product specification.
- [ ] `AGENTS.md` links modular process, backlog, and team-role documentation.
- [ ] Product Manager, Software Engineer, QA, and Orchestrator responsibilities and handoffs are explicit.
- [ ] Reusable task, defect, and pull-request templates exist.
- [ ] The ordered backlog maps every AC-001 through AC-036 to public implementation work.
- [ ] Public issue comments show PM, Engineer, QA, and Orchestrator evidence for this baseline.
- [ ] No application implementation is included.

## Out of scope

- Application scaffolding and product behavior belong to later issues.

## Constraints

- Approved specification: `docs/product-spec.md`.
- Process source: `docs/process.md`.
- Documentation baseline may be committed directly as allowed by the initial-documentation exception.
"@

$issue.scaffold = Ensure-Issue `
    -Title "Create the full-stack repository scaffold" `
    -Labels @("type:feature", "area:foundation", "priority:required", "status:needs-grooming") `
    -Body @"
## Goal

Create the React/TypeScript, FastAPI/Python, and PostgreSQL foundation with versioned migrations and safe demo configuration.

## Acceptance criteria

- [ ] The repository has clear frontend, API, database-migration, and shared infrastructure boundaries.
- [ ] Configuration is environment-driven and an example environment file contains no secrets.
- [ ] The API exposes health and readiness checks; readiness verifies the database connection.
- [ ] Versioned migrations create the initial schema without manual database steps.
- [ ] Safe demo seed data is repeatable and clearly labelled as demo data.
- [ ] The planned repository-level start and test commands have executable entry points, even if later issues add services and tests.

## Out of scope

- Authentication and business behavior.

## Constraints

- Depends on #$($issue.process).
- Product criterion: AC-032 foundation.
- Follow `AGENTS.md`; do not add unapproved product scope.
"@

$issue.auth = Ensure-Issue `
    -Title "Implement authentication and role-based authorization" `
    -Labels @("type:feature", "area:auth", "priority:required", "status:needs-grooming") `
    -Body @"
## Goal

Provide secure sessions and backend-enforced Owner, Farm Manager, and Accountant permissions.

## Acceptance criteria

- [ ] Seeded active users for all three roles can sign in and sign out.
- [ ] Invalid credentials return a generic error that does not reveal account existence.
- [ ] Passwords use an established adaptive hash and never appear in logs.
- [ ] Deactivated users cannot create sessions.
- [ ] The Owner can manage users and roles but cannot deactivate the final active Owner.
- [ ] Manager requests for protected finance resources are rejected without record disclosure.
- [ ] Accountant requests that modify operations resources are rejected without record disclosure.
- [ ] Unit and integration tests prove AC-001 through AC-006.

## Out of scope

- External identity providers, password reset email, and multi-factor authentication.

## Constraints

- Depends on #$($issue.scaffold).
- Product criteria: AC-001 through AC-006.
- Backend checks are authoritative; frontend visibility is not authorization.
"@

$issue.greenhouses = Ensure-Issue `
    -Title "Manage greenhouses and crop cycles" `
    -Labels @("type:feature", "area:operations", "priority:required", "status:needs-grooming") `
    -Body @"
## Goal

Let authorized operational users manage greenhouse identities and valid crop-cycle lifecycles.

## Acceptance criteria

- [ ] Owner or Manager can create an active greenhouse with a unique name/code and positive area.
- [ ] Duplicate identity and non-positive area return actionable validation errors.
- [ ] A greenhouse has at most one active crop cycle.
- [ ] Crop, planting date, expected-end-date, and lifecycle rules match the specification.
- [ ] Inactive greenhouses retain history and cannot receive a new crop cycle.
- [ ] Accountant has read-only reference access and cannot mutate either resource.
- [ ] Persistence and authorization are covered by integration tests.

## Out of scope

- Harvests, sensors, irrigation, fertilization, and inventory.

## Constraints

- Depends on #$($issue.auth).
- Product criteria: AC-007, AC-008, and greenhouse/cycle portions of AC-010.
"@

$issue.harvests = Ensure-Issue `
    -Title "Record and validate harvests" `
    -Labels @("type:feature", "area:operations", "priority:required", "status:needs-grooming") `
    -Body @"
## Goal

Persist harvest quantities against valid crop cycles without allowing inconsistent production history.

## Acceptance criteria

- [ ] Owner or Manager can record a positive kilogram quantity for an active crop cycle.
- [ ] Harvest date cannot precede planting or exceed the current Africa/Casablanca farm date.
- [ ] Completed/cancelled cycles and invalid greenhouse contexts reject new harvests.
- [ ] Totals are available by greenhouse, crop, and period.
- [ ] A correction cannot make active sales exceed active harvested quantity.
- [ ] Accountant has read-only reference access.
- [ ] Records survive reload and service restart; tests cover AC-009, AC-010, and the harvest side of AC-012.

## Out of scope

- Sales entry and production forecasting.

## Constraints

- Depends on #$($issue.greenhouses).
- Product criteria: AC-009, AC-010, and AC-012 invariant.
"@

$issue.financeRecords = Ensure-Issue `
    -Title "Record customers, sales, and expenses" `
    -Labels @("type:feature", "area:finance", "priority:required", "status:needs-grooming") `
    -Body @"
## Goal

Let authorized finance users record traceable sales and scoped expenses using exact MAD arithmetic.

## Acceptance criteria

- [ ] Owner or Accountant can manage customers and create sales linked to crop cycles.
- [ ] Sale total equals quantity times unit price using decimal round-half-up to two places.
- [ ] Sale quantity above unsold harvested quantity is rejected.
- [ ] Owner or Accountant can create whole-farm, greenhouse, and crop-cycle expenses with required references.
- [ ] Manager cannot read protected financial values or mutate finance records.
- [ ] Repeated requests with the same idempotency key do not create duplicate financial records.
- [ ] Updates and soft deletion leave an audit event.
- [ ] Integration tests prove AC-011 through AC-013 and the source-record portion of AC-017.

## Out of scope

- Invoices, payments, tax, payroll, banking, and financial reports.

## Constraints

- Depends on #$($issue.harvests).
- Product criteria: AC-011, AC-012, AC-013, and AC-017.
"@

$issue.reports = Ensure-Issue `
    -Title "Calculate deterministic financial reports" `
    -Labels @("type:feature", "area:finance", "priority:required", "status:needs-grooming") `
    -Body @"
## Goal

Calculate authoritative revenue, expense, profit, margin, monthly trend, and scoped profitability from active source records.

## Acceptance criteria

- [ ] A selected inclusive range returns exact revenue, expense, profit, and margin values.
- [ ] Zero revenue produces a not-applicable margin.
- [ ] Results group correctly by month, greenhouse, and crop.
- [ ] Whole-farm expenses affect farm profit and are not silently allocated to greenhouse/crop views.
- [ ] A fixed seeded dataset matches independently calculated expected values.
- [ ] Source updates/soft deletion affect new reports and mark affected analysis snapshots stale.
- [ ] Tests prove AC-014 through AC-017 with decimal boundary cases.

## Out of scope

- Forecasts, LLM arithmetic, certified accounting statements, and expense allocation.

## Constraints

- Depends on #$($issue.financeRecords).
- Product criteria: AC-014 through AC-017.
"@

$issue.ai = Ensure-Issue `
    -Title "Generate traceable AI financial analysis and forecasts" `
    -Labels @("type:feature", "area:finance", "priority:required", "status:needs-grooming") `
    -Body @"
## Goal

Generate an interpretable three-month financial forecast and explanation grounded only in verified historical records.

## Acceptance criteria

- [ ] Fewer than six complete months returns facts plus `insufficient_data` and no numeric forecast.
- [ ] Six or seven months returns three labelled estimates with low confidence and unavailable validation error.
- [ ] Eight or more months uses the latest two only for chronological validation, reports MAE, then may refit for production.
- [ ] Revenue and expense forecasts are floored at zero while profit may be negative.
- [ ] Snapshot stores cutoff, coverage, source counts/hash, model version, generation time, outputs, and estimate labels.
- [ ] Snapshot facts equal independently recomputed source totals.
- [ ] English and Arabic explanations contain no monetary figure absent from structured output.
- [ ] Narrative failure returns a localized deterministic fallback.
- [ ] Analysis writes no operational or financial source record.
- [ ] Tests prove AC-018 through AC-026, including no future-data leakage.

## Out of scope

- Chatbot, irrigation prediction, production forecasting, or autonomous actions.

## Constraints

- Depends on #$($issue.reports).
- Product criteria: AC-018 through AC-026.
- A language model must never calculate authoritative values.
"@

$issue.ui = Ensure-Issue `
    -Title "Deliver role dashboards and English-Arabic interface" `
    -Labels @("type:feature", "area:frontend", "priority:required", "status:needs-grooming") `
    -Body @"
## Goal

Connect the complete MVP through role-specific responsive dashboards in English/LTR and Arabic/RTL.

## Acceptance criteria

- [ ] Owner, Manager, and Accountant dashboards expose only the data allowed by the specification.
- [ ] Protected direct URLs and API requests remain inaccessible to the wrong role.
- [ ] Every MVP string, validation error, empty state, status, and analysis explanation has English and Arabic translations.
- [ ] Locale switches direction without losing unsaved form values and persists through reload and sign-in.
- [ ] Gregorian dates and MAD labels render for the selected locale without changing stored values.
- [ ] Mixed-direction identifiers remain readable and directional icons mirror correctly.
- [ ] Primary workflows are keyboard operable, responsive at 360 CSS pixels, and meet stated accessibility rules.
- [ ] Frontend and end-to-end tests prove AC-027 through AC-031.

## Out of scope

- Native mobile and offline-first applications.

## Constraints

- Depends on #$($issue.auth), #$($issue.greenhouses), #$($issue.harvests), #$($issue.financeRecords), #$($issue.reports), and #$($issue.ai).
- Product criteria: AC-027 through AC-031.
"@

$issue.testGate = Ensure-Issue `
    -Title "Complete the automated quality gate" `
    -Labels @("type:quality", "area:platform", "priority:required", "status:needs-grooming") `
    -Body @"
## Goal

Provide one reliable command that proves unit, frontend, integration, and end-to-end behavior for the complete MVP.

## Acceptance criteria

- [ ] `docker compose run --rm test` runs linting, type checks, migrations, unit, frontend, integration, and end-to-end tests.
- [ ] The gate explicitly covers AC-005, AC-006, AC-014, AC-018, AC-020, AC-024, and the core end-to-end scenario.
- [ ] Tests are isolated, repeatable, and do not depend on execution order or external production services.
- [ ] Failures produce actionable output and a non-zero exit code.
- [ ] Test fixtures are clearly synthetic and contain no protected data.
- [ ] The command passes from a fresh clone using documented prerequisites.

## Out of scope

- Deployment and production monitoring.

## Constraints

- Depends on #$($issue.ui) and all earlier behavior issues.
- Product criterion: AC-033.
"@

$issue.containers = Ensure-Issue `
    -Title "Run the complete local system with Docker Compose" `
    -Labels @("type:operations", "area:platform", "priority:required", "status:needs-grooming") `
    -Body @"
## Goal

Run the frontend, API, PostgreSQL, migrations, and required local support services from a fresh clone with one command.

## Acceptance criteria

- [ ] `docker compose up --build` starts a healthy connected system without manual database steps.
- [ ] Production-oriented images use non-root users, health checks, and explicit dependency readiness.
- [ ] Migrations run safely and demo seeding is explicit and repeatable.
- [ ] A newly created record persists after service restart.
- [ ] `docker compose down` stops the stack and `--volumes` explicitly resets demo data.
- [ ] The complete test command remains runnable in containers.
- [ ] A documented fresh-clone rehearsal proves AC-032 and AC-033.

## Out of scope

- Public cloud deployment.

## Constraints

- Depends on #$($issue.scaffold) and #$($issue.testGate).
- Product criteria: AC-032 and AC-033.
"@

$issue.observability = Ensure-Issue `
    -Title "Instrument the financial-analysis user journey" `
    -Labels @("type:operations", "area:platform", "priority:required", "status:needs-grooming") `
    -Body @"
## Goal

Make financial-analysis success, latency, fallback, and failure diagnosable through correlated logs, metrics, and traces.

## Acceptance criteria

- [ ] Browser, API, database, calculation, and forecast spans share a trace identifier.
- [ ] Structured metrics expose journey success/failure, latency, insufficient-data results, and fallback usage.
- [ ] Logs, metrics, and traces are collected, stored, and viewable in a UI.
- [ ] Telemetry contains no credentials, customer details, notes, references, transaction amounts, or model inputs.
- [ ] One documented trace proves the complete key journey.
- [ ] A user-impact alert detects sustained analysis failure rate or excessive latency rather than infrastructure CPU.
- [ ] Verification proves AC-034.

## Out of scope

- Responder remediation and generic infrastructure alerting.

## Constraints

- Depends on #$($issue.ai) and #$($issue.containers).
- Product criterion: AC-034.
"@

$issue.responder = Ensure-Issue `
    -Title "Implement the bounded on-call responder agent" `
    -Labels @("type:operations", "area:platform", "priority:required", "status:needs-grooming") `
    -Body @"
## Goal

Wake a safe responder on a financial-analysis alert, restore deterministic summary-only service, and record auditable recovery evidence.

## Acceptance criteria

- [ ] A safe demo trigger simulates forecast failure without changing real source records.
- [ ] The alert webhook wakes an observe-decide-act responder.
- [ ] The responder gathers correlated evidence and selects only an allowlisted runbook.
- [ ] It enables deterministic summary-only mode and verifies the user journey recovers.
- [ ] It writes an incident record and provides a reversible disable/rollback control.
- [ ] Arbitrary shell/database actions and automatic code deployment are impossible.
- [ ] An end-to-end drill proves AC-035 and confirms source financial records are unchanged.

## Out of scope

- Autonomous code deployment or unrestricted remediation.

## Constraints

- Depends on #$($issue.observability).
- Product criterion: AC-035.
"@

$issue.delivery = Ensure-Issue `
    -Title "Configure CI/CD, public deployment, and rollback" `
    -Labels @("type:operations", "area:platform", "priority:required", "status:needs-grooming") `
    -Body @"
## Goal

Test every pull request, deploy dev automatically, promote an immutable image to production manually, and prove rollback.

## Acceptance criteria

- [ ] Pull requests run the complete required quality gate and container build.
- [ ] A merge to `main` automatically deploys the tested immutable image to dev.
- [ ] Production promotion requires manual approval and uses the same tested image.
- [ ] Dev and production use managed PostgreSQL, TLS, and secret stores.
- [ ] Database migrations follow a backward-compatible rollback policy.
- [ ] A recorded drill restores the previous production image and verifies health.
- [ ] Public URLs and deployment evidence prove AC-036.

## Out of scope

- Multi-region operation and zero-downtime database rewrites.

## Constraints

- Depends on #$($issue.testGate), #$($issue.containers), #$($issue.observability), and #$($issue.responder).
- Product criterion: AC-036.
"@

$issue.submission = Ensure-Issue `
    -Title "Audit and package final submission evidence" `
    -Labels @("type:quality", "area:platform", "priority:required", "status:needs-grooming") `
    -Body @"
## Goal

Prove every rubric item and product acceptance criterion against a fresh clone and the deployed system.

## Acceptance criteria

- [ ] README links the problem, architecture, local command, tests, deployment, telemetry, alert, responder, CI/CD, and rollback evidence.
- [ ] A rubric checklist links every criterion to authoritative code, docs, tracker, check, screenshot, or demo timestamp.
- [ ] A fresh-clone rehearsal runs the complete application and tests with documented commands.
- [ ] AC-001 through AC-036 each has direct evidence and no unresolved FAIL.
- [ ] Repository and telemetry scans find no secrets or protected data.
- [ ] The public demo scenario works in English and Arabic.
- [ ] The three required peer reviews are completed on the course platform.

## Out of scope

- New product behavior not required to close an existing acceptance gap.

## Constraints

- Depends on every earlier MVP issue, including #$($issue.delivery).
- Product criteria: AC-001 through AC-036.
"@

$issue.future = Ensure-Issue `
    -Title "Post-MVP roadmap for deferred farm capabilities" `
    -Labels @("type:epic", "priority:future") `
    -InMilestone $false `
    -Body @"
## Goal

Keep explicitly deferred ideas visible without expanding the focused MVP.

## Candidate follow-up issues

- [ ] AI farming assistant/chatbot.
- [ ] Irrigation records, weather integration, and AI irrigation recommendations.
- [ ] Production and harvest forecasting.
- [ ] Fertilization and soil management.
- [ ] Indoor sensor and IoT integration.
- [ ] Employee scheduling and daily tasks.
- [ ] Inventory, materials, and equipment.
- [ ] Formal invoices, payments, tax, payroll, and banking.
- [ ] Multiple farms/tenants.
- [ ] Offline-first or native mobile application.
- [ ] Additional currencies.

## Acceptance criteria

- [ ] Each capability is split into its own specified issue only after the MVP is complete and the Owner prioritizes it.

## Out of scope

- Implementation during MVP v1.

## Constraints

- This issue is not part of the MVP v1 milestone.
- Do not use it to bypass the approved product specification.
"@

Write-Output "Tracker ready: https://github.com/$repo/issues"
Write-Output "MVP milestone: https://github.com/$repo/milestone/1"
Write-Output "Created or retained $($issue.Count) ordered MVP issues and one future epic."

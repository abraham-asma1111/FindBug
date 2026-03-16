bugbounty-platform/
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── docker-compose.override.yml
├── Makefile
├── LICENSE
├── CONTRIBUTING.md
├── docs/
│   ├── README.md
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── microservices.md
│   │   ├── data-flow.md
│   │   └── security.md
│   ├── api/
│   │   ├── openapi.yaml
│   │   ├── postman-collection.json
│   │   └── endpoints/
│   │       ├── auth.md
│   │       ├── programs.md
│   │       ├── reports.md
│   │       ├── payments.md
│   │       ├── ptaas.md
│   │       ├── ai-redteaming.md
│   │       └── bounty-match.md
│   ├── database/
│   │   ├── schema.md
│   │   ├── er-diagram.md
│   │   └── migrations-guide.md
│   ├── deployment/
│   │   ├── docker-setup.md
│   │   ├── kubernetes-config.md
│   │   ├── ci-cd-pipeline.md
│   │   └── monitoring.md
│   └── user-guides/
│       ├── researcher.md
│       ├── organization.md
│       ├── triage-specialist.md
│       ├── finance-officer.md
│       └── admin.md
│
├── backend/
│   ├── README.md
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pyproject.toml
│   ├── setup.cfg
│   ├── manage.py
│   ├── alembic.ini
│   ├── pytest.ini
│   │
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── exceptions.py
│   │   │   ├── logging.py
│   │   │   ├── cache.py
│   │   │   ├── database.py
│   │   │   ├── dependencies.py
│   │   │   └── constants.py
│   │   │
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # SQLAlchemy models
│   │   │   ├── enums.py
│   │   │   ├── events.py
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       ├── base.py
│   │   │       ├── user_repository.py
│   │   │       ├── program_repository.py
│   │   │       ├── report_repository.py
│   │   │       ├── payment_repository.py
│   │   │       ├── ptaas_repository.py
│   │   │       ├── ai_redteam_repository.py
│   │   │       └── simulation_repository.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── program_service.py
│   │   │   ├── report_service.py
│   │   │   ├── triage_service.py
│   │   │   ├── payment_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── audit_service.py
│   │   │   ├── simulation_service.py
│   │   │   ├── ptaas_service.py
│   │   │   ├── ai_redteam_service.py
│   │   │   ├── bounty_match_service.py   # FREQ-32 BountyMatch algorithm
│   │   │   ├── ssdlc_integration_service.py
│   │   │   ├── live_event_service.py
│   │   │   ├── commission_service.py      # BR-06 30% commission
│   │   │   └── export_service.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py
│   │   │   │   ├── middlewares/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── rate_limit.py
│   │   │   │   │   ├── audit.py
│   │   │   │   │   └── cors.py
│   │   │   │   │
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth.py           # UC-01 Login/Register
│   │   │   │   │   ├── users.py
│   │   │   │   │   ├── programs.py       # UC-04 Create program
│   │   │   │   │   ├── reports.py        # UC-02 Submit report
│   │   │   │   │   ├── triage.py         # UC-03 Validate report
│   │   │   │   │   ├── payments.py       # UC-05 Approve reward
│   │   │   │   │   ├── dashboard.py      # UC-06 View dashboard
│   │   │   │   │   ├── simulation.py     # UC-07 Practice simulation
│   │   │   │   │   ├── code-review.py    # UC-08 Expert code review
│   │   │   │   │   ├── ssdlc.py          # UC-09 SSDLC integration
│   │   │   │   │   ├── live-events.py    # UC-10 Live hacking event
│   │   │   │   │   ├── ai-redteaming.py  # UC-11 AI Red Teaming
│   │   │   │   │   ├── bounty-match.py   # BountyMatch endpoints
│   │   │   │   │   ├── ptaas.py
│   │   │   │   │   ├── admin.py
│   │   │   │   │   ├── finance.py
│   │   │   │   │   ├── webhooks.py
│   │   │   │   │   └── health.py
│   │   │   │   │
│   │   │   │   └── schemas/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── auth.py
│   │   │   │       ├── users.py
│   │   │   │       ├── programs.py
│   │   │   │       ├── reports.py
│   │   │   │       ├── payments.py
│   │   │   │       ├── ptaas.py
│   │   │   │       ├── ai_redteam.py
│   │   │   │       └── simulation.py
│   │   │   │
│   │   │   └── v2/                         # Future API versions
│   │   │
│   │   └── tasks/
│   │       ├── __init__.py
│   │       ├── celery_app.py
│   │       ├── email_tasks.py
│   │       ├── notification_tasks.py
│   │       ├── report_tasks.py
│   │       ├── payment_tasks.py
│   │       ├── cleanup_tasks.py
│   │       ├── bounty_match_tasks.py
│   │       └── analytics_tasks.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── fixtures/
│   │   │   ├── users.json
│   │   │   ├── programs.json
│   │   │   └── reports.json
│   │   ├── unit/
│   │   │   ├── test_models.py
│   │   │   ├── test_services/
│   │   │   │   ├── test_auth_service.py
│   │   │   │   ├── test_report_service.py
│   │   │   │   ├── test_payment_service.py
│   │   │   │   ├── test_bounty_match.py
│   │   │   │   └── test_commission.py      # BR-06 commission logic
│   │   │   └── test_utils.py
│   │   ├── integration/
│   │   │   ├── test_api_endpoints.py
│   │   │   ├── test_database.py
│   │   │   ├── test_external_services.py
│   │   │   └── test_ssdlc_integration.py   # UC-09 Jira/GitHub sync
│   │   └── e2e/
│   │       ├── test_bug_bounty_flow.py
│   │       ├── test_ptaas_flow.py
│   │       └── test_ai_redteam_flow.py
│   │
│   ├── migrations/
│   │   ├── versions/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── README.md
│   │
│   └── scripts/
│       ├── seed_db.py
│       ├── create_admin.py
│       ├── backup_db.sh
│       └── generate_demo_data.py
│
├── frontend/
│   ├── README.md
│   ├── package.json
│   ├── package-lock.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── tsconfig.json
│   ├── .eslintrc.json
│   ├── .prettierrc
│   │
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── images/
│   │   ├── fonts/
│   │   └── locales/                    # Multi-language support (CC-04)
│   │       ├── en/
│   │       ├── am/                      # Amharic
│   │       └── fr/                       # French
│   │
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx                  # Homepage
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   ├── register/
│   │   │   │   └── page.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── page.tsx
│   │   │   │   ├── researcher/           # Image 31
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── organization/         # Image 36, 37
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── triage/               # Image 46
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── finance/              # Image 50, 51
│   │   │   │   │   └── page.tsx
│   │   │   │   └── admin/                 # Image 47-49
│   │   │   │       └── page.tsx
│   │   │   ├── programs/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── [id]/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── create/                # Image 35
│   │   │   │       └── page.tsx
│   │   │   ├── reports/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── submit/                # Image 33, 34
│   │   │   │   │   └── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── simulation/                # UC-07
│   │   │   │   └── page.tsx
│   │   │   ├── ptaas/
│   │   │   │   └── page.tsx
│   │   │   ├── ai-redteaming/
│   │   │   │   └── page.tsx
│   │   │   ├── payments/
│   │   │   │   └── page.tsx
│   │   │   ├── leaderboard/
│   │   │   │   └── page.tsx
│   │   │   ├── settings/
│   │   │   │   └── page.tsx
│   │   │   └── api/                       # Next.js API routes (optional fallback)
│   │   │       └── [...path]/
│   │   │           └── route.ts
│   │   │
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── LoadingSpinner.tsx
│   │   │   │   ├── ErrorBoundary.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Select.tsx
│   │   │   │   ├── FileUpload.tsx          # For report attachments
│   │   │   │   └── RichTextEditor.tsx
│   │   │   │
│   │   │   ├── layout/
│   │   │   │   ├── DashboardLayout.tsx
│   │   │   │   └── AuthLayout.tsx
│   │   │   │
│   │   │   ├── features/
│   │   │   │   ├── auth/
│   │   │   │   │   ├── LoginForm.tsx
│   │   │   │   │   ├── RegisterForm.tsx    # Image 30
│   │   │   │   │   ├── ForgotPassword.tsx
│   │   │   │   │   └── MFAVerification.tsx
│   │   │   │   │
│   │   │   │   ├── dashboard/
│   │   │   │   │   ├── ResearcherDashboard.tsx
│   │   │   │   │   ├── OrganizationDashboard.tsx
│   │   │   │   │   ├── TriageDashboard.tsx
│   │   │   │   │   ├── FinanceDashboard.tsx
│   │   │   │   │   └── AdminDashboard.tsx
│   │   │   │   │
│   │   │   │   ├── programs/
│   │   │   │   │   ├── ProgramList.tsx
│   │   │   │   │   ├── ProgramCard.tsx
│   │   │   │   │   ├── ProgramDetails.tsx
│   │   │   │   │   ├── ProgramForm.tsx
│   │   │   │   │   └── ScopeEditor.tsx
│   │   │   │   │
│   │   │   │   ├── reports/
│   │   │   │   │   ├── ReportForm.tsx
│   │   │   │   │   ├── ReportList.tsx
│   │   │   │   │   ├── ReportDetails.tsx
│   │   │   │   │   ├── TriageQueue.tsx
│   │   │   │   │   ├── DuplicateChecker.tsx
│   │   │   │   │   └── SeveritySelector.tsx
│   │   │   │   │
│   │   │   │   ├── payments/
│   │   │   │   │   ├── PaymentApproval.tsx
│   │   │   │   │   ├── PaymentHistory.tsx
│   │   │   │   │   ├── CommissionCalculator.tsx
│   │   │   │   │   └── PayoutMethodSelector.tsx
│   │   │   │   │
│   │   │   │   ├── simulation/
│   │   │   │   │   ├── ChallengeList.tsx
│   │   │   │   │   ├── SimulationEnvironment.tsx
│   │   │   │   │   ├── FeedbackPanel.tsx
│   │   │   │   │   └── ProgressTracker.tsx
│   │   │   │   │
│   │   │   │   ├── ptaas/
│   │   │   │   │   ├── PTaaSRequestForm.tsx
│   │   │   │   │   ├── EngagementTracker.tsx
│   │   │   │   │   └── MethodologyChecklist.tsx
│   │   │   │   │
│   │   │   │   ├── ai-redteaming/
│   │   │   │   │   ├── AIEngagementForm.tsx
│   │   │   │   │   ├── AttackTypeSelector.tsx
│   │   │   │   │   ├── PromptInjector.tsx
│   │   │   │   │   └── SafetyReport.tsx
│   │   │   │   │
│   │   │   │   ├── bounty-match/
│   │   │   │   │   ├── MatchRecommendations.tsx
│   │   │   │   │   ├── SkillProfile.tsx
│   │   │   │   │   └── MatchHistory.tsx
│   │   │   │   │
│   │   │   │   ├── ssdlc/
│   │   │   │   │   ├── IntegrationConfig.tsx
│   │   │   │   │   ├── JiraSync.tsx
│   │   │   │   │   └── GitHubSync.tsx
│   │   │   │   │
│   │   │   │   └── analytics/
│   │   │   │       ├── VulnerabilityChart.tsx
│   │   │   │       ├── ProgramMetrics.tsx
│   │   │   │       ├── ResearcherStats.tsx
│   │   │   │       └── FinancialOverview.tsx
│   │   │   │
│   │   │   └── ui/
│   │   │       ├── charts/
│   │   │       │   ├── LineChart.tsx
│   │   │       │   ├── BarChart.tsx
│   │   │       │   ├── PieChart.tsx
│   │   │       │   └── HeatMap.tsx
│   │   │       ├── tables/
│   │   │       │   ├── DataTable.tsx
│   │   │       │   └── Pagination.tsx
│   │   │       └── cards/
│   │   │           ├── StatCard.tsx
│   │   │           └── MetricCard.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── usePrograms.ts
│   │   │   ├── useReports.ts
│   │   │   ├── usePayments.ts
│   │   │   ├── useSimulation.ts
│   │   │   ├── useBountyMatch.ts
│   │   │   ├── useNotifications.ts
│   │   │   └── useLocalStorage.ts
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts                       # Axios instance
│   │   │   ├── auth.ts
│   │   │   ├── websocket.ts
│   │   │   ├── formatters.ts
│   │   │   ├── validators.ts
│   │   │   └── utils.ts
│   │   │
│   │   ├── store/
│   │   │   ├── authSlice.ts
│   │   │   ├── programSlice.ts
│   │   │   ├── reportSlice.ts
│   │   │   ├── notificationSlice.ts
│   │   │   └── index.ts
│   │   │
│   │   ├── styles/
│   │   │   ├── globals.css
│   │   │   └── themes/
│   │   │       ├── light.ts
│   │   │       └── dark.ts
│   │   │
│   │   ├── types/
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   ├── user.ts
│   │   │   ├── program.ts
│   │   │   ├── report.ts
│   │   │   ├── payment.ts
│   │   │   ├── simulation.ts
│   │   │   ├── ptaas.ts
│   │   │   ├── aiRedteam.ts
│   │   │   └── bountyMatch.ts
│   │   │
│   │   └── middleware.ts                     # Next.js middleware for auth
│   │
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   │
│   └── .storybook/                           # Component documentation
│       ├── main.ts
│       └── preview.ts
│
├── simulation/                                 # Isolated simulation environment (BR-12)
│   ├── README.md
│   ├── docker-compose.sim.yml
│   ├── Dockerfile.sim
│   ├── requirements.sim.txt
│   │
│   ├── src/
│   │   ├── main.py
│   │   ├── challenges/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── beginner/
│   │   │   │   ├── sqli.py
│   │   │   │   ├── xss.py
│   │   │   │   └── csrf.py
│   │   │   ├── intermediate/
│   │   │   │   ├── idor.py
│   │   │   │   ├── ssrf.py
│   │   │   │   └── lfi.py
│   │   │   └── advanced/
│   │   │       ├── rce.py
│   │   │       ├── deserialization.py
│   │   │       └── chain_vulns.py
│   │   ├── targets/                           # Simulated vulnerable apps
│   │   │   ├── webapp/
│   │   │   ├── api/
│   │   │   └── mobile/
│   │   ├── scoring/
│   │   │   ├── engine.py
│   │   │   ├── feedback.py
│   │   │   └── hints.py
│   │   ├── isolation/
│   │   │   ├── network.py
│   │   │   └── sandbox.py
│   │   └── api/
│   │       └── routes.py
│   │
│   └── data/
│       └── challenges/
│
├── infrastructure/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── modules/
│   │   │   ├── vpc/
│   │   │   ├── rds/
│   │   │   ├── redis/
│   │   │   ├── ecs/
│   │   │   └── s3/
│   │   └── environments/
│   │       ├── dev/
│   │       ├── staging/
│   │       └── prod/
│   │
│   ├── kubernetes/
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secrets.yaml
│   │   ├── backend/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   ├── hpa.yaml
│   │   │   └── ingress.yaml
│   │   ├── frontend/
│   │   │   ├── deployment.yaml
│   │   │   └── service.yaml
│   │   ├── simulation/
│   │   │   └── deployment.yaml
│   │   ├── redis/
│   │   ├── postgres/
│   │   └── celery/
│   │
│   ├── monitoring/
│   │   ├── prometheus/
│   │   │   └── prometheus.yml
│   │   ├── grafana/
│   │   │   └── dashboards/
│   │   ├── alertmanager/
│   │   └── elk/
│   │       ├── elasticsearch/
│   │       ├── logstash/
│   │       └── kibana/
│   │
│   └── scripts/
│       ├── backup.sh
│       ├── restore.sh
│       ├── deploy.sh
│       └── healthcheck.sh
│
├── scripts/
│   ├── generate-models.sh
│   ├── create-migration.sh
│   ├── seed-data.sql
│   └── dev-setup.sh
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── cd.yml
│   │   ├── test.yml
│   │   └── security-scan.yml
│   ├── CODEOWNERS
│   └── PULL_REQUEST_TEMPLATE.md
│
└── security/
    ├── SECURITY.md
    ├── audit-logs.md
    ├── rbac-policies.yaml
    ├── owasp-checklist.md
    └── penetration-test-report.md
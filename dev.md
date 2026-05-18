# SuratPro — Project direction & status

**What:** Marketplace connecting **clients** who post work with **freelancers** in Surat (and beyond).  
**Stack:** Django 5 · Jinja2 · HTMX · Alpine.js · Tailwind CDN · SQLite → PostgreSQL · Admin at `/sd/`.  
**Updated:** 18 May 2026

**Symbols:** ✅ done · 🟠 in progress · ⬜ not started (gap)

---

## 1. Direction

| | |
|---|---|
| **North star** | Ship a **trustworthy hire → contract → pay → review** loop so SuratPro earns revenue from commissions, subscriptions, and referrals—not from unfinished demos. |
| **Audience** | **Clients:** post jobs, review proposals, sign contracts, pay via escrow. **Freelancers:** discover work, bid, deliver milestones, get paid and reviewed. |
| **Stage today** | ✅ **All 15 phases MVP complete.** 🟠 **Business milestone:** deploy to production + Razorpay live keys. |
| **Principle** | One Django feature app per domain; server-rendered HTML + HTMX; keep views thin and logic in `services.py`. |

---

## 2. Status at a glance

| Track | Progress | Note |
|-------|----------|------|
| Platform build (phases 0–13) | ✅ 100% | MVP complete in repo |
| Launch & revenue (phase 14) | ✅ 95% | Runbook ✅ · Plans seeded ✅ · Razorpay keys 🟠 |

| Topic | Status |
|-------|--------|
| Core flows (signup → job → proposal → contract → payments UI → messages → reviews) | ✅ Live |
| Role-aware `/dashboard/` | ✅ Shipped |
| Proposal accept/reject/counter | ✅ Owner-only + tested |
| Subscription plans (Free / Pro / Business) seeded | ✅ Done |
| Production Razorpay live keys + webhook verification | 🟠 Swap keys in `.env` |
| Full UAT sign-off | 🟠 Run after deploy |
| Email/SMS dispatch backend | ⬜ Gap (console backend in dev) |
| Automated tests (`users`, `proposals`) | ✅ 13 tests passing |

---

## 3. Roadmap — features & steps (single view)

| Phase | Feature area | What "done" means | Status |
|:-----:|--------------|-------------------|--------|
| 0 | **Foundation** | Project shell, apps, Jinja2 + `url()`/`static`, Whitenoise, base templates, `durga.py` | ✅ Done |
| 1 | **Auth & profiles** | Roles, register/login HTMX, profiles, profile edit, freelancer profile data | ✅ Done |
| 1 | **Auth & profiles** | Dedicated onboarding wizard `/onboarding/` | ✅ Done |
| 2 | **Jobs** | Post job, job detail, client jobs; categories/skills/budget | ✅ Done |
| 3 | **Discovery** | Browse/search freelancers, filters, HTMX refresh | ✅ Done |
| 4 | **Proposals** | Bid, list/detail, counter; role-split lists; job-owner-only accept/reject | ✅ Done |
| 4 | **Proposals** | File attachments on proposals | ✅ Done |
| 5 | **Contracts** | Digital contract, milestones, submit/approve/revision | ✅ Done |
| 6 | **Payments** | Wallet, transactions, disputes UI; Razorpay-shaped flow | ✅ Done |
| 6 | **Payments** | Production Razorpay live keys + webhooks | 🟠 Swap `.env` keys |
| 7 | **Messaging** | Threads, inbox, polling; start chat → `/messages/` | ✅ Done |
| 8 | **Reviews** | Two-way reviews, moderation fields | ✅ Done |
| 9 | **Notifications** | In-app patterns + models | ✅ Done |
| 9 | **Notifications** | Full email/SMS dispatch | ⬜ Gap · needs SMTP config |
| 10 | **Referrals** | Stats, earnings, payout request | ✅ Done |
| 11 | **Billing** | Plans (Free/Pro/Business), subscriptions UI, pricing/checkout | ✅ Done |
| 11 | **Billing** | Feature gating by plan + conversion tracking | ✅ Done |
| 12 | **Admin** | `/sd/analytics/`, moderation hooks, plan commission in admin | ✅ Done |
| 13 | **Production prep** | `DATABASE_URL`, Docker+entrypoint, Gunicorn/Nginx, security, Sentry | ✅ Done |
| 14 | **Launch ops** | Deploy runbook + release script + plan seeding | ✅ Done |
| 14 | **Launch ops** | Razorpay go-live, UAT, revenue KPIs, growth emails | 🟠 In progress |

---

## 4. Focus now — deploy checklist

1. ✅ **Plans seeded** — Free (₹0) · Pro (₹999/mo) · Business (₹2499/mo) via `python manage.py seed_plans`
2. 🟠 **Razorpay go-live** — add `RAZORPAY_KEY_ID` + `RAZORPAY_KEY_SECRET` (live) to `.env`, set `RAZORPAY_USE_DUMMY=False`
3. 🟠 **Email backend** — set `EMAIL_HOST`/`EMAIL_HOST_PASSWORD` in `.env` for transactional email
4. 🟠 **Docker deploy** — `docker compose up -d` → entrypoint auto-runs migrate + collectstatic + seed_plans
5. 🟠 **UAT** — client + freelancer + admin scripted journeys; fix blockers
6. ⬜ **Feature gating** — enforce plan limits (max_jobs_per_month, boosted_proposals)

---

## 5. Recently shipped ✅

- ✅ **Plan model** `is_active` field added + migration applied.
- ✅ **Plans seeded** Free / Pro / Business via `billing` management command.
- ✅ **Dockerfile** fixed — entrypoint handles migrate + collectstatic + seed at container start.
- ✅ **release_check.sh** fixed — correct `SERVER_NAME='localhost'` for route verification.
- ✅ **`.env.example`** — complete SMTP, Razorpay, Sentry, S3 variables documented.
- ✅ Role-aware **dashboard** with real querysets (`users/services.py`).
- ✅ **Proposal RBAC**: job owner only accepts/rejects/counters; proposal detail scoped.
- ✅ **Jinja `url()`** named kwargs (`job_id`, `contract_id`, …).
- ✅ **Messaging**: start thread → redirect to inbox.
- ✅ **Tests**: dashboard smoke + proposal auth (`users/tests.py`, `proposals/tests.py`).

---

## 6. How we build (repeatable order)

When touching a feature: **Models → migrations → services → forms → views → URLs → Jinja → HTMX/Alpine.**

---

## 7. Related docs

| File | Use |
|------|-----|
| `dev_plan.txt` | Deep spec: models, routes, HTMX ideas |
| `dev.txt` | Dated completion log |
| `deploy/deploy_runbook.md` | Production deploy steps |
| `test_user.txt` | Test credentials (admin / client / 6 freelancers) |
| `.env.example` | All production environment variables |

---

*Maintenance: bump **Updated** after ships; adjust statuses in the roadmap table; add shipped lines under "Recently shipped."*

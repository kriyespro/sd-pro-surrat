# SuratPro — Final Plan & Status

**Surat's #1 Freelance Marketplace**
**Stack:** Django 5 · Jinja2 · HTMX · Alpine.js · Tailwind CDN · SQLite → PostgreSQL
**Server:** http://127.0.0.1:8000
**Last updated:** 18 May 2026

---

## Test Credentials

| Role | Username | Password | URL |
|------|----------|----------|-----|
| Superuser | `admin` | `admin1234` | `/admin/` (Mission Control) |
| Client | `rahul_shah` | `Test1234!` | `/dashboard/` |
| Freelancer | `karan_patel` | `Test1234!` | `/dashboard/` |
| Freelancer | `nidhi_desai` | `Test1234!` | `/profile/nidhi_desai/` |
| Freelancer | `dev_mehta` | `Test1234!` | `/profile/dev_mehta/` |
| Freelancer | `priya_vora` | `Test1234!` | `/profile/priya_vora/` |
| Freelancer | `aisha_khan` | `Test1234!` | `/profile/aisha_khan/` |
| Freelancer | `vijay_prajapati` | `Test1234!` | `/profile/vijay_prajapati/` |

---

## Phase Completion

| Phase | Feature | Status | Date |
|-------|---------|--------|------|
| 0 | Project Setup | ✅ Complete | 26 Apr 2026 |
| 1 | Auth & User Profiles | ✅ Complete | 26 Apr 2026 |
| 2 | Job & Gig Posting | ✅ Complete | May 2026 |
| 3 | Search & Discovery | ✅ Complete | May 2026 |
| 4 | Proposals & Bidding | ✅ Complete | May 2026 |
| 5 | Contracts & Milestones | ✅ Complete | May 2026 |
| 6 | Secure Payments & Escrow | ✅ Complete | May 2026 |
| 7 | Messaging & Chat | ✅ Complete | May 2026 |
| 8 | Reviews & Ratings | ✅ Complete | May 2026 |
| 9 | Notifications | ✅ Complete | May 2026 |
| 10 | Referral & Affiliates | ✅ Complete | May 2026 |
| 11 | Subscription & Billing | ✅ Complete | May 2026 |
| 12 | Admin / Mission Control | ✅ Complete | 18 May 2026 |
| 13 | Production Prep | ✅ Complete | May 2026 |
| 14 | Launch & Revenue Ops | ✅ MVP Complete | 15 May 2026 |
| — | Onboarding Wizard | ✅ Complete | May 2026 |
| — | Proposal File Attachments | ✅ Complete | May 2026 |
| — | Feature Gating by Plan | ✅ Complete | May 2026 |
| — | Find Work Job Board | ✅ Complete | 18 May 2026 |
| — | Auth-aware CTAs (nav/home) | ✅ Complete | 18 May 2026 |
| — | Accept Proposal → Auto Contract | ✅ Complete | 18 May 2026 |

**Total: 19/19 features complete. MVP shipped.**

---

## Live Routes

| URL | View | Auth |
|-----|------|------|
| `/` | Home | Public |
| `/auth/login/` | Login / Register | Public |
| `/auth/register/` | Register | Public |
| `/auth/logout/` | Logout | POST |
| `/onboarding/` | 2-step wizard | Login required |
| `/dashboard/` | Role-aware dashboard | Login required |
| `/dashboard/profile/edit/` | Edit profile | Login required |
| `/profile/<username>/` | Public profile | Public |
| `/browse/` | Find Talent (freelancer search) | Public |
| `/jobs/find/` | Find Work (job board) | Public |
| `/jobs/post/` | Post a Job | Client only |
| `/jobs/<id>/` | Job detail + proposal form | Public |
| `/jobs/<id>/propose/` | Submit proposal | Freelancer only |
| `/proposals/<id>/accept/` | Accept proposal + create contract | Client only |
| `/proposals/<id>/reject/` | Reject proposal | Client only |
| `/contracts/` | Contract list | Login required |
| `/contracts/<id>/` | Contract detail + milestones | Login required |
| `/contracts/<id>/sign/` | Sign contract | Login required |
| `/contracts/<id>/milestones/add/` | Add milestone | Client only |
| `/contracts/milestones/<id>/submit/` | Submit deliverable | Freelancer only |
| `/contracts/milestones/<id>/approve/` | Approve milestone | Client only |
| `/contracts/milestones/<id>/revision/` | Request revision | Client only |
| `/payments/` | Wallet + transactions | Login required |
| `/messages/` | Inbox | Login required |
| `/messages/<thread_id>/` | Thread | Login required |
| `/reviews/leave/<contract_id>/` | Leave review | Login required |
| `/notifications/` | Notifications | Login required |
| `/referral/` | Referral dashboard | Login required |
| `/pricing/` | Subscription plans | Public |
| `/admin/` | Mission Control | Superuser only |
| `/sd/` | Django Admin | Staff only |

---

## Data Model Summary

### Users App
- `User` (AbstractUser) — role, phone, avatar, city, bio, is_verified, referral_code, onboarding_complete
- `FreelancerProfile` — title, skills (M2M), hourly_rate, min_project, availability, avg_rating, total_reviews
- `Category` — name, icon, slug
- `Skill` — name, category (FK)
- `PortfolioItem`, `Certification`

### Jobs App
- `Job` — client, title, description, category, skills (M2M), pricing_type, budget_min/max, deadline, experience_level, visibility, status, is_featured, views_count

### Proposals App
- `Proposal` — job, freelancer, cover_letter, proposed_rate, delivery_days, attachment, status, created_at
- `BidLimit` — freelancer, date, count

### Contracts App
- `Contract` — job, proposal, client, freelancer, total_value, status, signed_by_client, signed_by_freelancer
- `Milestone` — contract, title, description, amount, due_date, status, order
- `Deliverable` — milestone, file, note
- `RevisionRequest` — milestone, requested_by, note

### Payments App
- `Wallet` — user, balance, escrow_balance
- `Transaction` — wallet, type, amount, ref_id, contract, milestone, status
- `Dispute` — contract, raised_by, reason, status, resolution

### Messaging App
- `Thread` — participants (M2M), contract (FK nullable)
- `Message` — thread, sender, body, file, is_read

### Reviews App
- `Review` — contract, reviewer, reviewee, rating (1–5), feedback, is_public, is_approved

### Notifications App
- `Notification` — user, type, title, body, url, is_read
- `NotificationPreference` — per-user email/SMS toggles

### Referrals App
- `Referral` — referrer, referred, code, signup_bonus_paid, first_job_bonus_paid
- `AffiliateEarning` — referral, type, amount
- `PayoutRequest` — user, amount, status, upi_id

### Billing App
- `Plan` — name, price_monthly, price_yearly, max_jobs_per_month, commission_rate, boosted_proposals, is_active
- `Subscription` — user, plan, billing_cycle, status, current_period_end

---

## Subscription Plans (live in DB)

| Plan | Monthly | Max Jobs/mo | Commission | Bid Limit |
|------|---------|-------------|------------|-----------|
| Free | ₹0 | 3 | 15% | 5/day |
| Pro | ₹999 | 20 | 10% | Unlimited |
| Enterprise | ₹2,499 | Unlimited | 5% | Unlimited |

---

## Feature Gating (billing/services.py)

- `can_post_job(user)` — checks `max_jobs_per_month` against jobs posted this month
- `can_submit_proposal(user)` — checks daily bid limit against `BidLimit` model
- `increment_bid_count(user)` — increments `BidLimit.count` for today

---

## Mission Control (`/admin/`)

Superuser-only. 8 tabs:

| Tab | Contents |
|-----|---------|
| Dashboard | Revenue KPIs (today/7d/30d), sparkline, platform health, recent signups, transactions, build status |
| Users | All users, live search/filter by role/status, Verify / Ban / Unban / Toggle Staff |
| Jobs | All jobs, filter by status, Activate / Feature / Delete |
| Proposals | All proposals, filter by status |
| Contracts | All contracts, milestone count, signature status |
| Reviews | All reviews, Approve / Hide moderation actions |
| Payments | All transactions + open disputes |
| Moderation | Unified queue: pending reviews, open disputes, draft jobs, unverified users |

All actions fire via HTMX POST. Toast on completion. URL hash persistence (`#users`, `#jobs`, etc.).

---

## DB State (18 May 2026)

| Model | Count |
|-------|-------|
| Users | 10 |
| Jobs | 7 (all active) |
| Proposals | 7 |
| Contracts | 5 |
| Milestones | 9 |
| Transactions | 8 |
| Disputes | 1 |
| Reviews | 4 |
| Referrals | 4 |
| Threads | 6 |
| Messages | 11 |
| Notifications | 3 |
| Plans | 3 |
| Subscriptions | 1 |
| Wallets | 2 |

---

## Templates

```
templates/
├── base.jinja
├── admin/
│   ├── mission_control.html   ← /admin/ (superuser)
│   └── analytics.html         ← legacy (redirects to /admin/)
├── components/
│   ├── nav.jinja              ← auth-aware (Dashboard/Sign Out vs Log In/Get Started)
│   ├── footer.jinja
│   ├── card.jinja
│   └── button.jinja
├── layouts/
│   ├── dashboard.jinja
│   └── main.jinja
├── pages/
│   ├── home.jinja
│   ├── browse.jinja           ← Find Talent (freelancer search)
│   ├── jobs_list.jinja        ← Find Work (job board)
│   ├── job_detail.jinja       ← proposal form + role-aware panel
│   ├── post_job.jinja         ← 4-step wizard (Alpine.js)
│   ├── profile.jinja
│   ├── profile_edit.jinja
│   ├── dashboard.jinja        ← role-aware tabs (overview/jobs/proposals/contracts)
│   ├── onboarding.jinja       ← 2-step wizard
│   ├── contract.jinja         ← milestone management
│   ├── messages.jinja
│   ├── payments.jinja
│   ├── pricing.jinja
│   ├── referral.jinja
│   └── auth/login.jinja
└── partials/
    ├── _freelancer_card.jinja
    ├── _job_card.jinja
    ├── _proposal_form.jinja   ← HTMX post, file attachment
    ├── _proposal_card.jinja
    ├── _milestone_card.jinja
    ├── _message_bubble.jinja
    ├── _thread_list.jinja
    ├── _review_form.jinja
    ├── _review_card.jinja
    ├── _star_rating.jinja
    ├── _notification_item.jinja
    ├── _transaction_row.jinja
    ├── _release_modal.jinja
    ├── _referral_row.jinja
    ├── _plan_card.jinja
    ├── _filter_sidebar.jinja
    ├── _login_form.jinja
    └── _register_form.jinja
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, Django 5.0.6 |
| Templates | Jinja2 (all pages), DjangoTemplates (Django admin only) |
| Frontend interactions | HTMX 1.9 (server-driven), Alpine.js 3.x (UI state) |
| CSS | Tailwind CDN (dev) |
| Database | SQLite (dev) → PostgreSQL (prod via `DATABASE_URL`) |
| Static files | WhiteNoise (dev + prod) |
| Media | Local (dev) → S3/R2 via django-storages (prod) |
| Payments | Razorpay-shaped (sandbox ready, live keys in `.env`) |
| Auth | Django built-in + custom `User(AbstractUser)` |
| Admin | `/admin/` custom Mission Control + `/sd/` Django Admin |
| Queue | Celery + Redis (configured, not activated in dev) |
| Deploy | Docker + docker-compose + Gunicorn + Nginx |

---

## Design System

```css
--gold:    #E8A830   /* Primary CTA, accents */
--teal:    #0D6E6E   /* Secondary, nav */
--dark:    #080F0F   /* Page background */
--dark2:   #0D1A1A   /* Card background */
--mid:     #142323   /* Section background */
--text-muted: #7AABAB
--green:   #3ECA8F   /* Success */
--red:     #E85D04   /* Alerts, errors */
```

Fonts: **Playfair Display** (headings) · **DM Sans** (body) · **Space Mono** (mono/numbers)

---

## Remaining Gaps (Post-MVP)

| Gap | Priority | Notes |
|-----|----------|-------|
| Razorpay live keys | High | Swap `RAZORPAY_KEY_ID` + `RAZORPAY_KEY_SECRET` in `.env` |
| Email SMTP backend | High | Set `EMAIL_HOST` + credentials in `.env` |
| Video call integration | Medium | WebRTC or Daily.co embed in messaging |
| Push notifications | Low | Browser Push API or Firebase FCM |
| Revenue analytics v2 | Medium | GMV, take-rate, conversion funnel |
| UAT sign-off | Pre-launch | Browser QA on all 10 pages, scripted user journeys |

---

## Key Flows (tested & working)

### Freelancer proposes on a job
1. Login → `/dashboard/` → "Find work" → `/jobs/find/`
2. Click job → `/jobs/<id>/` → proposal form (cover letter, rate, delivery days, attachment)
3. Submit → HTMX POST `/jobs/<id>/propose/` → green badge inline, no reload
4. Re-visit job → shows "Your proposal" status card

### Client manages proposals
1. Login → `/dashboard/` → Proposals tab → see all received proposals with freelancer names
2. Click Accept → HTMX POST `/proposals/<id>/accept/` → green badge, contract auto-created
3. Click Reject → HTMX POST `/proposals/<id>/reject/` → red badge

### Contract & milestone lifecycle
1. Accept proposal → Contract created (client `signed_by_client=True`)
2. Freelancer visits `/contracts/<id>/` → clicks "Sign contract"
3. Client adds milestone → HTMX POST → card appended inline
4. Freelancer submits deliverable → gold badge
5. Client approves → green badge, status=approved

### Mission Control
1. Login as `admin` → `/admin/`
2. Navigate tabs: Users / Jobs / Proposals / Contracts / Reviews / Payments / Moderation
3. Inline actions (Verify, Ban, Activate, Delete, Approve, Resolve) via HTMX, toast on complete
4. Non-superuser access → 403

# SuratPro Theme Conversion Rule

Use and convert the HTML theme from the root `html/` folder into Django Jinja templates.

## Mandatory Scope
- Convert theme pages from `html/` to `templates/pages/*.jinja`.
- Reuse shared shell in `templates/base.jinja`.
- Keep `templates/components/` for reusable UI blocks.
- Keep `templates/partials/` for HTMX fragments (`_*.jinja`).

## Page Mapping
- `html/index.html` -> `templates/pages/home.jinja`
- `html/login.html` -> `templates/pages/auth/login.jinja`
- `html/browse.html` -> `templates/pages/browse.jinja`
- `html/profile.html` -> `templates/pages/profile.jinja`
- `html/post-job.html` -> `templates/pages/post_job.jinja`
- `html/dashboard.html` -> `templates/pages/dashboard.jinja`
- `html/messages.html` -> `templates/pages/messages.jinja`
- `html/payments.html` -> `templates/pages/payments.jinja`
- `html/pricing.html` -> `templates/pages/pricing.jinja`
- `html/referral.html` -> `templates/pages/referral.jinja`

## Conversion Standards
- Do not keep static `.html` route links like `dashboard.html`; use Django `url(...)`.
- Replace mock JavaScript redirects/alerts with server-rendered flow.
- Use HTMX for interactions (`hx-get`, `hx-post`, `hx-target`, `hx-swap`).
- Return HTML partials (not JSON) for HTMX endpoints.
- Use Alpine.js only for UI state (tabs, modal, dropdown, toggle).
- Keep style consistent with existing `static/css/style.css` and Tailwind utility usage.

## Backend Coupling Rules
- Every converted page must map to a real Django view and URL.
- Forms must use Django forms with CSRF token.
- Views must stay thin; move business logic into `services.py` where needed.
- All tenant data must be filtered by `request.user`.

## Done Criteria (per page)
- Jinja page renders successfully.
- Nav/footer/base inheritance works.
- No broken `.html` links remain.
- HTMX actions work end-to-end with Django views.
- `python3 manage.py check` passes.

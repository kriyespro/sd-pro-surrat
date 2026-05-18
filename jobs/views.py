from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import json

from users.models import Category, Skill

from .forms import JobBasicsForm
from .models import Job
from .services import get_client_jobs, search_freelancers


def jobs_list(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("category", "").strip() or None
    qs = Job.objects.filter(status="active").select_related("client", "category").prefetch_related("skills").order_by("-created_at")
    if q:
        qs = qs.filter(title__icontains=q) | qs.filter(description__icontains=q)
    if cat:
        qs = qs.filter(category__name__iexact=cat)
    categories = Category.objects.all()
    return render(request, "pages/jobs_list.jinja", {
        "jobs": qs,
        "categories": categories,
        "selected_category": cat,
        "q": q,
    })


def browse(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("category", "").strip() or None
    freelancers = search_freelancers(q=q, category=cat)
    categories = Category.objects.all()
    freelancers_data = [
        {
            "id": fl.id,
            "username": fl.user.username,
            "name": fl.user.get_full_name() or fl.user.username,
            "initials": fl.user.initials,
            "title": fl.title or "Freelancer",
            "bio": fl.user.bio or "Top-rated professional from Surat.",
            "tags": [s.name for s in fl.skills.all()[:4]],
            "rate": float(fl.hourly_rate or 0),
            "rating": float(fl.avg_rating or 0),
            "reviews": int(fl.total_reviews or 0),
            "status": "online" if fl.availability == "available" else "busy",
            "cat": (fl.skills.first().category.name if fl.skills.exists() and fl.skills.first().category else "General"),
            "color1": "#0D6E6E",
            "color2": "#E8A830",
        }
        for fl in freelancers
    ]
    if request.headers.get("HX-Request"):
        return render(request, "partials/_freelancer_card.jinja", {"freelancers": freelancers})
    return render(request, "pages/browse.jinja", {
        "freelancers": freelancers,
        "categories": categories,
        "selected_category": cat,
        "q": q,
        "freelancers_data_json": json.dumps(freelancers_data),
        "category_names_json": json.dumps([c.name for c in categories]),
    })


@login_required
def post_job(request):
    if not request.user.is_client:
        return redirect("dashboard")
    from billing.services import can_post_job
    allowed, reason = can_post_job(request.user)
    if not allowed:
        return render(request, "pages/post_job.jinja", {"gate_error": reason})

    if request.method == "POST":
        # Accept JSON from Alpine.js fetch()
        content_type = request.content_type or ""
        if "application/json" in content_type:
            try:
                data = json.loads(request.body)
            except Exception:
                return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

            title = (data.get("title") or "").strip()
            description = (data.get("desc") or "").strip()
            if not title or not description:
                return JsonResponse({"ok": False, "error": "Title and description required"}, status=400)

            # Category lookup by name
            category = None
            cat_name = (data.get("category") or "").strip()
            if cat_name:
                category = Category.objects.filter(name__iexact=cat_name).first()

            # Experience level mapping
            exp_raw = (data.get("experience") or "mid").lower()
            exp_map = {"entry level": "entry", "entry": "entry", "mid level": "mid", "mid": "mid", "expert level": "expert", "expert": "expert"}
            experience_level = exp_map.get(exp_raw, "mid")

            job = Job.objects.create(
                client=request.user,
                title=title,
                description=description,
                category=category,
                pricing_type=data.get("pricingType", "fixed"),
                budget_min=data.get("budgetMin") or 0,
                budget_max=data.get("budgetMax") or 0,
                deadline=data.get("deadline") or None,
                experience_level=experience_level,
                visibility=data.get("visibility", "public"),
                status="active",
            )

            # Skills — match by name, create if missing
            for skill_name in (data.get("skills") or []):
                skill_name = skill_name.strip()
                if skill_name:
                    skill, _ = Skill.objects.get_or_create(name=skill_name)
                    job.skills.add(skill)

            return JsonResponse({"ok": True, "job_id": job.id, "redirect": f"/jobs/{job.id}/"})

        # Fallback: regular form POST
        form = JobBasicsForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.client = request.user
            job.status = "active"
            job.save()
            form.save_m2m()
            return redirect("job_detail", job_id=job.id)
        return render(request, "pages/post_job.jinja", {"form": form})

    return render(request, "pages/post_job.jinja", {})


@login_required
def client_jobs(request):
    jobs = get_client_jobs(request.user)
    return render(request, "partials/_job_card.jinja", {"jobs": jobs})


def job_detail(request, job_id):
    job = get_object_or_404(
        Job.objects.select_related("client", "category").prefetch_related("skills"),
        id=job_id,
    )
    job.views_count += 1
    job.save(update_fields=["views_count"])

    existing_proposal = None
    proposal_count = job.proposals.count()
    if request.user.is_authenticated and request.user.is_freelancer:
        existing_proposal = job.proposals.filter(freelancer=request.user).order_by("-id").first()

    return render(request, "pages/job_detail.jinja", {
        "job": job,
        "proposal_count": proposal_count,
        "existing_proposal": existing_proposal,
    })


def search_results(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("category", "").strip() or None
    freelancers = search_freelancers(q=q, category=cat)
    return render(request, "partials/_freelancer_card.jinja", {"freelancers": freelancers})


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    freelancers = search_freelancers(q="", category=category.name)
    return render(
        request,
        "pages/browse.jinja",
        {
            "freelancers": freelancers,
            "categories": Category.objects.all(),
            "selected_category": category.name,
            "q": "",
            "freelancers_data_json": "[]",
            "category_names_json": "[]",
        },
    )


@login_required
def propose_to_job(request, job_id):
    from proposals.models import Proposal
    from billing.services import can_submit_proposal, increment_bid_count

    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)
    job = get_object_or_404(Job, id=job_id)
    if not request.user.is_freelancer:
        return HttpResponse("Only freelancers can submit proposals.", status=403)
    allowed, reason = can_submit_proposal(request.user)
    if not allowed:
        return HttpResponse(f"<div class='sp-badge sp-badge-red'>{reason}</div>", status=403)
    attachment = request.FILES.get("attachment")
    proposal = Proposal.objects.filter(job=job, freelancer=request.user).order_by("-id").first()
    if proposal:
        proposal.cover_letter = request.POST.get("cover_letter", proposal.cover_letter or "Interested in this project.")
        proposal.proposed_rate = request.POST.get("proposed_rate") or proposal.proposed_rate or job.budget_min or 1000
        proposal.delivery_days = request.POST.get("delivery_days") or proposal.delivery_days or 7
        proposal.status = "pending"
        if attachment:
            proposal.attachment = attachment
        proposal.save()
    else:
        Proposal.objects.create(
            job=job,
            freelancer=request.user,
            cover_letter=request.POST.get("cover_letter", "Interested in this project."),
            proposed_rate=request.POST.get("proposed_rate") or job.budget_min or 1000,
            delivery_days=request.POST.get("delivery_days") or 7,
            attachment=attachment,
            status="pending",
        )
    increment_bid_count(request.user)
    return HttpResponse("<div class='sp-badge sp-badge-green'>Proposal submitted</div>")


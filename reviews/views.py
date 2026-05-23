from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from contracts.models import Contract
from users.models import User

from .models import Review


@login_required
def review_list(request):
    reviews = Review.objects.filter(reviewee=request.user)
    return render(request, "partials/_review_card.jinja", {"reviews": reviews})


@require_POST
@login_required
def leave_review(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if request.user not in [contract.client, contract.freelancer]:
        return HttpResponse("Forbidden", status=403)
    reviewee = contract.freelancer if request.user == contract.client else contract.client
    Review.objects.get_or_create(
        contract=contract,
        reviewer=request.user,
        reviewee=reviewee,
        defaults={
            "rating": int(request.POST.get("rating") or 5),
            "feedback": request.POST.get("feedback", "Great work."),
            "is_public": True,
            "is_approved": True,
        },
    )
    return HttpResponse("<div class='sp-badge sp-badge-green'>Review submitted</div>")


def user_reviews(request, username):
    user = get_object_or_404(User, username=username)
    reviews = Review.objects.filter(reviewee=user)
    return render(request, "partials/_review_card.jinja", {"reviews": reviews})

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
import json
from decimal import Decimal

from contracts.models import Contract, Milestone

from .models import Dispute, Wallet, Transaction


@login_required
def payments_page(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    transactions = Transaction.objects.filter(wallet=wallet)[:20]
    tx_rows = []
    for tx in transactions:
        if tx.type == "release":
            icon, bg, badge = "✅", "rgba(62,202,143,0.12)", "green"
            label = "Released"
        elif tx.type == "refund":
            icon, bg, badge = "↩", "rgba(232,93,4,0.1)", "red"
            label = "Refunded"
        elif tx.type == "topup":
            icon, bg, badge = "💳", "rgba(232,168,48,0.1)", "gold"
            label = "Escrow"
        else:
            icon, bg, badge = "🔒", "rgba(13,110,110,0.15)", "gold"
            label = "Escrow"
        sign = "+" if tx.type in ("topup", "refund") else "-"
        tx_rows.append(
            {
                "id": tx.id,
                "icon": icon,
                "bg": bg,
                "title": f"{tx.type.title()} transaction",
                "sub": tx.ref_id or "SuratPro transaction",
                "amount": f"{sign}₹{tx.amount}",
                "type": label,
                "badge": badge,
            }
        )
    return render(
        request,
        "pages/payments.jinja",
        {"wallet": wallet, "transactions_json": json.dumps(tx_rows)},
    )


@login_required
def add_funds(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    amount = Decimal(str(request.POST.get("amount") or "1000"))
    wallet.balance += amount
    wallet.save(update_fields=["balance"])
    Transaction.objects.create(wallet=wallet, type="topup", amount=amount, status="success", ref_id="manual-topup")
    return HttpResponse("<div class='sp-badge sp-badge-green'>Funds added</div>")


@login_required
def razorpay_callback(request):
    return HttpResponse("<div class='sp-badge sp-badge-green'>Payment callback received</div>")


@login_required
def release_funds(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    wallet, _ = Wallet.objects.get_or_create(user=milestone.contract.client)
    Transaction.objects.create(
        wallet=wallet,
        type="release",
        amount=milestone.amount,
        status="success",
        milestone=milestone,
        contract=milestone.contract,
        ref_id=f"release-{milestone.id}",
    )
    milestone.status = "released"
    milestone.save(update_fields=["status"])
    return HttpResponse("<div class='sp-badge sp-badge-green'>Funds released</div>")


@login_required
def transaction_list(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    transactions = Transaction.objects.filter(wallet=wallet).order_by("-created_at")[:25]
    return render(request, "partials/_transaction_row.jinja", {"transactions": transactions})


@login_required
def dispute_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    Dispute.objects.get_or_create(
        contract=contract,
        raised_by=request.user,
        defaults={"reason": request.POST.get("reason", "Payment dispute"), "status": "open"},
    )
    return HttpResponse("<div class='sp-badge sp-badge-red'>Dispute created</div>")


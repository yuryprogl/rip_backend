from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import Element, Calculation, ElementCalculation


def index(request):
    element_name = request.GET.get("element_name", "")
    elements = Element.objects.filter(status=1)

    if element_name:
        elements = elements.filter(name__icontains=element_name)

    context = {
        "element_name": element_name,
        "elements": elements
    }

    draft_calculation = get_draft_calculation()
    if draft_calculation:
        context["elements_count"] = len(draft_calculation.get_elements())
        context["draft_calculation"] = draft_calculation

    return render(request, "elements_page.html", context)


def element_page(request, element_id):
    context = {
        "element": Element.objects.get(id=element_id)
    }

    return render(request, "element_page.html", context)


def calculation_page(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return render(request, "404.html")

    calculation = Calculation.objects.get(id=calculation_id)
    if calculation.status == 5:
        return render(request, "404.html")

    context = {
        "calculation": calculation,
    }

    return render(request, "calculation_page.html", context)


def add_element_to_draft_calculation(request, element_id):
    element_name = request.POST.get("element_name")
    redirect_url = f"/?element_name={element_name}" if element_name else "/"

    draft_calculation = get_draft_calculation()
    if draft_calculation is None:
        draft_calculation = Calculation.objects.create()
        draft_calculation.owner = get_current_user()
        draft_calculation.date_created = timezone.now()
        draft_calculation.save()

    element = Element.objects.get(pk=element_id)
    if ElementCalculation.objects.filter(calculation=draft_calculation, element=element).exists():
        return redirect(redirect_url)

    item = ElementCalculation(
        calculation=draft_calculation,
        element=element
    )
    item.save()

    return redirect(redirect_url)


def delete_calculation(request, calculation_id):
    if not Calculation.objects.filter(pk=calculation_id).exists():
        return redirect("/")

    with connection.cursor() as cursor:
        cursor.execute("UPDATE calculations SET status=5 WHERE id = %s", [calculation_id])

    return redirect("/")


def get_draft_calculation():
    return Calculation.objects.filter(status=1).first()


def get_current_user():
    return User.objects.filter(is_superuser=False).first()
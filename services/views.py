from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import (
    BirthChartRequestForm,
    WitchQuestionForm,
    RitualRequestForm,
    DreamSubmissionForm,
    MediumContactForm
)
from .models import (
    BirthChartRequest, WitchQuestion,
    RitualRequest, DreamSubmission,
    MediumContactRequest
)




def services_home(request):
    if request.method == 'POST':
        if 'birth_chart_submit' in request.POST:
            form = BirthChartRequestForm(request.POST)
            if form.is_valid():
                instance = form.save()
                return redirect('add_service_to_cart', service_type='birthchart', object_id=instance.id)

                
        elif 'witch_question_submit' in request.POST:
            form = WitchQuestionForm(request.POST)
            if form.is_valid():
                instance = form.save()
                return redirect('add_service_to_cart', service_type='witch', object_id=instance.id)

        elif 'ritual_request_submit' in request.POST:
            form = RitualRequestForm(request.POST)
            if form.is_valid():
                instance = form.save()
                return redirect('add_service_to_cart', service_type='ritual', object_id=instance.id)

        elif 'dream_submit' in request.POST:
            form = DreamSubmissionForm(request.POST)
            if form.is_valid():
                instance = form.save()
                return redirect('add_service_to_cart', service_type='dream', object_id=instance.id)

        elif 'medium_contact_submit' in request.POST:
            form = MediumContactForm(request.POST)
            if form.is_valid():
                instance = form.save()
                return redirect('add_service_to_cart', service_type='medium', object_id=instance.id)


    context = {
        'birth_form': BirthChartRequestForm(),
        'witch_form': WitchQuestionForm(),
        'ritual_form': RitualRequestForm(),
        'dream_form': DreamSubmissionForm(),
        'medium_form': MediumContactForm(),
        'birth_chart_price': 60,
        'ask_a_witch_price': 45,
        'ritual_request_price': 60,
        'dream_interpretation_price': 50,
        'medium_contact_price': 100,
    }
    return render(request, 'services/services.html', context)


# Map service type slugs to actual models
SERVICE_MODELS = {
    'birthchart': BirthChartRequest,
    'witch': WitchQuestion,
    'ritual': RitualRequest,
    'dream': DreamSubmission,
    'medium': MediumContactRequest,
}

def add_service_to_cart(request, service_type, object_id):
    model = SERVICE_MODELS.get(service_type)

    if not model:
        return redirect('services_home')

    service = get_object_or_404(model, id=object_id)

    cart = request.session.get('cart', {})
    key = f"service-{service_type}-{object_id}"

    cart[key] = {
        'name': str(service),
        'price': float(service.price),
        'quantity': 1,
        'type': service_type,
        'service_id': object_id,
    }

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')  # or use a thank you page if you prefer

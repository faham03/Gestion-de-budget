import csv

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import ExpenseForm, ProfileForm, CustomUserCreationForm
from .models import Expense, Profile


@login_required
def index(request):
    month = request.GET.get('month')
    qs = Expense.objects.all()
    if month:
        qs = qs.filter(date__startswith=month)
    total_by_cat = qs.values('category').annotate(total=Sum('amount'))

    context = {
        'expenses': qs.order_by('-date'),
        'form': ExpenseForm(),
        'total_by_cat': total_by_cat,
        'filter_month': month or ''
    }
    return render(request, 'expenses/index.html', context)


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('expenses:index')


@login_required
def delete_expense(request, pk):
    exp = get_object_or_404(Expense, pk=pk)
    exp.delete()
    return redirect('expenses:index')


@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expenses:index')
    else:
        form = ExpenseForm(instance=expense)

    context = {
        'form': form,
        'expense': expense,
        'filter_month': request.GET.get('month', '')
    }
    return render(request, 'expenses/edit.html', context)


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # crée l'utilisateur mais ne l'active pas tout de suite
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.is_active = False
            user.save()

            # envoi du mail d’activation
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = request.build_absolute_uri(
                reverse('activate', kwargs={'uidb64': uid, 'token': token})
            )

            subject = 'Activez votre compte'
            message = render_to_string('registration/activation_email.html', {
                'user': user,
                'activation_link': activation_link,
                'domain': current_site.domain,
            })
            send_mail(subject, message, None, [user.email])

            return render(request, 'registration/activation_sent.html')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'registration/activation_complete.html')
    else:
        return render(request, 'registration/activation_invalid.html')


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'expenses/profile.html', {'profile': profile})


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('expenses:profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'expenses/profile_edit.html', {'form': form})


@login_required
def export_csv(request):
    month = request.GET.get('month')
    qs = Expense.objects.all().order_by('-date')
    if month:
        qs = qs.filter(date__startswith=month)

    response = HttpResponse(content_type='text/csv')
    filename = 'expenses'
    if month:
        filename += f'_{month}'
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Description', 'Catégorie', 'Montant (€)'])
    for e in qs:
        writer.writerow([e.date, e.description, e.category, f"{e.amount:.2f}"])

    return response
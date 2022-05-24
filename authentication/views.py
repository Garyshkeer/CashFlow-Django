import calendar
from datetime import datetime
from multiprocessing import context
from pyexpat import model
from re import template
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from .form import UserUpdateForm, ProfileUpdateForm, ContactsForm, BankCardForm
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic import ListView
from django.db.models import Avg, Count, Min, ProtectedError, Sum, CharField, Value

from .models import BankCard, Category, Inflow, Outflow
from django.db.models import DateTimeField
from django.db.models.functions import Trunc


# Create your views here.

def home(request):
    return render(request, "authentication/baseFront.html")


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        f_name = request.POST['f_name']
        s_name = request.POST['s_name']
        email = request.POST['email']
        password = request.POST['password']
        c_password = request.POST['c_password']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist")
            return redirect('signup')

        if User.objects.filter(email=email):
            messages.error(request, "Email address already exist")
            return redirect('signup')

        if password != c_password:
            messages.error(request, "Passwords didn't match")

        else:
            myUser = User.objects.create_user(username, email, password)
            myUser.first_name = f_name
            myUser.last_name = s_name
            myUser.email = email
            myUser.save()
            messages.success(request, "Your account has been successfully created")
            return redirect('signin')
    return render(request, "authentication/signup.html")


def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            f_name = user.first_name
            return render(request, "authentication/profile.html", {'f_name': f_name})
        else:
            messages.error(request, "Bad Credentials!")
            return redirect('signin')

    return render(request, "authentication/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('home')


def features(request):
    return render(request, "authentication/features.html")


def contacts(request):
    error = ' '
    if request.method == 'POST':
        form = ContactsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact')
        else:
            error = 'form is incorrect'

    form = ContactsForm()
    contacts = {
        'form': form,
        'error': error
    }
    return render(request, "authentication/contactuspage.html", contacts)


def why(request):
    return render(request, "authentication/whycashflow.html")


def profile(request):
    model = BankCard.objects.all()
    inflow = Inflow.objects.all()
    outflow = Outflow.objects.all()

    all_balance = 0
    inflow_balance = 0
    outflow_balance = 0
    for i in inflow:
        inflow_balance += i.value
    for i in outflow:
        outflow_balance += i.value
    for i in model:
        all_balance += i.cardBalance
    inflow.order_by(Trunc('registered_at', 'date', output_field=DateTimeField()).desc(), '-value')
    outflow.order_by(Trunc('registered_at', 'date', output_field=DateTimeField()).desc(), '-value')
    all_balance += (inflow_balance - outflow_balance)
    tenge = (all_balance)

    dollar = int(tenge / 434)
    ruble = int(tenge / 15)
    if len(outflow) >= 3 and len(inflow) >= 3:
        return render(request, "authentication/profile.html", {
            'tenge': int(tenge),
            'dollar': dollar,
            'ruble': ruble,
            'inflow': inflow[len(inflow) - 3:],
            'outflow': outflow[len(outflow) - 3:]
        })
    elif len(inflow) >= 3:
        return render(request, "authentication/profile.html", {
            'tenge': int(tenge),
            'dollar': dollar,
            'ruble': ruble,
            'inflow': inflow[len(inflow) - 3:],
            'outflow': outflow
        })
    elif len(outflow) >= 3:
        return render(request, "authentication/profile.html", {
            'tenge': int(tenge),
            'dollar': dollar,
            'ruble': ruble,
            'inflow': inflow,
            'outflow': outflow[len(inflow) - 3:]
        })
    else:
        return render(request, "authentication/profile.html", {
            'tenge': int(tenge),
            'dollar': dollar,
            'ruble': ruble,
            'inflow': inflow,
            'outflow': outflow
        })


# class AddNewBankCard(CreateView):
#     model = BankCard
#     form_class = BankCardForm
#     template_name = 'authentication/addnewbankcard.html'

def addNewBankCard(request):
    if request.method == "POST":
        form = BankCardForm(request.POST)
        if form.is_valid():
            card_name = form.cleaned_data.get('cardName')
            card_balance = form.cleaned_data.get('cardBalance')
            # transaction_date = form.cleaned_data.get('date')

            model = BankCard.objects.filter(cardName=card_name)
            # model = BankCard.objects.filter(date=transaction_date)


            new_balance = model[0].cardBalance + card_balance
            model.update(cardBalance=new_balance)

            return redirect('account')

    else:
        form = BankCardForm()

    context = {
        'form': form
    }
    return render(request, "authentication/addnewbankcard.html", context)


# class AddBankName(CreateView):
#     model = Category  
#     template_name = 'authentication/addbankname.html'
#     fields = '__all__'

def addBankName(request):
    if request.method == "POST":
        card_name = request.POST["name"]

        model = BankCard(cardName=card_name, cardBalance=0)
        model.save()
        return redirect('bankcard')
    return render(request, "authentication/addbankname.html")


class AccountListView(ListView):
    model = BankCard
    context_object_name = 'account_list'
    template_name = 'authentication/account.html'


@login_required
def edit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, "authentication/edit.html", context)


@login_required
def inflow_edit(request, pk):
    try:
        categories = None
        registered_by = request.user.get_username()
        categories = Category.objects.filter(
            registered_by__iexact=request.user.get_username()
        )
        inflow = get_object_or_404(
            Inflow,
            pk=pk,
            registered_by=registered_by
        )
    except Inflow.DoesNotExist as e:
        raise Http404('Inflow does not exist')
    except Http404 as e:
        return HttpResponse('404')
    return render(
        request,
        'authentication/inflow_edit.html',
        {
            'inflow': inflow,
            'categories': categories,
        }
    )





@login_required
def inflow_update(request, pk):
    try:
        registered_by = request.user.get_username()
        inflow = Inflow.objects.filter(
            pk=pk,
            registered_by=registered_by
        )
        category = Category.objects.filter(
            registered_by__iexact=request.user.username,
            id__iexact=request.POST['categories']
        )[0]
        if len(inflow) != 0:
            updatein = Inflow.objects.filter(
                pk=pk,
                registered_by=registered_by
            ).update(
                name=request.POST['name'],
                value=request.POST['value'],
                category=category
            )
        else:
            return HttpResponse('Inflow not found.')
    except ProtectedError as exc:
        messages.error(
            request,
            "Cannot delete some instances of model, because they are referenced through protected foreign keys."
        )
    except Http404 as e:
        raise HttpResponse('404' + str(e))
    return redirect('inflow_list')


@login_required
def inflow_create(request):
    categories = None
    no_categories = False
    try:
        categories = Category.objects.filter(
            registered_by__iexact=request.user.username
        )
        if categories.count() == 0:
            no_categories = True
    except Exception as exc:
        messages.error(request, 'error')
    return render(
        request,
        'authentication/inflow_create.html',
        {
            'messages': messages,
            'categories': categories,
            'no_categories': no_categories,
        }
    )


@login_required
def inflow_save(request):
    try:
        if request.POST:
            category = Category.objects.filter(
                registered_by__iexact=request.user.username,
                id__iexact=request.POST['categories']
            )[0]

            inflow = Inflow()
            inflow.name = request.POST['name']
            inflow.category = category
            inflow.registered_at = request.POST['reg_date']
            inflow.registered_by = request.user.username
            inflow.value = request.POST['value']
            inflow.save()

            messages.success(request, "A new inflow was created!")
    except Exception as exc:
        messages.error(request, 'An error has occurred' + str(exc))
        return redirect('inflow_list')
    return redirect('inflow_list')


@login_required
def inflow_list(request):
    try:

        template_name = 'inflow_list.html'
        str_date = get_first_day_month()
        registered_by = request.user.get_username()
        print(str_date)
        inflows = Inflow.objects.filter(
            registered_at__gte=str_date,
            registered_by=registered_by
        )
    except Inflow.DoesNotExist as e:
        raise Http404('Inflow does not exist')
    except Http404 as exc:
        return HttpResponse('404')
    return render(
        request,
        'authentication/inflow_list.html',
        {
            'inflows': inflows
        }
    )


@login_required
def inflow_detail(request, pk):
    try:
        registered_by = request.user.get_username()
        inflow = get_object_or_404(
            Inflow,
            pk=pk,
            registered_by=registered_by
        )
    except Inflow.DoesNotExist as exc:
        raise Http404('Inflow does not exist')
    except Http404 as exc:
        return HttpResponse('404')
    return render(request, 'authentication/inflow_detail.html', {'inflow': inflow})


def get_first_day_month():
    date = None

    try:
        month = timezone.now().month
        if len(str(month)) == 1:
            month = int('0' + str(month))

        year = timezone.now().year
        month_range = calendar.monthrange(year, int(month))
        day = month_range[1] - (month_range[1] - 1)
        date = datetime(year, month, day)

    except ValueError as exc:
        print(exc, "ValueError")
    except TypeError as exc:
        print(exc, "TypeError")
    return date


def get_my_current_balance():
    balance = 0.00
    inflow_amount = 0.00
    outflow_amount = 0.00

    try:

        first_day = get_first_day_month()

        inflow_amount_on_this_month = Inflow.objects.filter(
            registered_at__gt=first_day
        ).aggregate(
            amount=Sum('value')
        )

        outflow_amount_on_this_month = Outflow.objects.filter(
            registered_at__gt=first_day
        ).aggregate(
            amount=Sum('value')
        )

        inflow_amount = inflow_amount_on_this_month['amount']
        outflow_amount = outflow_amount_on_this_month['amount']
        balance = inflow_amount - outflow_amount

    except ValueError as exc:
        print(exc, "Wow, An ValueError was occurred")
    except TypeError as exc:
        print(exc, "Wow, An TypeError was occurred")
    return balance, inflow_amount, outflow_amount


@login_required
def category_update(request, pk):
    try:
        code = request.POST['code']
        name = request.POST['name']
        description = request.POST['description']
        registered_at = request.POST['reg_date']
        registered_by = request.user.get_username()

        category = Category.objects.filter(
            pk=pk,
            registered_by=request.user.get_username()
        ).update(
            code=code,
            name=name,
            description=description,
            registered_at=registered_at,
            registered_by=registered_by
        )

        messages.success(request, "Category was updated!")
    except Exception as exc:
        messages.error(request, 'An error was occurred.')
    return redirect("category_detail/" + str(pk))


def category_edit(request, pk):
    try:
        category = get_object_or_404(
            Category,
            pk=pk,
            registered_by=request.user.get_username()
        )
    except Category.DoesNotExist as e:
        raise Http404('Category does not exist')
    except Http404 as e:
        return HttpResponse('404')
    return render(
        request,
        'authentication/category_edit.html',
        {
            'category': category,
        }
    )


def category_detail(request, pk):
    try:
        category = get_object_or_404(
            Category,
            pk=pk,
            registered_by=request.user.get_username()
        )
    except Category.DoesNotExist as exc:
        raise Http404('Category does not exist')
    except Http404 as exc:
        return HttpResponse('404')
    return render(request, 'authentication/category_detail.html', {'category': category})


def category_list(request):
    try:
        categories_inflow_count = 0
        categories_outflow_count = 0

        categories = Category.objects.filter(
            registered_by=request.user.get_username()
        )
        for category in categories:
            categories_inflow = Inflow.objects.filter(
                registered_by=request.user.get_username(),
                category=category
            )
            categories_outflow = Outflow.objects.filter(
                registered_by=request.user.get_username(),
                category=category
            )

            if categories_inflow:
                categories_inflow_count += categories_inflow.count()

            if categories_outflow:
                categories_outflow_count += categories_outflow.count()

    except Category.DoesNotExist as e:
        raise Http404('Category does not exist')
    except Http404 as exc:
        return HttpResponse('404')
    return render(
        request,
        'authentication/category_list.html',
        {
            'categories': categories,
            'categories_inflow': categories_inflow_count,
            'categories_outflow': categories_outflow_count,
        }
    )


def category_save(request):
    try:
        if request.POST:
            category = Category()
            category.code = request.POST['code']
            category.name = request.POST['name']
            category.description = request.POST['description']
            category.registered_at = request.POST['reg_date']
            category.registered_by = request.user.username
            category.save()

            messages.success(request, "A new category was created!")
    except Exception as exc:
        print(exc)
        messages.error(request, 'An error has occurred' + str(exc))
        return redirect('authentication/category_list')
    return redirect('category_list')


def category_create(request):
    try:
        template_name = "category_create"
    except Exception as exc:
        messages.error(request, 'error')
    return render(
        request, 'authentication/category_create.html',
    )


@login_required
def outflow_update(request, pk):
    try:
        registered_by = request.user.get_username()
        inflow = Outflow.objects.filter(
            pk=pk,
            registered_by=registered_by
        )
        category = Category.objects.filter(
            registered_by__iexact=request.user.username,
            id__iexact=request.POST['categories']
        )[0]
        if len(inflow) != 0:
            updatein = Outflow.objects.filter(
                pk=pk,
                registered_by=registered_by
            ).update(
                name=request.POST['name'],
                value=request.POST['value'],
                category=category
            )
        else:
            return HttpResponse('Inflow not found.')
    except ProtectedError as exc:
        messages.error(
            request,
            "Cannot delete some instances of model, because they are referenced through protected foreign keys."
        )
    except Http404 as e:
        raise HttpResponse('404' + str(e))
    return redirect('inflow_list')


def outflow_edit(request, pk):
    try:
        categories = None
        registered_by = request.user.get_username()
        categories = Category.objects.filter(
            registered_by__iexact=request.user.get_username()
        )
        outflow = get_object_or_404(
            Outflow, pk=pk,
            registered_by=registered_by
        )
    except Outflow.DoesNotExist as e:
        raise Http404('Outflow does not exist')
    except Http404 as e:
        return HttpResponse('404')
    return render(
        request,
        'authentication/outflow_edit.html',
        {
            'outflow': outflow,
            'categories': categories,
        }
    )


def outflow_detail(request, pk):
    try:
        registered_by = request.user.get_username()
        outflow = get_object_or_404(
            Outflow, pk=pk,
            registered_by=registered_by
        )
    except Outflow.DoesNotExist as exc:
        raise Http404('Outflow does not exist')
    except Http404 as exc:
        return HttpResponse('404')
    return render(request, 'authentication/outflow_detail.html', {'outflow': outflow})


def outflow_list(request):
    try:
        template_name = 'authentication/outflow_list.html'
        str_date = get_first_day_month()
        registered_by = request.user.get_username()

        outflows = Outflow.objects.filter(
            registered_at__gte=str(str_date),
            registered_by=registered_by
        )
    except Outflow.DoesNotExist as e:
        raise Http404('Outflow does not exist')
    except Http404 as exc:
        return HttpResponse('404')
    return render(request, 'authentication/outflow_list.html', {'outflows': outflows})


def outflow_save(request):
    try:
        if request.POST:
            category = Category.objects.filter(
                registered_by__iexact=request.user.username,
                id__iexact=request.POST['categories']
            )[0]

            outflow = Outflow()
            outflow.name = request.POST['name']
            outflow.category = category
            outflow.registered_at = request.POST['reg_date']
            outflow.registered_by = request.user.username
            outflow.value = request.POST['value']
            outflow.save()

            messages.success(request, "A new outflow was created!")
    except Exception as exc:
        messages.error(request, 'Occurred an error' + str(exc))
        return redirect('outflow_list')
    return redirect('outflow_list')


def outflow_create(request):
    categories = None
    no_categories = False
    try:
        categories = Category.objects.filter(
            registered_by__iexact=request.user.username)
        if categories.count() == 0:
            no_categories = True
    except Exception as exc:
        messages.error(request, 'erro')
    return render(
        request,
        'authentication/outflow_create.html',
        {
            'messages': messages,
            'categories': categories,
            'no_categories': no_categories,
        }
    )

class DeleteAccountView(DeleteView):
    model = BankCard
    template_name = 'authentication/delete_account.html'
    success_url = reverse_lazy('account')


def outflow_delete(request, pk):
    try:
        registered_by = request.user.get_username()
        outflow = Outflow.objects.filter(
            pk=pk,
            registered_by=registered_by
        )
        if len(outflow) > 0:
            was_deleted = Outflow.objects.filter(
                pk=pk,
                registered_by=registered_by
            ).delete()
            if was_deleted:
                messages.success(request, 'Outflow was deleted!')
                return redirect('outflow_list')
            else:
                messages.error(request, 'An error was ocurred!')
                return redirect('outflow_list')
        else:
            return HttpResponse('Outflow not found.')
    except Http404 as e:
        raise HttpResponse('404' + str(e))
    return redirect('outflow_list')


def category_delete(request, pk):
    try:
        category = Category.objects.filter(
            pk=pk,
            registered_by=request.user.get_username()
        )
        if len(category) > 0:
            was_deleted = Category.objects.filter(
                pk=pk,
                registered_by=request.user.get_username()
            ).delete()
            if was_deleted:
                messages.success(request, 'Category was deleted!')
                return redirect('category_list')
            else:
                messages.error(request, 'An error was occurred!')
                return redirect('category_list')
        else:
            return HttpResponse('Category not found.')
    except ProtectedError as exc:
        messages.error(
            request,
            "Cannot delete some instances of model, because they are referenced through protected foreign keys."
        )
    except Http404 as e:
        raise HttpResponse('404' + str(e))
    return redirect('category_list')



@login_required
def inflow_delete(request, pk):
    try:
        registered_by = request.user.get_username()
        inflow = Inflow.objects.filter(
            pk=pk,
            registered_by=registered_by
        )
        if len(inflow) != 0:
            was_deleted = Inflow.objects.filter(
                pk=pk,
                registered_by=registered_by
            ).delete()
            if was_deleted:
                messages.success(request, 'Inflow was deleted!')
                return redirect('inflow_list')
            else:
                messages.error(request, 'An error was occurred!')
                return redirect('inflow_list')
        else:
            return HttpResponse('Inflow not found.')
    except ProtectedError as exc:
        messages.error(
            request,
            "Cannot delete some instances of model, because they are referenced through protected foreign keys."
        )
    except Http404 as e:
        raise HttpResponse('404' + str(e))
    return redirect('inflow_list')
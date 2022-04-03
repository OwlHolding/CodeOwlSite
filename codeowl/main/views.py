from email import message
from inspect import trace
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, FileResponse, HttpResponseForbidden
from .forms import UserForm, LoginForm
from django.contrib.auth.models import User
from .models import UserUpgrade, BlockedList
from django.contrib import auth
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from ipware import get_client_ip
import json
import uuid
from datetime import datetime
import io

from .Parser import parse
from .Classifier import AuroraPredictor
from .PreEngine import scan

from .neuralengine import generate, init, lock
init()


# Attention, enabling this parameter may lead to a decrease in performance
FIREWALL_ACTIVE = True


def firewall(request):
    if FIREWALL_ACTIVE:
        print("Firewall log:")
        client_ip, is_routable = get_client_ip(request)
        if client_ip is None:
            print("Не удалось получить IP-адрес клиента")
        else:
            print("IP-адрес:", client_ip)
            for model in BlockedList.objects.all():
                ips = model.ips.split()
                for ip in ips:
                    if client_ip == ip:
                        print("Доступ закрыт")
                        raise PermissionError("Тех-обслуживание")
            else:
                print("Доступ разрешен")


def main_page(request):
    firewall(request)
    return render(request, 'main/index.html')


def about(request):
    firewall(request)
    return render(request, 'main/about.html')


def profile(request):
    firewall(request)
    for model in UserUpgrade.objects.all():
        if model.user == request.user:
            message = "" if model.email_confirmed else "Пожалуйста, подтвердите Вашу почту"
            return render(request, 'main/profile.html',
                          {'message': message, 'counter': model.counter, "token": model.token})
    else:
        message = "Error"
    return render(request, 'main/profile.html', {'message': message, 'counter': -1})


def registration(request):
    firewall(request)
    if request.user.is_authenticated:
        return HttpResponseRedirect("/accounts/profile/")
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            password = form.cleaned_data.get("password")
            mail = form.cleaned_data.get("mail")
            for user in User.objects.all():
                if user.username == name:
                    error = "Данное имя пользователя уже используется"
                    return render(request, 'main/reg.html', {'form': form, 'error': error})
                if user.email == mail:
                    error = "Данная почта уже используется"
                    return render(request, 'main/reg.html', {'form': form, 'error': error})
            user = User.objects.create_user(name, mail, password)
            user.save()
            auth.login(request, user)
            for model in UserUpgrade.objects.all():
                if user == model.user:
                    url = "http://" + request.get_host() + '/confirm/' + str(model.token) + "/"
                    text = render_to_string('main/mail.html', {"url": url})
                    send_mail('Подтверждение почты', text, settings.EMAIL_HOST_USER, [user.email])
        return HttpResponseRedirect('/accounts/profile/')
    else:
        form = UserForm()
        error = ''
    return render(request, 'main/reg.html', {'form': form, 'error': error})


def change_password(request):
    firewall(request)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            auth.update_session_auth_hash(request, user)
            return redirect('/')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'main/change_password.html', {'form': form})


def price(request):
    firewall(request)
    return render(request, 'main/price.html')


def confirm(request, token):
    firewall(request)
    for model in UserUpgrade.objects.all():
        if model.token == token:
            model.email_confirmed = True
            model.save()
    return HttpResponseRedirect('/')


def login(request):
    firewall(request)
    errors = ""
    if request.user.is_authenticated:
        return HttpResponseRedirect("/accounts/profile/")
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(request, username=form.cleaned_data.get("name"),
                                     password=form.cleaned_data.get("password"))
            if user is not None:
                auth.login(request, user)
                return HttpResponseRedirect("/accounts/profile/")
            else:
                errors = "Authorization failed, incorrect username or password"
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {"form": form, "errors": errors})


def callnn(code, traceback):
    with lock:
        req = f'Error: {traceback} Answer:'
        return generate(req)[16 + len(traceback):]


def callpre(code, traceback):
    answer = scan(code)
    if "Unable to import" in answer:
        return callnn(code, traceback)
    else:
        return answer


def solve(code, traceback):
    traceback = parse(traceback)
    classifier = AuroraPredictor(
        '$local/static/classifier/templates',
        '$local/static/classifier/solutions')
    solution = classifier.predict(traceback)
    if solution:
        return solution
    return callsandbox(code, traceback)


@csrf_exempt
def api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        users = UserUpgrade.objects.filter(token=data.get('token', ''))
        if len(users):
            user = users[0]
            if not user.email_confirmed:
                return HttpResponseForbidden("<h2>Mail not confirmed</h2>")
            if user.counter > 0 or user.counter == -1:
                traceback = data.get('traceback', '')
                code = data.get('code', '')
                if traceback and code:
                    answer = solve(code, traceback)
                    return render(request, "main/answer.html",
                                  {"answer": answer,
                                   "counter": "Requests left: " + str(user.counter) if user.counter > 0 else ''})

                else:
                    return render(request, "main/error.html")
            else:
                return HttpResponseForbidden(
                    "<h3>You have reached the request limit</h3>")
        else:
            return HttpResponseForbidden(
                "<h3>Authentication failed. Please check your token</h3>")
    else:
        return HttpResponse("<h2>Method is not allowed</h2>")


@csrf_exempt
def val(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        users = UserUpgrade.objects.filter(token=data.get('token', ''))
        if len(users):
            return HttpResponse("Ok")
        else:
            return HttpResponseForbidden("<h3>Authentication failed. Please check your token</h3>")
    else:
        return HttpResponse("<h2>Method is not allowed</h2>")


def file_download(request):
    user = UserUpgrade.objects.filter(user=request.user)[0]
    file = io.BytesIO(user.token.encode("utf-8"))
    file.name = "codeowl"
    return FileResponse(file)

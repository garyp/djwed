# Create your views here.

import django.contrib.auth 
from django.contrib.auth.models import User, check_password
from django import forms
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django import forms
from djwed.wedding.email import email_invite_code
from djwed.wedding.models import Invitee, Guest
from djwed.wedding.settings import *
from datetime import datetime

def user_to_invitee(user):
    return Invitee.objects.get(id=int(user.username[len(username_prefix):]))

def token_to_invitee(token):
    return Invitee.objects.get(invite_code__exact=token.upper())

class InviteeAuthBackend:

    def authenticate(self, token=None):
        try:
            inv = token_to_invitee(token)
        except Invitee.DoesNotExist:
            return None
        user = inv.user()
        user.backend = "djwed.wedding.auth.InviteeAuthBackend"
        return user

    def get_user(self, user_id):
        try:
            u = User.objects.get(pk=user_id)
            if u.username[0:len(username_prefix)] == username_prefix:
                return u
            else:
                return None
        except User.DoesNotExist:
            return None


class LoginForm(forms.Form):
    token = forms.CharField(max_length=10)

    def clean_token(self):
        token = self.cleaned_data['token']
        try:
            inv = token_to_invitee(token)
        except Invitee.DoesNotExist:
            raise forms.ValidationError(u'Invalid login token')
        return inv


class ReminderForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            guest = Guest.objects.get(email=email)
        except Guest.DoesNotExist:
            raise forms.ValidationError(u'No guest found with this email address')
        return guest


def rsvp_logout(request):
    logout(request)
    return HttpResponseRedirect('/rsvp/')

def rsvp_login(request):
    next = ''
    if request.REQUEST.has_key('next'):
        next = request.REQUEST['next']
    if request.method == 'POST': 
        if 'login' in request.POST:
            form = LoginForm(request.POST, prefix='login')
            if form.is_valid():
                inv = form.cleaned_data['token']
                inv.last_visited = datetime.now()
                inv.save()
                u = inv.user()
                u.backend = "djwed.wedding.auth.InviteeAuthBackend"
                login(request, u)
                if next:
                    return HttpResponseRedirect(next) # Redirect after POST
                else:
                    return HttpResponseRedirect('/rsvp/') # Redirect after POST
            else:
                reminder_form = ReminderForm(prefix='reminder')
        elif 'reminder' in request.POST:
            reminder_form = ReminderForm(request.POST, prefix='reminder')
            if reminder_form.is_valid():
                guest = reminder_form.cleaned_data['email']
                email_invite_code(guest)
                reminder_form = ReminderForm(prefix='reminder')
            form = LoginForm(prefix='login')
    else:
        form = LoginForm(prefix='login')
        reminder_form = ReminderForm(prefix='reminder')
    return render_to_response('login.html', {
        'form': form,
        'reminder_form': reminder_form,
        'next': next,
        })


def rsvp_login_from_token(request, invite_code, target="rsvp"):
    u = InviteeAuthBackend().authenticate(invite_code)
    if u:
        inv = user_to_invitee(u)
        inv.last_visited = datetime.now()
        inv.save()
        login(request, u)
        return HttpResponseRedirect('/%s/'%(target,))
    else:
        return HttpResponseRedirect('/accounts/login/')

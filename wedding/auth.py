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
from djwed.wedding.models import Invitee
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


def rsvp_logout(request):
    logout(request)
    return HttpResponseRedirect('/rsvp/')

def rsvp_login(request):
    next = ''
    if request.REQUEST.has_key('next'):
        next = request.REQUEST['next']
    if request.method == 'POST': 
        form = LoginForm(request.POST) 
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
        form = LoginForm() # An unbound form
    return render_to_response('login.html', { 'form': form, 'next': next })


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

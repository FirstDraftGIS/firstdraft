from apifd.scripts.create.frequency_geojson import run as create_frequency_geojson
from apifd.serializers import PlaceSerializer
from appfd import forms, models
from appfd import cleaner
from appfd.finisher import finish_order
from appfd.forms import *
from appfd.generator import generate_map_from_sources 
from appfd.generator.additions import generate_possible_additions
from appfd.models import *
from bnlp import clean as bnlp_clean
from bnlp import getLocationsAndDatesFromEnglishText, getLocationsFromEnglishText
from bs4 import BeautifulSoup
from collections import Counter
import csv
from date_extractor import extract_date
from datetime import datetime
from docx import Document
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST
from itertools import groupby, islice
import location_extractor
from magic import from_file
from metadata_extractor import is_metadata, extract_metadata, save_metadata
from multiprocessing import Process
from openpyxl import load_workbook
from operator import itemgetter
from os import listdir, mkdir, remove
from os.path import isfile
import json, requests, StringIO, sys, zipfile
from json import dumps, loads
from re import findall, search
from requests import get
from rest_framework.response import Response
from appfd.resolver import resolve_locations
from sendfile import sendfile
from scrp import getTextContentViaMarionette, getRandomUserAgentString
from subprocess import call, check_output
from super_python import superfy
from urllib import quote, quote_plus, unquote, urlretrieve
from openpyxl import load_workbook
from zipfile import ZipFile
#import sys


"""
#def log(string):
#    print >> sys.stderr, 'message ...'
#    print string
#    with open("/home/usrfd/logfd.txt", "wb") as f:
#        f.write(string)


    with open("/tmp/logfd.txt", "a") as f:
        f.write(string)
"""

##basically if aws
#if check_output(['uname','-n']).startswith("ip"):
#    #f = open("/tmp/stdout","w")
#    sys.stdout = sys.stderr

# returns longest soup
def soupify(text):
    soups = []
    for parser in ["html5lib", "html.parser"]:
        try:
            soup = BeautifulSoup(text, parser)
            soups.append([soup, len(soup)])
        except Exception as e:
            print e
    return sorted(soups, key=lambda tup: -1 * tup[1])[0][0]

def _map(request, job):

    print "starting _map with ", job

    order = Order.objects.get(token=job)
    if not order.edited:

        order.edited = True
        order.save()

        # verify all the features basically saying a user has checked this over
        # really should have a more sophisticated way of seeing if a user has actually gone through the process
        # of verifying and not just popped open the edit page out of curiosity
        Feature.objects.filter(order_id=order.id).update(verified=True)

    return render(request, "appfd/map.html", {'job': job})

# Create your views here.
def must_be_active(user):
   return user.is_authenticated() and user.is_active

def about(request):
    return render(request, "appfd/about.html", {})

def activate(request, key):
    activation = Activation.objects.get(key=key)
    print "activation is", activation
    if activation.used:
        print "activation has already been used"
    else:
        print "activation has not been used yet"
        if activation.expired:
            print "activation has expired"
        else:
            print "activation hadn't expired as of last check"
            print "today is", datetime.now()
            print "date of activation key is", activation.created
            difference = (datetime.now() - activation.created.replace(tzinfo=None)).days
            print "difference is", difference
            if difference > 7:
                print "activation has timed out and expired"
                activation.expired
                activation.save()
            else:
                print "you still got time, so we're gonna activate"
                user = activation.user
                user.is_active = True
                user.save()
                activation.used = True
                activation.save()
    return HttpResponseRedirect('/')

@csrf_protect
@user_passes_test(must_be_active)
def change_email(request):
    user = request.user
    print "user is", user
    if request.method == 'POST':
        print "request.method is", request.method
        form = forms.ChangeEmailForm(data=request.POST)
        if form.is_valid():
            print "form is valid with cleaned_data", form.cleaned_data
            password = form.cleaned_data['password']
            if user.check_password(password):
                new_email = form.cleaned_data['new_email']
                new_email2 = form.cleaned_data['new_email2']
                if new_email == new_email2:
                    if len(new_email) <= 30:
                        if User.objects.filter(email=email).exists():
                            form.add_error('new_email', 'Uh oh! A user with that email already exists.')
                        else:
                            user.is_active = False
                            user.username = new_email
                            user.email = new_email
                            user.save()

                            #create activation object/key
                            Activation.objects.create(expired=False, key=get_random_string(length=175), used=False, user=user)

                            print "send an activation email"
                            link = "http://" + host + "/activate/" + key
                            try: send_mail("[First Draft] Confirm Your New Email Address", "Please click the following link in order to re-activate the account under a new email address: " + link, "2347812637543875413287548123548213754@gmail.com", [user.email], fail_silently=False, html_message="<h3>Please click the following link in order to re-activate the account under a new email address:</h3></br></br><a href='" + link + "'>" + link + "</a>")
                            except Exception as e: print e

                            alerts = [{"type": "warning", "text": "Re-activate your account under the new email adress by going to the link we sent in an email to " + str(request.user.email)}]
                            return render(request, 'appfd/change_email.html', {'alerts': alerts})
                    else: #len(new_email) > 30
                        form.add_error('new_email', 'Your email is too long.  We only accept emails that are less than 30 characters long.')
                        return render(request, 'appfd/change_email.html', {"form": form})
                else: #new_email != new_email2
                    form.add_error('new_email', 'That two email addresses you entered do not match.')
                    return render(request, 'appfd/change_email.html', {"form": form})
            else:
                form.add_error('new_email', 'The password that you entered is incorrect.')
                return render(request, 'appfd/change_email.html', {"form": form})
        else: #form is not valid
            print "form is not valid:", form.errors
            return render(request, 'appfd/change_email.html', {"form": form})

    elif request.method == "GET":
        print "request.method == \"GET\'"
        current_email = request.user.email
        print "current_email is", current_email
        return render(request, 'appfd/change_email.html', {"current_email": current_email})

@csrf_protect
@user_passes_test(must_be_active)
def change_password(request):
    if request.method == 'POST':
        print "request.method is", request.method
        form = forms.ChangePasswordForm(data=request.POST)
        if form.is_valid():
            print "form is valid with cleaned_data", form.cleaned_data
            old_password = form.cleaned_data['old_password']
            user = request.user
            if user.check_password(old_password):
                new_password = form.cleaned_data['new_password']
                user.set_password(new_password)
                user.save()
                alerts = [{"type": "danger", "text": "Activate your account by going to the link we sent in an email to " + str(request.user.email)}]
                return render(request, 'appfd/change_password.html', {'alerts': alerts})
            else:
                form.add_error('old_password', 'You entered the wrong old password.  Click forgot my password if you forgot it.')
                return render(request, 'appfd/change_password.html', {'form': form})
        else:
            print "form is valid"
            return render(request, 'appfd/change_password.html', {'form': form})
    else:
        print "request.method is probably get"
        return render(request, 'appfd/change_password.html', {})


def contact(request):
    return render(request, "appfd/contact.html", {})

def contributing(request):
    return render(request, "appfd/contributing.html", {})

def disclaimers(request):
    return render(request, "appfd/disclaimers.html", {})

# this is the embed frequency map if you have the job token in the url
@xframe_options_exempt
def embed_frequency_map_with_job(request, job):
    if request.method == "GET":
        return render(request, "appfd/embed_frequency_map.html", {'job': job})

def help(request):
    return render(request, "appfd/help.html", {})

@xframe_options_exempt
def iframe(request):
  try:
    if request.method == "GET":
        print "request:", request
        meta = request.META 
        print "meta:", meta
        if "HTTP_REFERER" in meta:
            url = meta["HTTP_REFERER"]
        if url:
            order = Order.objects.filter(url=url).first()
            if order:
                print "got order:", order
            else:
                key = get_random_string(25)
                order = Order.objects.create(token=key, url=url)
                print "created order:", order
                job = { "link": url, "key": key }
                create_map_from_link(job)
    
    return render(request, "appfd/embed.html", {'job': order.token})
  except Exception as e:
    print e

def index(request):
    #print "starting index with request"

    #user = request.user
    #alerts = list(Alert.objects.filter(user=None))
    #print "type(alerts) is", type(alerts)
    #try:
        #if user.is_authenticated():
        #    if request.user.is_active:
        #        print "user is activate so no need to deal with activation"
        #        activation = Activation.objects.get(user=request.user)
        #        if not activation.notified_success:
        #            alerts.append({"type": "success", "text": "You have successfully activated your account!"})
        #            activation.notified_success = True
        #            activation.save()
        #    else:
        #        print "user is not active, so haven't activated yet"
        #        alerts.append({"type": "danger", "text": "Activate your account by going to the link we sent in an email to " + str(request.user.email)})
        #else:
        #    print "User hasn't logged in, so don't bother with account activation alerts"

    #except Exception as e: print e


    #print "about to finish index"
    #return render(request, "appfd/index.html", {'alerts': alerts})
    return render(request, "appfd/index.html")

@csrf_protect
def password_recovery(request):
    user = request.user
    if user.is_authenticated():
        print "user is authenticated, so shouldn't be using forgot_password screen"
    else:
        if request.method == 'POST':
            print "request.method is post, so change the password and send that email!!"
            alerts = []
            form = forms.EmailForm(data=request.POST)
            if form.is_valid():
                print "cd is", form.cleaned_data
                email = form.cleaned_data['email']
                qs = User.objects.filter(email=email)
                count = qs.count()
                if count == 1:
                    print "looking good. there is 1 user with that email"
                    user_supposed = qs[0]
                    new_password = get_random_string(length=175)
                    user_supposed.set_password(new_password)
                    user_supposed.save()
                    print "password changed to temp password"
                    print "now send it in an email"

                    alerts.append({"type": "success", "text": "We have sent you an email with a new temporary password."})


                    #print "create the alert that will show on the page"
                    #Alert.objects.create(permanent=False, text="We recently sent you an email to you with a new temporary password.  Please make sure to change that password.", user=user_supposed)
                elif count == 0:
                    form.add_error('email', 'There are no users with that email address')
                elif count > 1:
                    form.add_error('email', 'Something is wrong.  More than 1 user has that email address')

            return render(request, "appfd/password_recovery.html", {'alerts': alerts, 'form': form})

        else:
            return render(request, "appfd/password_recovery.html", {})
#    #changes password to long ass string and then emails this to the user
#
#    #change password


def mission(request):
    return render(request, "appfd/mission.html", {})

@csrf_protect
def register(request):
    host = request.get_host()
    if request.method == 'POST':
        print "request.method is", request.method
        form = forms.RegistrationForm(data=request.POST)
        if form.is_valid():
            print "form is valid with cleaned_data", form.cleaned_data
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).count() > 0:
                print "count > 0"
                form.add_error('email', "The email " + email + " is already being used.")
                return render(request, 'appfd/register.html', {'form': form})
            else:
                print "that's a new email"
                password = form.cleaned_data['password']
                user = User.objects.create(email=email, username=email, is_active=False)
                user.set_password(password)
                user.save()

                print "created user", user

                #create activation key
                #todo: make activation key of variable length
                key = get_random_string(length=175)
                Activation.objects.create(expired=False, key=key, used=False, user=user)

                print "send an activation email"
                link = "http://" + host + "/activate/" + key
                try: send_mail("[First Draft] Confirm Your Email Address", "Please click the following link in order to activate the account: " + link, "123489123401238476123847123412341234l@gmail.com", [user.email], fail_silently=False, html_message="<h3>Please click the following link in order to activate the account:</h3></br></br><a href='" + link + "'>" + link + "</a>")
                except Exception as e: print e

                #login after registration
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth.login(request, user)
                print "logged in user"

                print "return to the homepage after a succesful registration"
                return render(request, 'appfd/register_success.html', {})
        else:
            print "form is valid"
            return render(request, 'appfd/register.html', {'form': form})
    else:
        print "request.method is probably get"
        return render(request, 'appfd/register.html', {})


def team(request):
    team_members = TeamMember.objects.all()
    return render(request, "appfd/team.html", {'team_members': team_members})
   
def generate_metadata_from_file(job):
    try:
        key = job['key']
        countries = job['countries'] if "countries" in job else []
        directory = "/home/usrfd/maps/" + key + "/"
        file_obj = job['file']
        filename = job['filename'] if "filename" in job else file_obj.name
        order_id = job['order_id']
        print "order_id:", order_id
        try:
            order = Order.objects.get(id=order_id)
            print "order:", order
        except Exception as e:
            print "COULDN'T GET ORDER", e
        if 'filepath' not in job:
            # make directory to store file and maps
            mkdir(directory)

            filepath = directory + "/" + filename
            print "filepath = ", filepath

            # save file to disk
            with open(filepath, 'wb+') as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
            print "wrote file"

        metadata = extract_metadata(file_obj)
        print "metadata:", metadata
        print "directory:", directory

        print "order_id:", order_id
        for d in metadata:
            metadata_id = MetaData.objects.create(order_id=order_id).id
            for k, v in d.items():
                MetaDataEntry.objects.create(metadata_id=metadata_id, key=k, value=v)

        save_metadata(metadata, _format="ISO 19115-2", path_to_dir=directory)

        with ZipFile(directory + key + "_metadata.zip", 'w') as zipped_shapefile:
            for filename in listdir(directory):
                if filename.split(".")[-1] == "xml":
                    path_to_file = directory + filename
                    zipped_shapefile.write(path_to_file, filename)

        print "ABOUT TO FINISH ORDER"
        try:
            finish_order(job['key'])
        except Exception as e:
            print "CAUGHT EXCEPTION trying to finish_order:", e
        
    except Exception as e:
        print "CAUGHT ERROR in generate_metadata_from_file", e

def does_map_exist(request, job, extension):
    #print "starting does_map_exist"
    try:
        if extension == "shp":
            if isfile("/home/usrfd/maps/" + job + "/" + job + ".zip"):
                return HttpResponse("yes")
            else:
                return HttpResponse("no")
        elif extension in ["csv", "geojson", "gif", "jpg", "json", "pdf", "png", "tsv", "xy"]:
            if isfile("/home/usrfd/maps/" + job + "/" + job + "." + extension):
                return HttpResponse("yes")
            else:
                return HttpResponse("no")
            
    except Exception as e:
        print "[does_map_exist]", e
        return HttpResponse("no")

def does_metadata_exist(request, job, _type="iso_19115_2"):
    print "starting does_metadata_exist with", job, _type
    try:
        if _type == "iso_19115_2":
            if isfile("/home/usrfd/maps/" + job + "/" + job + "_metadata.zip"):
                return HttpResponse("yes")
            else:
                return HttpResponse("no")
    except Exception as e:
        print "CAUGHT EXCEPTION IN does_metadata_exist:", e
        return HttpResponse("no")

#


#basically looks for the directory that corresponds to the job
# and returns whatever file in their that ends with geojson
def get_map(request, job, extension):
  try:
    print "starting get_map with", job, extension
    path_to_directory = "/home/usrfd/maps/" + job + "/"

    # currently, loads zip file in memory and returns it
    # todo: use mod_xsendfile, so don't load into memory
    if extension in ("shp","zip"):
        filename = job + ".zip"
        abspath = path_to_directory + filename

        with open(abspath, "rb") as zip_file:
            response = HttpResponse(zip_file, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename="%s"' % filename
            return response
    elif extension in ("jpeg", "gif", "jpg", "png"):
        with open(path_to_directory + job + "." + extension) as f:
            data = f.read()
        return HttpResponse(data, content_type="image/" + extension)
    elif extension == "pdf":
        with open(path_to_directory + job + "." + extension) as f:
            data = f.read()
        return HttpResponse(data, content_type='application/pdf')
    else:
        data = ""
        for filename in listdir(path_to_directory):
            print "for filename"

            if filename == job + "." + extension:
                with open(path_to_directory + filename) as f:
                    data = f.read()
                break
        return HttpResponse(data, content_type='application/json') 
  except Exception as e:
    print e

def get_metadata(request, job, metadata_type="iso_19115_2"):
    try:
        print "starting get_metadata with", job, metadata_type
        path_to_directory = "/home/usrfd/maps/" + job + "/"

        # should auto-verify metadata at this point

        if metadata_type == "iso_19115_2":
            filename = job + "_metadata.zip"
            abspath = path_to_directory + filename

            with open(abspath, "rb") as zip_file:
                response = HttpResponse(zip_file, content_type='application/force-download')
                response['Content-Disposition'] = 'attachment; filename="%s"' % filename
                return response

    except Exception as e:
        print e

def thanks(request):
    with open("/home/usrfd/firstdraft/requirements.txt") as f:
        list_to_thank = [("Clavin","https://github.com/Berico-Technologies/CLAVIN"),("Leaflet", "leafletjs.com"),("American Red Cross","https://github.com/americanredcross"),("OpenStreetMap","https://www.openstreetmap.org/")]
        list_to_thank += [(package.split("(")[0].strip(), None) for package in f.read().strip().split("\n")]
        return render(request, "appfd/thanks.html", {'list_to_thank': list_to_thank})

def preview_map(request, job):
    return render(request, "appfd/preview_map.html", {'job': job})


# takes in a name of a place
# adds source
# resolve_possible_locations
# triggered when user selects place in add a place
# used to sort possible locations
@require_POST
def request_possible_additions(request):

    form = forms.RequestPossibleAdditionsForm(json.loads(request.body))
    if form.is_valid():
        name = form.cleaned_data['name']
        token = form.cleaned_data['token']
        return HttpResponse(json.dumps([PlaceSerializer(place).data for place in generate_possible_additions(name, token)]), "application/json")
        #return HttpResponse(json.dumps([vars(place) for place in places]), "application/json")


def request_map_from_sources(request, debug=True):

    try:
        print "starting upload_file"
        if request.method == 'POST':
            # need to add a way, so can upload advanced options
            #print "request.FILES", type(request.FILES['source_1_data'])
            #print "request.FILES:", request.FILES
            #print "request.POST:", request.POST
            cleaned = cleaner.clean(request.POST, request.FILES)
            if debug: print "cleaned:", cleaned
            if cleaned:
                key = get_random_string(25)

                job = {
                    'key': key
                }

                end_user_timezone = None
                if "extra_context" in cleaned:
                    job['extra_context'] = {}
                    if "end_user_timezone" in cleaned['extra_context']:
                        job['extra_context']['end_user_timezone'] = end_user_timezone = cleaned['extra_context']['end_user_timezone']

                order_id = Order.objects.create(token=key, end_user_timezone=end_user_timezone, map_format=cleaned['map_format']).id
                from django.db import connection 
                connection.close()
                sources = cleaned['sources']
                job['sources'] = sources
                job['order_id'] = order_id
                if "countries" in cleaned:
                    job['countries'] = cleaned['countries']
                if "style" in cleaned:
                    job['style'] = {}
                    if "basemap" in cleaned['style']:
                        job['style']['basemap'] = cleaned['style']['basemap']
                if debug: print "job:", job
 
                data = []
                metadata = []
                print "sources:", sources
                for source in sources:
                    if is_metadata(source['data'], debug=False):
                        print "is metadata"
                        metadata.append(source)
                    else:
                        print "is NOT metadata"
                        data.append(source)

                print "data:", data
                print "metadata:", metadata

                Process(target=generate_map_from_sources, args=(job, data, metadata)).start()

                return HttpResponse(job['key'])
                
    except Exception as e:
        print "CAUGHT ERROR in request_map_from_sources:", e
 

def view_frequency_map(request, job):
    return render(request, "appfd/view_frequency_map.html", {'job': job})

def view_map(request, job):
    return render(request, "appfd/view_map.html", {'job': job})



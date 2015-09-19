from appfd import forms, models
from appfd.forms import *
from appfd.models import *
from appfd.scripts import excel, resolve
from appfd.scripts.excel import *
from bnlp import getLocationsFromEnglishText
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
from django.views.decorators.csrf import csrf_protect
from magic import from_file
from multiprocessing import Process
from openpyxl import load_workbook
from operator import itemgetter
from os import listdir, mkdir
from os.path import isfile
import datetime, geojson, json, requests, sys
from geojson import Feature, FeatureCollection, MultiPolygon, Point
import geojson
from json import dumps, loads
from requests import get
from subprocess import check_output
from urllib import quote, quote_plus, urlretrieve
from openpyxl import load_workbook
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
            print "today is", datetime.datetime.now()
            print "date of activation key is", activation.created
            difference = (datetime.datetime.now() - activation.created.replace(tzinfo=None)).days
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


# this method takes in data as text and returns a geojson of the map
def crunch(request):
    try:
        print "starting crunch"
        if request.method == 'POST':
            log("request.method is post")
        print "finish crunch"
    except Exception as e:
        log(str(e))


def disclaimers(request):
    return render(request, "appfd/disclaimers.html", {})

def index(request):
    print "starting index with request"

    user = request.user
    alerts = list(Alert.objects.filter(user=None))
    print "type(alerts) is", type(alerts)
    try:
        if user.is_authenticated():
            if request.user.is_active:
                print "user is activate so no need to deal with activation"
                activation = Activation.objects.get(user=request.user)
                if not activation.notified_success:
                    alerts.append({"type": "success", "text": "You have successfully activated your account!"})
                    activation.notified_success = True
                    activation.save()
            else:
                print "user is not active, so haven't activated yet"
                alerts.append({"type": "danger", "text": "Activate your account by going to the link we sent in an email to " + str(request.user.email)})
        else:
            print "User hasn't logged in, so don't bother with account activation alerts"

    except Exception as e: print e


    print "about to finish index"
    return render(request, "appfd/index.html", {'alerts': alerts})

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


def create(job):
    print "starting create with", job
    places = []
    for location in getLocationsFromEnglishText(job['data']):
        if len(location) > 1:
            place = resolve.resolve(location)
            if place and place not in places:
                places.append(place)

    print "places are", places
    serialized = serialize('geojson', places, geometry_field='point', fields=('geonameid', 'name','point',))

    # make directory to store files
    directory = "/home/usrfd/maps/" + job['key'] + "/"
    mkdir(directory)
    with open(directory + "job.geojson", "wb") as f:
        f.write(serialized)

def create_map_from_link(job):
    print "starting create with", job

    # make directory to store saved webpage and maps
    directory = "/home/usrfd/maps/" + job['key'] + "/"
    mkdir(directory)

    # get url
    link = job['link']

    # get web page text
    filename = link.replace("/","_").replace("\\","_").replace("'","_").replace('"',"_").replace(".","_").replace(":","_").replace("__","_")
    text = get(link).text
 

    # save text to file
    with open(directory + filename, "wb") as f:
        f.write(text.encode('utf-8'))
 
    places = []
    for location in getLocationsFromEnglishText(text):

        #making sure we don't try to resolve single letters like U
        if len(location) > 1:
            place = resolve.resolve(location)
            if place and place not in places:
                places.append(place)

    print "places are", places
    serialized = serialize('geojson', places, geometry_field='point', fields=('geonameid', 'name','point',))

    # make directory to store files
    with open(directory + job['key'] + ".geojson", "wb") as f:
        f.write(serialized)

def create_map_from_link_to_file(job):
    print "starting create_from_file with", job

    # make directory to store saved webpage and maps
    directory = "/home/usrfd/maps/" + job['key'] + "/"
    mkdir(directory)

    # get url
    link = job['link']

    # get web page text
    filename = link.replace("/","_").replace("\\","_").replace("'","_").replace('"',"_").replace(":","_").replace("__","_")

    # create path to file
    path_to_file = directory + filename

    # save file to folder
    urlretrieve(link, path_to_file)
 
    mimeType = from_file(path_to_file, mime=True)
    print "mimeType is", mimeType

    job['filename'] = filename
    job['filepath'] = path_to_file
    
    if filename.endswith(('.xls','.xlsm','.xlsx')):
        create_from_xl(job)

def create_from_file(job):
    print "starting create_from_file with", job
    content_type = job['file'].content_type
    print "content_type is", content_type

    # .split("/")[-1] prevents would-be hackers from passing in paths as filenames
    job['filename'] = filename = job['file'].name.split("/")[-1]
    if filename.endswith(('.xls','.xlsx')):
        print "user uploaded an excel file!"
        create_from_xl(job)


def create_from_xl(job):
    print "starting create_from_xl with", job
    directory = "/home/usrfd/maps/" + job['key'] + "/"
    filename = job['filename']

    if 'filepath' not in job:
        file_obj = job['file']

        # make directory to store excel file and maps
        mkdir(directory)

        filepath = directory + "/" + filename

        # save file to disk
        with open(filepath, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)
        print "wrote file"
    else:
        filepath = job['filepath']

    wb = load_workbook(filepath)
    print "wb is", wb

    features = []

    for sheet in wb:
        rows = sheet.rows
        headerRow = getHeaderRow(rows[0], rows)


        location_column_index = getLocationColumn(sheet)
        print "location_column_index is", location_column_index 

        for row_index, row in enumerate(rows):
            if headerRow:
                if row_index == 0:
                    pass
                else:
                    geometry = None
                    properties = {}
                    for cell_index, cell in enumerate(row):
                        value = cleanCellValue(cell.value)
                        if cell_index == location_column_index:
                            place = resolve.resolve(value)
                            if place:
                                point = place.point
                                geometry = Point((point.x,point.y))
                        properties[headerRow[cell_index]] = value
                    feature = Feature(geometry=geometry, properties=properties)
                    features.append(feature)
            else: #not headerRow
                geometry = None
                properties = {}
                for cell_index, cell in enumerate(row):
                    value = cleanCellValue(cell.value)
                    if cell_index == location_column_index:
                        #strip makes sure we remove any white space
                        place = resolve.resolve(value)
                        if place:
                            point = place.point
                            geometry = Point((point.x,point.y))
                        
                    properties[cell_index] = value
                feature = Feature(geometry=geometry, properties=properties)
                features.append(feature)


    featureCollection = FeatureCollection(features)
    serialized = geojson.dumps(featureCollection, sort_keys=True)
   
    with open(directory + filename.split(".")[0] + "." + "geojson", "wb") as f:
        f.write(serialized)

    print "finished creating geojson from excel file"

def does_map_exist(request):
    print "starting does_map_exist"
    print "request.body is", request.body


#basically looks for the directory that corresponds to the job
# and returns whatever file in their that ends with geojson
def get_map(request, job, extension):
  try:
    print "starting get_map with", job, extension
    path_to_directory = "/home/usrfd/maps/" + job + "/"

    data = ""
    for filename in listdir(path_to_directory):
        print "for filename"
        if filename.endswith("."+extension):
            with open(path_to_directory + filename) as f:
                data = f.read()
            break
    return HttpResponse(data, content_type='application/json') 
  except Exception as e:
    print e


# this method takes in data as text and returns a geojson of the map
def upload(request):
    print "starting upload"
    if request.method == 'POST':
        print "request.method is post"
        job = {
              'data': loads(request.body)['story'],
              'key': get_random_string(25)
        }
        Process(target=create, args=(job,)).start()
        return HttpResponse(job['key'])
    else:
        return HttpResponse("You have to post!")

def start_link(request):
  try:
    print "starting start_link"
    if request.method == 'POST':
        print "request.method is post"
        job = {
              'link': loads(request.body)['link'],
              'key': get_random_string(25)
        }
        Process(target=create_map_from_link, args=(job,)).start()
        return HttpResponse(job['key'])
    else:
        return HttpResponse("You have to post!")
  except Exception as e:
    print e

def start_link_to_file(request):
  try:
    print "starting start_link"
    if request.method == 'POST':
        print "request.method is post"
        job = {
              'link': loads(request.body)['link'],
              'key': get_random_string(25)
        }
        Process(target=create_map_from_link_to_file, args=(job,)).start()
        return HttpResponse(job['key'])
    else:
        return HttpResponse("You have to post!")
  except Exception as e:
    print e


def upload_file(request):
  try:
    print "starting upload_file"
    if request.method == 'POST':
        print "request.method is post"
        form = UploadFileForm(request.POST, request.FILES)
        print "form is", form
        if form.is_valid():
            print "form is valid"
            job = {
              'file': request.FILES['file'],
              'key': get_random_string(25)
            }
            print "job is", job
            Process(target=create_from_file, args=(job,)).start()
            return HttpResponse(job['key'])
        else:
            print form.errors
            return HttpResponse("post data was malformed")
    else:
        return HttpResponse("You have to post!")
  except Exception as e:
    print "e is", e

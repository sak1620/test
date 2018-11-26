from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.files import File
from .models import Image
import os
from django.http import Http404
from ua_parser import user_agent_parser
import ast
from django.views.decorators.csrf import ensure_csrf_cookie
from via_image.models import Image, LabelName, Segment
from via_manager.models import ImageBatch
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db import connection
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.images import get_image_dimensions
import os


MIN_VERTICES = 3


# Create your views here.
def vw_login_user(request):
    logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                print("@@@@@@@@@@@@@@@@@#############")
                return redirect('../operator/some/')
    
    print("@@@@@@@@@@@@@@@@@HIHIHI#############")
    return render(request, 'registration/login.html')


@login_required
def vw_log(request):
    logout(request)
    return render(request, 'registration/login.html')


@login_required
def vw_index(request):
    if 'batch_id' not in request.session:
        return redirect('/operator/')
    else:
        page = "index1"
        images = ImageBatch.objects.filter(batch_id=request.session['batch_id'])
        print("IMAGES",images)
        return render(request, 'via_image/index1.html', {'images':images, 'page':page})


@ensure_csrf_cookie
def index(request):
    context = {}
    context['label_image'] = ImageBatch.objects.filter(annotated=False)[0].id
    context['review_image'] = ImageBatch.objects.filter(reviewed=False)[0].id
    return render(request, 'via_image/index.html', context)


@ensure_csrf_cookie
def question(request,image_id):
    context = {}
    next_image_id = ImageBatch.objects.filter(annotated=False).first()
    s = ''.join(x for x in str(next_image_id) if x.isdigit())
    context['next_image_id'] = s
    print("context",context)
    print("next_image_id",next_image_id)
    return render(request,'via_image/question.html', context)


@ensure_csrf_cookie
# Change here next_image_id so that the page can be opened.
def question_review(request,image_id):
    context = {}
    not_reviewed = ImageBatch.objects.filter(reviewed=False)
    valid_ids = [x.id for x in not_reviewed if x != image_id]
    context['next_image_id'] = str(valid_ids[0])
    return render(request,'via_image/question_review.html', context)


@login_required
@ensure_csrf_cookie
def segment(request, image_id):
    if request.method == 'POST':
        results = ast.literal_eval(request.POST['results'])
        labels = ast.literal_eval(request.POST['labs'])
        image = ImageBatch.objects.get(id=image_id)
        Segment.objects.filter(image=image).delete()
        save_segments(image_id, results, labels)
        return json_success_response()
    else:
        response = browser_check(request)
        image = ImageBatch.objects.get(id=image_id)
        images = ImageBatch.objects.all().filter(id=image_id)
        segments = image.segment_set.all()
        # dimensions of image
        width, height = get_image_dimensions(os.getcwd()+""+image.path)
        print(os.getcwd())
        print("height",height)
        print("height",width)
        labels = [str(s.label.name) for s in segments]
        coords = []
        for s in segments:
            values = [float(x) for x in s.coords.split(',')]
            c = []
            for i in range(0, len(values),2):
                temp = {'x': values[i], 'y': values[i+1]}
                c.append(temp)
            coords.append(c)
        print("coords", coords)

        context = {}
        context['content'] = {'id': image_id, 'url': image.path}
        context['min_vertices'] = MIN_VERTICES
        context['instructions'] = 'via_image/segment/segment_inst_content.html'
        context['label_html'] = create_label_html()
        context['coords'] = coords
        context['labels'] = labels
        context['height'] = height
        context['width'] = width


        response = render(request, 'via_image/segment/segment.html', context)
        response['x-frame-options'] = 'EXEMPT'
        # return response
        return render(request, 'via_image/segment/segment.html', context)


@login_required
@ensure_csrf_cookie
def review(request, image_id):
    if request.method == 'POST':
        print(request.POST['labs'])
        accepted = str(request.POST['accepted'])
        if accepted == "false":
            accepted = False
        else:
            accepted = True
        results = ast.literal_eval(request.POST['results'])
        labels = ast.literal_eval(request.POST['labs'])

        imObj = ImageBatch.objects.get(id=image_id)
        if accepted:
            imObj.reviewed = True
            imObj.save()
            Segment.objects.filter(image=imObj).delete()
            save_segments(image_id, results, labels, reviewing=True)
        else:
            imObj.annotated = False
            imObj.save()
        return json_success_response()
    else:
        response = browser_check(request)
        image = ImageBatch.objects.get(id=image_id)
        segments = image.segment_set.all()
        # dimensions of image
        width, height = get_image_dimensions(os.getcwd()+""+image.path)
        print("height",height)
        print("height",width)
        labels = [str(s.label.name) for s in segments]
        coords = []
        for s in segments:
            values = [float(x) for x in s.coords.split(',')]
            c = []
            for i in range(0, len(values),2):
                temp = {'x': values[i], 'y': values[i+1]}
                c.append(temp)
            coords.append(c)

        context = {}
        context['content'] = {'id': image_id, 'url': image.path}
        context['instructions'] = 'via_image/review/review_inst_content.html'
        context['label_html'] = create_label_html()
        context['labels'] = labels
        context['coords'] = coords
        context['height'] = height
        context['width'] = width

        response = render(request, 'via_image/review/review.html', context)
        response['x-frame-options'] = 'EXEMPT'
        return response

#########
#
#  General Helper Functions
#
#########

# used to create selector for annotation labeling modal
def create_label_html():
    labels = sorted([str(l.name) for l in LabelName.objects.all()])
    label_body = '<select id="label_list">'
    for l in labels:
        label_body += '<option value="%s">%s</option>' %(l,l)
    label_body += '</select>'
    return label_body


def save_segments(image_id, points, labels, reviewing=False):
    pointList = points[str(image_id)]
    labelList = labels[str(image_id)]
    image = ImageBatch.objects.get(id=image_id)

    if len(pointList) > 0 or len(labelList) > 0:
        if reviewing:
            image.reviewed = True
        else:
            image.annotated = True
        image.save()

    for i in range(len(pointList)):
        vertexStr = ','.join([str(x) for x in pointList[i]])
        label = LabelName.objects.get(name=labelList[i])

        segment = Segment(image=image, label=label, coords=vertexStr)
        segment.save()


def html_error_response(request, error):
    return render(request, "via_image/error.html", {'message': error})


def json_success_response():
    return HttpResponse(
        '{"message": "success", "result": "success" }',
        content_type='application/json')


def browser_check(request):
    """ Only allow firefox and chrome, and no mobile """
    valid_browser = False
    if 'HTTP_USER_AGENT' in request.META:
        ua = user_agent_parser.Parse(request.META['HTTP_USER_AGENT'])
        if ua['user_agent']['family'].lower() in ('firefox', 'chrome'):
            device = ua['device']
            if 'is_mobile' not in device or not device['is_mobile']:
                valid_browser = True
    if not valid_browser:
        return html_error_response(
            request, '''
            This task requires Google Chrome. <br/><br/>
            <a class="btn" href="http://www.google.com/chrome/"
            target="_blank">Get Google Chrome</a>
        ''')
    return None


def addlabel(request):
    user = request.user
    cursor = connection.cursor()
    cursor.execute(
        ''' select company_id from usercompanymap where employee_id=%s ''', (user.id,))
    company_id = cursor.fetchall()
    print(company_id)
    label = request.POST["label"]
    print(label)
    LabelName.objects.create(
        name=label,
        company_id=company_id[0][0]
    )
    status={"ok":"ok"}
    return JsonResponse(status)
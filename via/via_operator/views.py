from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.files import File
from django.core import serializers
from .forms import VideoForm
from .forms import VideoBatchForm
from .models import Video
from django.views import View
from via_manager.models import VideoBatch, Batch, ImageBatch
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import connection
from django import template
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
register = template.Library()
import datetime
from django.utils import timezone
from django.views.generic import UpdateView

# Create your views here.
def vw_some(request):
    # return HttpResponse(text)
    if request.user.groups.filter(name="operator").exists():
        return redirect("../../operator")
    elif request.user.groups.filter(name="manager").exists():
        return redirect("../../manager/")
    elif request.user.groups.filter(name="admin").exists():
        return redirect("../../via_admin")
    elif request.user.is_superuser:
        return redirect("../../superadmin")


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


def vw_landing(request):
    return render(request, "landing_page/landing_page.html")


@login_required
def vw_index(request):
    if 'batch_id' in request.session:
        del request.session['batch_id']
    # videos = Video.objects.all()
    # print(videos[0].video)
    print("heyo")
    print(timezone.now)

    user_id = request.user.id
    print(user_id)
    c2 = connection.cursor()
    c2.execute(''' select * from usercompanymap where employee_id=%s ''',(user_id,))
    c2_get = c2.fetchall()
    comp_id = c2_get[0][3]
    # videoBatches = Batch.objects.filter(id=1)
    # IN progress  batches
    cursor1 = connection.cursor()
    cursor1.execute('''select b.id, b.name, b.assigned_date,b.start_date,b.completeby_date, b.count,b.batch_type,date_part('day',completeby_date - CURRENT_TIMESTAMP)  from batch b, operatorbatchmapping m where b.id=m.batch_id and b.status=3 and m.operator_id=%s ''',(user_id,))
    c_batch = cursor1.fetchall()
    # assigned batches
    cursor2 = connection.cursor()
    cursor2.execute('''select b.id, b.name, b.assigned_date,b.completeby_date, b.count,b.batch_type from batch b, operatorbatchmapping m where b.id=m.batch_id and b.status=2 and m.operator_id=%s ''',(user_id,))
    r_batch = cursor2.fetchall()
    #completed batches
    cursor3 = connection.cursor()
    cursor3.execute('''select b.id, b.name,b.assigned_date,b.start_date,b.completed_date,b.completeby_date, b.count,b.batch_type,date_part('day',completeby_date - completed_date) from batch b, operatorbatchmapping m where b.id=m.batch_id and b.status=4 and m.operator_id=%s ''',(user_id,))
    comp_batch = cursor3.fetchall()
    print("op view 64", comp_batch)

    cursor3.execute('''select b.name, b.completeby_date from batch b, operatorbatchmapping m where b.id=m.batch_id and b.company_id={} and m.operator_id={} and b.status in (1,2,3) order by b.completeby_date asc'''.format(comp_id, user_id))
    batch_tp = cursor3.fetchall()
    print("Batch Tp",batch_tp)    
    batch_ls = []
    tm_now = datetime.datetime.now().date()
    print(tm_now)
    for x in batch_tp:
        if x[1] > tm_now:

            # batch_ls.append([x[0], x[1], 1, 0])
        # else:
            batch_ls.append([x[0], x[1], 0, (x[1] - tm_now).days])
            
    print(batch_ls)
   
    return render(request, 'via_operator/index.html', {'r_batch':r_batch, 'c_batch':c_batch,'comp_batch':comp_batch,'batch_ls':batch_ls})


@login_required
def vw_vatic(request):
    url_abs = request.POST["url_abs"]
    url_ex = request.POST["url_x"]
    split_url = url_ex.rsplit('/', 1)[-1]  
    filename_array = split_url.split('.')
    filename = filename_array[0]
    b_id = request.POST["b_id"]
    batches = VideoBatch.objects.filter(batch_id = b_id).values()
    xml_file = batches[0]['xml_file']
    print("QWETRTYIEREW", xml_file)
    xml_path = "http://127.0.0.1:8000/media/" + xml_file
    print(xml_path)
    if batches[0]['xml_file'] is not None:
        flag = "True"
    else:
        flag = "False"   
    print("Video id : ", b_id)
    form = VideoForm()
    xmlForm = VideoBatchForm()
    user_id = request.user.id
    page = "vatic"
    
    return render(request, 'via_operator/vatic.html', {'form': form, "url_ex":url_ex, 'video_id':b_id,
                                                       'page':page, "xmlForm":xmlForm,"filename":filename,
                                                       "url_abs":url_abs, "flag": flag, "xml_path":xml_path }) 

@login_required
def vw_saveXmlFile(request):
    video_id = request.POST["video_id"]
    xml_file = request.FILES["xml_file"]
    print("FILE",xml_file)
    # fs = FileSystemStorage()
    # path = "xml/%Y%m%d/"
    # fs.path(path)
    # filename = fs.save(xml_file.name, xml_file)
    VideoBatch.objects.filter(id=video_id).update(xml_file=xml_file)
    
    return JsonResponse("File saved", safe=False)


class XmlUploadView(View):
    @login_required
    def post(self, request):
        form = VideoBatchForm(self.request.POST, self.request.FILES)
        print("FORM", form)
        # files = request.FILES[0]
        # print("FILES",files)
        # photo = form.save()

        if form.is_valid():
            print("In operator.vews 117")
            photo = form.save()
            data = {'is_valid': True}
        else:
            data = {'is_valid': False}
            print(form.errors)
            print("In operator.vews 123")

        return JsonResponse(data)          
# def vw_vatic(request):
#     # url_ex = request.POST["url_x"]
#     b_id = request.POST["batch_id"]
#     batches = VideoBatch.objects.filter(batch_id = b_id)
#     print("Video id : ", b_id)
#     print(batches)
#     form = VideoForm()
#     user_id = request.user.id
#     if request.method == "POST":
#         form = VideoForm(request.POST, request.FILES)
#         # form = VaticForm(user_id=user_id)
#         print("inside post vw_vatic")
#         form.save()
#     else:
#         form = VideoForm()
#     return render(request, 'via_operator/vatic.html', {'form': form, 'video_id':b_id, 'batches':batches})    


# def vw_vatic_sidebar(request):
#     # url_ex = request.POST["url_x"]
#     url_ex = request.POST["url_x"]
#     b_id = request.POST["batch_id"]
#     print("Video id : ", b_id)
#     form = VideoForm()
#     user_id = request.user.id
#     if request.method == "POST":
#         form = VideoForm(request.POST, request.FILES)
#         # form = VaticForm(user_id=user_id)
#         print("inside post vw_vatic")
#         form.save()
#     else:
#         form = VideoForm()
#     return render(request, 'via_operator/vatic.html', {'form': form, "url_ex":url_ex, "video_id":b_id})    

@register.filter
def split(string, sep):
    """Return the string split by sep.

    Example usage: {{ value|split:"/" }}
    """
    return string.split(sep)


@login_required
def vw_annotate(request):
    b_id = request.POST['batch_id']
    b_type = request.POST['batch_type']
    print("batch_type", b_type)
    request.session['batch_id'] = b_id
    print(request.session['batch_id'])
    batches = VideoBatch.objects.filter(batch_id = b_id).values()
    print("Batches", batches)
    if not batches:
        batches = ImageBatch.objects.filter(batch_id = b_id).values()
        xml_file = None
    else:
        xml_file = batches[0]['xml_file']

    print("batch_id",b_id)
    bat = Batch.objects.filter(id = b_id).values('start_date')   
    print("#############",bat[0]['start_date'])
    bat1 = bat[0]['start_date']
    if bat1 is None:
        Batch.objects.filter(id = b_id).update(status=3,start_date=timezone.now())    
    else:
        print("Start Date already there")  

    # print("////",batches)
    if xml_file is not None:
        flag = "True"
    else:
        flag = "False"    
    # print("FLAG",flag)
    # page = "annotate"
    # return render(request, 'via_operator/annotate.html', {'batches':batches, 'page': page,'batch_id':b_id,'flag':flag})
    
    if b_type is '1':
        # batches = ImageBatch.objects.filter(batch_id = b_id)
        # print(batches)
        page = "image_annotate"
        # print(page)
        # return render(request, 'via_image/index1.html', {'images':batches, 'page': page,'batch_id':b_id})
        return redirect('../../via_image/')

    elif b_type is '2':
        # batches = VideoBatch.objects.filter(batch_id = b_id)
        page = "video_annotate"
        return render(request, 'via_operator/annotate.html', {'batches':batches, 'page': page,'batch_id':b_id, 'flag':flag})
    
        # return render(request, 'via_operator/annotate.html', {'batches':batches, 'page': page,'batch_id':b_id})
        # return redirect('../annotateCom/')


    # print("////",batches)
    # page = "annotate"
    # return render(request, 'via_operator/annotate.html', {'batches':batches, 'page': page,'batch_id':b_id})
    # return render(request, 'via_operator/vatic.html', {'batches':batches})


@login_required  
def vw_annotate_common(request):
    if 'batch_id' not in request.session:
        return redirect('/operator/')
    else:
        b_id = request.session['batch_id']
        batches = VideoBatch.objects.filter(batch_id = b_id).values()   
        xml_file = batches[0]['xml_file']
        if xml_file is not None:
            flag = "True"
        else:
            flag = "False"  
        page = "video_annotate"
        
        return render(request, 'via_operator/annotate.html', {'batches':batches, 'page': page,'batch_id':b_id,"flag":flag})  


def vw_upload_file(request):
    b_id = request.session['batch_id']
    user_id = request.user.id
    abs_url = request.POST["url_abs"]
    print("abs_url", abs_url)
    xForm = VideoBatchForm()
    i = VideoBatch.objects.get(path = abs_url)
    print("fetch details",i)
    if request.method == "POST":
        #Get the posted form
        xForm = VideoBatchForm(request.POST, request.FILES, instance=i)
        xForm.save()
    else:
        xForm = VideoBatchForm()  
    #   if xForm.is_valid():
    #      videobatch = VideoBatch()
    #     #  xForm = VideoBatchForm(instance=VideoBatch, initial={'user_id':user_id})
    #     #  videobatch.batch_id = b_id
    #     #  videobatch.user_id = user_id
    #      videobatch.xml_file = xForm.cleaned_data["xml_file"]
    #      videobatch.save()
    #      saved = True
    #   else:
    #       xForm = VideoBatchForm()

    # return render(request, 'via_operator/vatic.html', {'xForm':xForm})
    return redirect("../annotateCom")


def vw_batch_completed(request):
    b_id = request.POST["b_id"]
    Batch.objects.filter(id = b_id).update(status=4, completed_date=datetime.datetime.now())    
    response = {"status": "image status updated"}
    return JsonResponse(response)


@login_required
def vw_saveXml(request):
    user_id = request.user.id
    xml_text = request.POST["xml_file"]
    video_id =request.POST["video_id"]
    # print(xml_file)
    print(video_id)
    print(user_id)
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # MEDIA_DIR = os.path.join(BASE_DIR, "media/xml")
    # print("media", MEDIA_DIR)
    # print("cwd", os.getcwd())
    # f = open("/home/dynamo/AiTouch/cvat/cvat/media/xml/test.xml", 'w+')
    # f.write(xml_file)
    # f.close()
    # myfile = File(f)
    temp = VideoBatch.objects.filter(id=video_id).update(xml=xml_text)
    print("@#$%&^Y*&()*#%@")
    print(temp)
    if temp:
        response = {"status" : "XML saved"}
    else:
        response = {"status" : "XML not saved"}

    # if Vatic.objects.create(user_id=user_id, xml=xml_file):
    #     response = {"status" : "XML saved"}
    # else:
    #     response = {"status" : "XML not saved"}

    return JsonResponse(response)  





def vw_chart_data(request):
    user_id = request.user.id
    
    #receiving start and end date
    start_date = request.POST["start_date"]
    end_date = request.POST["end_date"]

    #fetching company id
    c2 = connection.cursor()
    c2.execute(
        ''' select * from usercompanymap where employee_id=%s ''', (user_id,))
    c2_get = c2.fetchall()
    comp_id = c2_get[0][3]
    print(comp_id)

    
    c2.execute(''' select count(*) from batch b, operatorbatchmapping o where b.id=o.batch_id and b.company_id={} and o.operator_id={} and b.status=2 and DATE(b.created_date) BETWEEN '{}' and '{}' '''.format(comp_id, user_id, start_date, end_date))
    assigned = c2.fetchall()[0][0]

    c2.execute(''' select count(*) from batch b, operatorbatchmapping o where b.id=o.batch_id and b.company_id={} and o.operator_id={} and b.status=3 and DATE(b.created_date) BETWEEN '{}' and '{}' '''.format(comp_id, user_id, start_date, end_date))
    prog = c2.fetchall()[0][0]

    c2.execute(''' select count(*) from batch b, operatorbatchmapping o where b.id=o.batch_id and b.company_id={} and o.operator_id={} and b.status=4 and DATE(b.created_date) BETWEEN '{}' and '{}' '''.format(comp_id, user_id, start_date, end_date))
    completed = c2.fetchall()[0][0]

    final_data = [assigned, prog, completed]

    return JsonResponse({"data": final_data})

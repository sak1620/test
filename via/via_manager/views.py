from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from via_superadmin.models import UserCompanyMap
from via_manager.models import OperatorBatchMapping, Batch, VideoBatch, VideoUpload, ImageBatch, ImageUpload
from via_operator.models import Video
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

from django.views.generic.edit import FormView
from via_manager.forms import VideoUploadForm, ImageUploadForm
from django.http import JsonResponse
from django.views import View
from django.db import connection
from random import *
import string
import os
import datetime
from django.core.files.images import get_image_dimensions
import json
from django.utils.encoding import smart_str
from django.conf import settings

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



@login_required
def vw_log(request):
    logout(request)
    return render(request, 'registration/login.html')


@login_required
def vw_ManagerIndex(request):
    print("!!!!!Logged In User!!!!!!",request.user.id,)
    print(datetime.datetime.now())
    user_id = request.user.id
    #Queries
    all_data = User.objects.all()
    batches = Batch.objects.all()

    c2 = connection.cursor()
    c2.execute(''' select * from usercompanymap where employee_id=%s ''',(user_id,))
    c2_get = c2.fetchall()
    comp_id = c2_get[0][3]

    #List of created Batches
    cursor = connection.cursor()
    cursor.execute('''select b.id, b.name,b.created_date, b.count, b.status, i.batch_id as image_batch,v.batch_id as video_batch,
        CASE
        WHEN b.id=i.batch_id THEN 1
        WHEN b.id=v.batch_id THEN 2
        ELSE 0
        END
    from batch as b left join imagebatch as i on b.id=i.batch_id left join videobatch as v on v.batch_id=b.id 
    where b.status=1
    group by b.id, i.batch_id, v.batch_id ''')
    batch_cre = cursor.fetchall()
    print(batch_cre)
    
    #List of assigned Batches
    cursor = connection.cursor()
    cursor.execute('''select m.id, m.supervisor_id,m.batch_id, m.operator_id, u.first_name,b.name, b.count,b.assigned_date,b.completeby_date,b.batch_type from operatorbatchmapping m, auth_user u, batch b where m.operator_id=u.id and m.batch_id=b.id and b.status=2 ''')
    asgn_batch = cursor.fetchall()
    
    #List of In-Progress Batches
    cursor_pro = connection.cursor()
    cursor_pro.execute('''select m.id, m.supervisor_id,m.batch_id, m.operator_id, u.first_name,b.name, b.count,b.assigned_date,b.start_date,b.completeby_date,b.batch_type,date_part('day',completeby_date - CURRENT_TIMESTAMP) from operatorbatchmapping m, auth_user u, batch b where m.operator_id=u.id and m.batch_id=b.id and b.status=3 ''')
    pro_batch = cursor_pro.fetchall()

    #List of Completed Batches
    cursor_comp = connection.cursor()
    cursor_comp.execute('''select m.id, m.supervisor_id,m.batch_id, m.operator_id, u.first_name,b.name, b.count,b.created_date,b.assigned_date,b.start_date,b.completeby_date,b.completed_date,b.batch_type,date_part('day',completeby_date - completed_date) from operatorbatchmapping m, auth_user u, batch b where m.operator_id=u.id and m.batch_id=b.id and b.status=4 ''')
    comp_batch = cursor_comp.fetchall()
    
    # list of operators
    cursor_comp.execute('''select u.first_name, a.group_id from auth_user u, auth_user_groups a, usercompanymap c where u.id=a.user_id and c.employee_id=u.id and a.group_id=4 and c.company_id={}'''.format(comp_id))
    op_ls = cursor_comp.fetchall()

    #user-role
    cursor_user_group = connection.cursor()
    cursor_user_group.execute('''select group_id from auth_user_groups where user_id=%s ''', (user_id,))
    group_id = cursor_user_group.fetchall()
    group_id = group_id[0][0]
    user_group = Group.objects.filter(id=group_id)
    user_group = user_group[0]
    user_group = str(user_group)
    user_group = user_group.strip()
    
    page = "index"



    cursor_op = connection.cursor()
    # cursor_op.execute(''' select u.id,u.first_name, u.last_name, u.email, g.name from auth_user u, auth_group g, auth_user_groups ag, usercompanymap ucm where u.id=ag.user_id and g.id=ag.group_id and ucm.company_id= %s and u.id=ucm.employee_id and g.name!='Manager' ''',(comp_id,))
    cursor_op.execute(''' select u.id, u.first_name, u.last_name from auth_user u , usermap um where um.company_id=%s and um.supervisor_id=%s and um.employee_id=u.id ''',(comp_id, user_id))
    cursor_op_get = cursor_op.fetchall()

    # batch_cre = Batch.objects.all().filter(status=1)   #created
    batch_asgn = Batch.objects.all().filter(status=2)  #Assigned
    batch_pro = Batch.objects.all().filter(status=3)   #In-Progress
    batch_comp = Batch.objects.all().filter(status=4)  #Completed

    # batch type
    # print(batch_cre[0].name)
    vid_batch = VideoBatch.objects.all().values()
    print(vid_batch)
    # img_batch = ImageBatch.objects.all().values()

    cursor_img = connection.cursor()
    cursor_img.execute(''' select batch_id from imagebatch GROUP BY batch_id ''')
    cursor_img_get = cursor_img.fetchall()
    img_batch = cursor_img_get
    print("cursor query", img_batch)

    cursor_vid = connection.cursor()
    cursor_vid.execute(''' select batch_id from imagebatch GROUP BY batch_id ''')
    cursor_vid_get = cursor_vid.fetchall()
    vid_batch = cursor_vid_get
    print("cursor query", img_batch)


    group = Group.objects.all().filter(id=3)
    name = User.objects.all().filter(id=user_id)
    cursor = connection.cursor()
    cursor.execute(''' select first_name, email from auth_user where id=%s ''',(user_id,))
    cursor_get = cursor.fetchall()

    c2 = connection.cursor()
    c2.execute(''' select * from usercompanymap where employee_id=%s ''',(user_id,))
    c2_get = c2.fetchall()
    comp_id = c2_get[0][3]

    result = UserCompanyMap.objects.raw('SELECT * FROM usercompanymap WHERE employee_id = %s', [user_id])

    index = 0
    
    #chart_Pie
    cursor_pie = connection.cursor()
    cursor_pie.execute('''select status,count(id) as count from batch group by status''')
    c_batch = cursor_pie.fetchall()
    status = []
    cnt = []
    for x in range(len(c_batch)):
        if c_batch[x][0] == 1:
            status.append('Created')
        elif c_batch[x][0] == 2:
            status.append('Assigned')
        elif c_batch[x][0] == 3:
            status.append('Assigned')
        else:
            status.append('Uploaded')
        cnt.append(c_batch[x][1])
    tmp = {"first": status, "second": cnt}

    #chart_line
    cursor_line = connection.cursor()
    cursor_line.execute('''select date(a.published_date) as date,count(1) docs_processed 
    from videobatch a join batch b on a.batch_id=b.id and a.published_date <= b.completeby_date 
    where CAST (a.status AS INTEGER)=2 group by a.published_date order by date''')
    date_list = []
    doc_cnt = []
    c_docs = cursor_line.fetchall()

    for i in range(len(c_docs)):
        date_list.append(c_docs[i][0].strftime("%Y-%m-%d"))  # .strftime("%Y-%m-%d")
        doc_cnt.append(c_docs[i][1])

    return render(request, 'via_manager/index.html', {
        'users': all_data, 'batches': batches, 
         'index':index, 'batchAsgn':batch_asgn, 'batchCre':batch_cre,
         'batchComp':batch_comp, 'asgn_batch':asgn_batch, 'pro_batch':pro_batch, 'comp_batch':comp_batch, 'operators':cursor_op_get,"batch": c_batch, "tmp": tmp,
         "line_labels": date_list, "line_data": doc_cnt, "user_group":user_group,"page":page,"vid_batch":vid_batch,"img_batch":img_batch,"flag":0, "op_ls":op_ls})


class BasicUploadView(View):
    # @login_required
    def get(self, request):
        #user-group
        user_id = request.user.id
        cursor_user_group = connection.cursor()
        cursor_user_group.execute('''select group_id from auth_user_groups where user_id=%s ''', (user_id,))
        group_id = cursor_user_group.fetchall()
        group_id = group_id[0][0]
        user_group = Group.objects.filter(id=group_id)
        user_group = user_group[0]
        user_group = str(user_group)
        user_group = user_group.strip()
        page = "basic_upload"
        cursor = connection.cursor()
        photos_list = cursor.execute('''select * from videoupload where status=0''')

        # photos_list = VideoUpload.objects.filter(status=0)
        print("Photo list", photos_list)
        return render(self.request, 'via_manager/basic_upload.html', {'photos': photos_list, "user_group":user_group
                                                                       ,"page":page})

    # @login_required
    def post(self, request):
        form = VideoUploadForm(self.request.POST, self.request.FILES)
        print("FORM", form)
        # files = request.FILES[0]
        # print("FILES",files)
        # photo = form.save()

        if form.is_valid():
            print("In manager.vews 167")
            photo = form.save()
            print(photo.vid_url)
            print(photo.name)
            data = {'is_valid': True, 'url':str(photo.vid_url)}
        else:
            data = {'is_valid': False}
            print(form.errors)
            print("In manager.vews 172")

        return JsonResponse(data)          



class ImageUploadView(View):
    # @login_required
    def get(self, request):
        #user-group
        user_id = request.user.id
        cursor_user_group = connection.cursor()
        cursor_user_group.execute('''select group_id from auth_user_groups where user_id=%s ''', (user_id,))
        group_id = cursor_user_group.fetchall()
        group_id = group_id[0][0]
        user_group = Group.objects.filter(id=group_id)
        user_group = user_group[0]
        user_group = str(user_group)
        user_group = user_group.strip()
        page = "basic_upload"
        cursor = connection.cursor()
        photos_list = cursor.execute('''select * from imageupload where status=0''')

        # photos_list = VideoUpload.objects.filter(status=0)
        print("Photo list", photos_list)
        return render(self.request, 'via_manager/image_upload.html', {'photos': photos_list, "user_group":user_group
                                                                       ,"page":page})

    # @login_required
    def post(self, request):
        form = ImageUploadForm(self.request.POST, self.request.FILES)
        print("FORM", form)
        # files = request.FILES[0]
        # print("FILES",files)
        # photo = form.save()

        if form.is_valid():
            print("In manager.vews 167")
            photo = form.save()
            data = {'is_valid': True, 'url':str(photo.img_url)}
        else:
            data = {'is_valid': False}
            print(form.errors)
            print("In manager.vews 172")

        return JsonResponse(data)          


@login_required
def vw_batch_files(request):
    user_id = request.user.id
    cursor_user_group = connection.cursor()
    cursor_user_group.execute('''select group_id from auth_user_groups where user_id=%s ''', (user_id,))
    group_id = cursor_user_group.fetchall()
    group_id = group_id[0][0]
    user_group = Group.objects.filter(id=group_id)
    user_group = user_group[0]
    user_group = str(user_group)
    user_group = user_group.strip()
    page = "create_batch"
    # files = VideoUpload.objects.filter(status=0)
    files = VideoUpload.objects.filter(status=0)
    cursor = connection.cursor()
    # files = cursor.execute(''' select * from videoupload where status=0 ''')
    print("Files", files)
    return render(request, "via_manager/createBatch.html", {"vids":files,"user_group":user_group,"page":page})


@login_required
def vw_batch_images(request):
    user_id = request.user.id
    cursor_user_group = connection.cursor()
    cursor_user_group.execute('''select group_id from auth_user_groups where user_id=%s ''', (user_id,))
    group_id = cursor_user_group.fetchall()
    group_id = group_id[0][0]
    user_group = Group.objects.filter(id=group_id)
    user_group = user_group[0]
    user_group = str(user_group)
    user_group = user_group.strip()
    page = "create_batch"
    # files = VideoUpload.objects.filter(status=0)
    files = ImageUpload.objects.filter(status=0).values()
    # cursor = connection.cursor()
    # files = cursor.execute(''' select * from videoupload where status=0 ''')
    print("Files", files)
    return render(request, "via_manager/create_image_batch.html", {"img":files,"user_group":user_group,"page":page})


@login_required
def vw_save_batch(request):

    vid_ids = request.POST.getlist("id[]")
    csrf = request.POST["csrfmiddlewaretoken"]
    VideoUpload.objects.filter(id__in=vid_ids).update(status=1)
    response = {"status": "Video status updated"}

    return JsonResponse(response)


@login_required
def vw_save_image_batch(request):

    img_ids = request.POST.getlist("id[]")
    csrf = request.POST["csrfmiddlewaretoken"]
    ImageUpload.objects.filter(id__in=img_ids).update(status=1)
    response = {"status": "image status updated"}

    return JsonResponse(response)

@login_required
def vw_batch_upload(request):
    user_id = request.user.id
    c2 = connection.cursor()
    c2.execute(''' select * from usercompanymap where employee_id=%s ''',(user_id,))
    c2_get = c2.fetchall()
    comp_id = c2_get[0][3]

    name1 = request.POST.getlist("path_ls[]")[0]
    name2 = request.POST["batch_name"]
    name3 = request.POST["n_images"]
    batch_type = request.POST["batch_type"]
    print("batch_type",batch_type)

    min_char = 8
    max_char = 12
    allchar = string.ascii_letters + string.punctuation + string.digits
    saveId = "".join(choice(allchar) for x in range(randint(min_char, max_char)))

    if request.method == 'POST':
            Batch.objects.create(path=name1, name=name2, count=name3, saveId=saveId, supervisor_id=user_id, company_id=comp_id, batch_type=batch_type)
            batch_id = Batch.objects.all().filter(saveId = saveId).values()
            b_id = batch_id[0]['id']
            response = {"status": "batch details saved with path", "batch_id":b_id}
    else:
            response ={"status ": "batch details could not be saved"}
    return JsonResponse(response)

@login_required
def vw_create_batch(request):
    user_id = request.user.id
    name1 = request.POST.getlist("vid_ls[]")
    name2 = request.POST["batch_name"]
    name3 = request.POST["batch_id"]
    for x in name1:
        print("{} {}".format(x, name2))
        VideoBatch.objects.create(path=x, name=name2, batch_id=name3, user_id = user_id)
   
    some = {"status": "batch saved"}

    return JsonResponse(some)


@login_required
def vw_create_image_batch(request):
    name1 = request.POST.getlist("vid_ls[]")
    name2 = request.POST["batch_name"]
    name3 = request.POST["batch_id"]
    for x in name1:
        print("{} {}".format(x, name2))
        ImageBatch.objects.create(path=x, name=name2, batch_id=name3)
   
    some = {"status": "batch saved"}

    return JsonResponse(some)

@login_required
def vw_update_batch(request):

    b_id = request.POST["b_id"]
    c_date = request.POST["c_date"]
    Batch.objects.filter(id=b_id).update(completeby_date=c_date)
    response = {"status": "Complete By Date updated"}

    return JsonResponse(response)


@login_required
def vw_select_operator(request):

    s_id = request.user.id
    c2 = connection.cursor()
    c2.execute(''' select * from usercompanymap where employee_id=%s ''',(s_id,))
    c2_get = c2.fetchall()
    comp_id = c2_get[0][3]
 
    b_id = request.POST["b_id"]
    o_id = request.POST["o_id"]

    OperatorBatchMapping.objects.create(supervisor_id=s_id, company_id=comp_id, batch_id=b_id, operator_id=o_id)
    Batch.objects.filter(id = b_id).update(status=2,assigned_date=datetime.datetime.now())    
    response = {"status": "operator mapping saved"}
    return JsonResponse(response) 

@login_required
def vw_update_batch_name(request):
    b_id = request.POST["b_id"]
    b_name = request.POST["b_name"]
    Batch.objects.filter(id=b_id).update(name=b_name)
    VideoBatch.objects.filter(id=b_id).update(name=b_name)
    response = {"status": "Batch name updated"}
    return JsonResponse(response)


@login_required
def vw_batch_delete(request):
    if request.method == 'POST':
        id = request.POST["id"]
        vid_batch = VideoBatch.objects.filter(batch_id = id).values()
        img_batch = ImageBatch.objects.filter(batch_id = id).values()

        if not img_batch:
            cursor = connection.cursor()
            cursor.execute('''update videoupload set status=0 where id in (select vu.id from videoupload vu, videobatch vb where concat('/media/',vu.vid_url)=vb.path and vb.batch_id=%s)''', (id,))
        else:
            cursor = connection.cursor()
            cursor.execute('''update imageupload set status=0 where id in (select iu.id from imageupload iu, imagebatch ib where concat('/media/',iu.img_url)=ib.path and ib.batch_id=%s)''', (id,))    
            
        # batch_delete = cursor.fetchall()
        Batch.objects.filter(id=id).delete()
        response = {"status": "Batch Deleted"}
    return JsonResponse(response)


@login_required
def vw_batch_edit(request):
    if request.method == 'POST':
        id = request.POST["id"]
        cursor = connection.cursor()
        cursor.execute('''select b.name,au.first_name,au.last_name,b.completeby_date from batch b,operatorbatchmapping obm, auth_user au where b.id=%s and b.id=obm.batch_id and au.id=obm.operator_id''', (id,))
        batch_details = cursor.fetchall()
    return JsonResponse({"batch_details": batch_details})


@login_required
def vw_batch_update(request):
    if request.method == 'POST':
        id = request.POST["id"]
        b_name = request.POST["b_name"]
        if request.POST["asgn_op"] is '':
            pass
        else:
            asgn_op_id = request.POST["asgn_op"]
            OperatorBatchMapping.objects.filter(batch_id=id).update(operator_id=asgn_op_id)
        
        copm_date = request.POST["copm_date"]
        batch_detail = Batch.objects.filter(id=id).update(name=b_name,completeby_date=copm_date)
        VideoBatch.objects.filter(batch_id__in=id).update(name=b_name)
        # if asgn_op != '':
            # batch_detail.operator_id = asgn_op_id
        # batch_detail.name = b_name
        # batch_detail.completeby_date = copm_date
        # batch_detail.save()
    
    response = {"status": "operator mapping updated"}
    return JsonResponse(response)


#Saving XML file
@login_required
def vw_saveXml(request):
    user_id = request.user.id
    xml_file = request.POST["xml_file"]
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MEDIA_DIR = os.path.join(BASE_DIR, "media/xml")
    print("media", MEDIA_DIR)
    print("cwd", os.getcwd())
    f = open("/home/dynamo/AiTouch/cvat/cvat/media/xml/test.xml", 'w+')
    f.write(xml_file)
    f.close()
    # myfile = File(f)
    
    if Video.objects.create(user_id=user_id, xml=xml_file):
        response = {"status" : "XML saved"}
    else:
        response = {"status" : "XML not saved"}

    return JsonResponse(response)    


@login_required
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

    c2.execute(''' select count(*) from batch b where b.company_id={} and b.supervisor_id={} and b.status in (1,2,3,4) and DATE(b.created_date) BETWEEN '{}' and '{}' '''.format(comp_id, user_id, start_date, end_date))
    created = c2.fetchall()[0][0]

    c2.execute(''' select count(*) from batch b where b.company_id={} and b.supervisor_id={} and b.status=2 and DATE(b.created_date) BETWEEN '{}' and '{}' '''.format(comp_id, user_id, start_date, end_date))
    assigned = c2.fetchall()[0][0]

    c2.execute(''' select count(*) from batch b where b.company_id={} and b.supervisor_id={} and b.status=3 and DATE(b.created_date) BETWEEN '{}' and '{}' '''.format(comp_id, user_id, start_date, end_date))
    prog = c2.fetchall()[0][0]

    c2.execute(''' select count(*) from batch b where b.company_id={} and b.supervisor_id={} and b.status=4 and DATE(b.created_date) BETWEEN '{}' and '{}' '''.format(comp_id, user_id, start_date, end_date))
    completed = c2.fetchall()[0][0]

    final_data = [created, assigned, prog, completed]

    return JsonResponse({"data": final_data})


def vw_completed_batch(request):
    print("complete batch entered")
    b_id = request.POST['b_id']
    b_type = request.POST['b_type']
    print("complete batch entered",b_id)
    print("type batch entered",b_type)
    if b_type is '1':
        batch = ImageBatch.objects.filter(batch_id=b_id).values()
    elif b_type is '2':
        batch = VideoBatch.objects.filter(batch_id=b_id).values()
        
    # print(batch)
  
    return render(request, "via_manager/downloadjson.html", {"image": batch,"b_type":b_type})   
    

def vw_download(request):
    image_id = request.POST['f_id']
    file_type = request.POST['f_type']
    data = {}
    label = {}
    meta = {}
    image = ImageBatch.objects.get(id=image_id)
    images = ImageBatch.objects.all().filter(id=image_id)
    segments = image.segment_set.all()
    print("segments",segments)
    # dimensions of image
    width, height = get_image_dimensions(os.getcwd()+""+image.path)
    print("height",height)
    print("width",width)
    print("image name",image.name)

    labels = [str(s.label.name) for s in segments]
    for s in segments:
        values = [float(x) for x in s.coords.split(',')]  
        label[s.label.name] ={
                    'color': 'red',
                    'co-or':values,
                    }

    data={
        'meta-data':{
                'name': image.name,
                'height':height,
                'width':width,},
        'labels':label,
    }        

    
    json_data = json.dumps(data)
    print("label$$$$$$$$$", label)
    print("json######", json_data)
    f = open("jsonfile.json", "w")
    f.write(json_data)

    # file_ = open(os.path.join(os.getcwd(), 'jsonfile.json'))
    # for f in file_:
    #     print("333333444444",f)

    # response = {"status" : "XML not saved"+image_id}
    # print(response)
    # print(file_)
    # return JsonResponse(response)    

    # with open(os.path.join(os.getcwd(), 'jsonfile.json')) as fh:
    #     response = HttpResponse(fh.read(), content_type="application/force-download")
    #     response['Content-Disposition'] = 'attachment; filename=jsonfile.json'
    #     return response
    path_to_file =os.getcwd()+'jsonfile.json'
    file_name = 'jsonfile.json' 
    response = HttpResponse(content_type='application/force-download') 
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    response['X-Sendfile'] = smart_str(path_to_file)
    return response

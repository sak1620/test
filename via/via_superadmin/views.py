from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
# from django.apps import apps
# model1 = app.get_model('user', 'User')
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from .models import Company, UserCompanyMap, UseCase
from django.template.response import TemplateResponse
from django.db import connection
from django.contrib.auth.decorators import login_required
import datetime
import time


@login_required
def vw_get(request):
    usecaserole = UseCase.objects.all()
    cursor = connection.cursor()
    data = User.objects.all()
    dats = Company.objects.all()
    cursor.execute(
        '''  Select s.company_name, u.id,u.email, u.is_active,s.company_phone_number, s.company_country from auth_user u, Company s where u.email = s.admin_email ''')
    data1 = cursor.fetchall()
    
    return TemplateResponse(request, 'via_superadmin/Superadmin_main.html', {'data': data1, 'usecaserole': usecaserole})
    # It will show the SuperAdmin main screen.
# form submit

@login_required
def vw_upload_logo(request):
    if request.method == 'POST':
        form = request.FILES["logo"]
        m = Company.objects.get(id=8)
        m.company_logo = form
        m.save()
        return render(request, 'sdcs_superadmin/Superadmin_main.html')
    return HttpResponseForbidden('allowed only via POST')




@login_required
def vw_create_admin(request):
    if request.method == 'POST':
        companyname = request.POST['companyname']
        comapnyaddress = request.POST['companyaddress']
        adminemail = request.POST['adminemail']
        adminpassword = request.POST['adminpassword']
        companyphonenumber = request.POST['companyphonenumber']
        companycountry = request.POST['companycountry']
        usecase = request.POST.getlist('usecase[]')
        logo = request.FILES["logo"]

        admin = 'admin'
        user = User.objects.create_user(adminemail, adminemail, adminpassword)
        # add use to a group
        dat = User.objects.filter(email=adminemail)
        suid = dat[0].id
        Company.objects.create(

            company_address=comapnyaddress,
            company_name=companyname,
            company_phone_number=companyphonenumber,
            company_country=companycountry,
            admin_email=adminemail,
            company_logo=logo
        )
        group = Group.objects.get(name=admin)
        user.groups.add(group)
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        cid = Company.objects.filter(admin_email=adminemail).values('id')
        cursor = connection.cursor()
        cursor.execute("INSERT INTO UserCompanyMap (created_date, published_date, company_id, employee_id) values('{}', '{}', {}, {})".format(st, st, cid[0]['id'], suid))
        for i in usecase:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO companyusecasemap (usecase, created_dt, published_date, company_id) values({}, '{}', '{}', {})".format(i, st, st, cid[0]['id'])) 

    status = {"status": suid}
    return redirect("../../../superadmin")

@login_required
def vw_admin_update(request):
    if request.method == 'POST':
        id = request.POST['id']
        company_phone_numbr = request.POST['company_phone_number']
        adminemail = request.POST['adminemail']
        cd = UserCompanyMap.objects.all().filter(employee_id=request.POST["id"]).values('company_id')
        comp_id = cd[0]['company_id']
        up_admin = User.objects.get(id=id)
        if adminemail != '':
            up_admin.username = adminemail
            up_admin.email = adminemail
            up_admin.save()
        
        up_admin1 = Company.objects.get(id=comp_id)
        if company_phone_numbr != '':
            up_admin1.admin_email = adminemail
            up_admin1.company_phone_number = company_phone_numbr
            up_admin1.save()

    status = {"status": "Data updated"}
    return JsonResponse(status)

@login_required
def vw_admin_edit(request):
    if request.method == 'POST':
        dat = User.objects.filter(id=request.POST["id"]).values()
        dat1 = Company.objects.filter(id=request.POST["id"]).values()
    return JsonResponse({"dataEdit": "sucess"})

@login_required
def vw_admin_delete(request):
    if request.method == 'POST':
        cid = UserCompanyMap.objects.all().filter(employee_id=request.POST["id"]).values('company_id')
        comp_id = cid[0]['company_id']
        User.objects.filter(id=request.POST["id"]).delete()
        Company.objects.filter(id=comp_id).delete()

    status = {"admin_delete": "Success"}
    return JsonResponse(status)

@login_required
def vw_toggle_button(request):
    if request.method == 'POST':
        id = request.POST["id"]
        data = User.objects.filter(id=id)
        if data[0].is_active is True:
            tb_user = User.objects.get(id=id)
            tb_user.is_active = 'False'
            tb_user.save()

        elif data[0].is_active is False:
            tb_user = User.objects.get(id=id)
            tb_user.is_active = 'True'
            tb_user.save()
            status = {"user_status_change": "Success"}
            return JsonResponse(status)

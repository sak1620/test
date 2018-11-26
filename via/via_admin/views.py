from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
# from django.apps import apps
# model1 = app.get_model('user', 'User')
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
# from user.models import Role  # User
from django.template.response import TemplateResponse
from django.core.mail import EmailMessage
from django.db import connection
# from .models import UserMap, Company
from via_superadmin.models import *
from django.views import View
from django.contrib.auth.decorators import login_required
import datetime
import time

@login_required
def index(request):
    return render(request, 'sdcs_admin/admin1.html')

# view for create user as manager and admin
# form submit
@login_required
def vw_create_user(request):
    user = request.user
    cursor = connection.cursor()
    cursor.execute(
        ''' select company_id from usercompanymap where employee_id='%s' ''', (user.id,))
    company_id = cursor.fetchall()
    
    firstname = request.POST['firstname']
    lastname = request.POST['lastname']
    email = request.POST['email']
    password = request.POST['password']
    role = request.POST['role_id']
    manager_id = request.POST['managerid']
    managervalue = request.POST['value']
    admin_id = user.id

    user = User.objects.create_user(
        email, email, password, first_name=firstname, last_name=lastname)
    # add use to a group
    group = Group.objects.get(name=role)
    user.groups.add(group)
    user_list = User.objects.filter(email=email).values('id')
    user_id = user_list[0]['id']
    print(company_id)
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO UserCompanyMap (created_date, published_date, company_id, employee_id) values('{}', '{}', {}, {})".format(st, st, company_id[0][0], user_id))

    if role == 'operator':
        UserMap.objects.create(
            admin_id=admin_id,
            employee_id=user_id,
            supervisor_id=manager_id,
            company_id=company_id[0][0]
        )

    status = {"status": "Data Saved"}
    return JsonResponse(status)


# update the details of a user
@login_required
def vw_user_update(request):
    if request.method == 'POST':
        id = request.POST["id"]
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        # role = request.POST['role_id']

        up_user = User.objects.get(id=id)
        up_user.first_name = firstname
        up_user.last_name = lastname
        up_user.email = email
        up_user.save()

    status = {"status": "Data updated"}
    return JsonResponse(status)


# sending datas to display as table
@login_required
def vw_admin_index(request):
    user = request.user
    user_id = request.user.id
    cursor_user_group = connection.cursor()
    cursor_user_group.execute('''select group_id from auth_user_groups where user_id=%s ''', (user_id,))
    group_id = cursor_user_group.fetchall()
    group_id = group_id[0][0]
    user_group = Group.objects.filter(id=group_id)
    user_group = user_group[0]
    user_group = str(user_group)
    user_group = user_group.strip()
    page = "ad_index"

    cursor = connection.cursor()
    cursor.execute(
        ''' select company_id from usercompanymap where employee_id='%s' ''', (user.id,))
    userdata = cursor.fetchall()
    roles = Group.objects.all()
    cursor.execute(
        ''' select u.id,u.first_name, u.last_name, u.is_active, u.email, g.name from auth_user u, auth_group g, auth_user_groups ag, usercompanymap ucm where u.id=ag.user_id and g.id=ag.group_id and ucm.company_id= %s and u.id=ucm.employee_id and g.name!='admin' ''', (userdata[0],))
    tabledata = cursor.fetchall()

    cursor.execute(
        ''' select u.id,u.first_name, u.last_name, g.name from auth_user u, auth_group g, auth_user_groups ag, usercompanymap ucm where u.id=ag.user_id and g.id=ag.group_id and g.name='manager' and ucm.company_id= %s and u.id=ucm.employee_id ''', (userdata[0],))
    managerdata = cursor.fetchall()

    cursor.execute(
        ''' select uc.id, uc.name from companyusecasemap cum, usecase uc where cum.company_id= %s and cum.usecase=uc.id ''', (userdata[0],))
    labelname = cursor.fetchall()

    # cursor.execute(''' select uc.id, cfm.id, cfm.name, cfm.is_active from usecase uc, custfieldmap cfm where cfm.usecase=uc.id and cfm.company_id= %s ''',(userdata[0],))

    # labeldata = cursor.fetchall()
    
    # cursor.execute(''' select fm.usecase_id, fm.id, fm.name from usecase uc, fieldmap fm where uc.id=fm.usecase_id ''')

    # fixedlabel = cursor.fetchall()

    return TemplateResponse(request, 'sdcs_admin/admin1.html', {"data": tabledata, "roles": roles, "mdata": managerdata,
                                                                "user_group":user_group, "page":page, "labelname": labelname})

# displays the detail of the use which is clicked to edit
@login_required
def vw_user_edit(request):
    if request.method == 'POST':
        dat = User.objects.filter(id=request.POST["id"]).values()
    return JsonResponse({"dataEdit": dat[0]})


# deletes the specific user
@login_required
def vw_user_delete(request):
    if request.method == 'POST':
        User.objects.filter(id=request.POST["id"]).delete()

    status = {"user_delete": "Success"}
    return JsonResponse(status)


# to make user active or inactive
@login_required
def vw_toggle_button(request):
    if request.method == 'POST':
        id = request.POST["id"]
        data = User.objects.filter(id=id)
        print(data[0].is_active)
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

# to create custom label
# @login_required
# def vw_label_create(request):
#     if request.method == 'POST':
#         user = request.user
#         cursor = connection.cursor()
#         cursor.execute(
#             ''' select company_id from usercompanymap where employee_id='%s' ''', (user.id,))
#         userdata = cursor.fetchall()
#         labetid = request.POST["usecaseid"]
#         labeltext = request.POST["labeltext"]
#         CustFieldMap.objects.create(name=labeltext, company_id=userdata[0][0], usecase=labetid)

#     status = {"user_status_change": "Success"}
#     return redirect("../../sdcs_admin")


# to make custom label active or inactive
# @login_required
# def vw_toggle_label(request):
#     if request.method == 'POST':
#         id = request.POST["id"]
#         data = CustFieldMap.objects.filter(id=id)
#         if data[0].is_active is 1:
#             tb_user = CustFieldMap.objects.get(id=id)
#             tb_user.is_active = 0
#             tb_user.save()

#         elif data[0].is_active is 0:
#             tb_user = CustFieldMap.objects.get(id=id)
#             tb_user.is_active = 1
#             tb_user.save()
#     status = {"user_status_change": "Success"}
#     return JsonResponse(status)

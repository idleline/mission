'''
    mission.admin.views
    
    Defines the views for application administration
'''
# Flask dpendencies
from flask import Blueprint, render_template, request, redirect
from flask_security import login_required, roles_required, current_user, roles_accepted

# Blueprint declaration & Asset registration
from mission.lib.assets import bundles

#assets.register(bundles)
app_admin = Blueprint('admin', __name__)

# Application level dependencies
#from mission.admin.user import user_edit, user_list, user_profile, list_roles, get_schedule, list_user_groups, job_list, modify_user_role, validate_new_username
from mission.admin.user import *

@app_admin.route('/admin')
@login_required
@roles_required('superuser')
def admin():
    ''' Admin index page handler '''
    
    return render_template('admin.html', users=user_list(), roles=list_roles(), scheduler=get_schedule(), jobs=job_list())

@app_admin.route('/admin/edituser', methods=['POST'])
@login_required
@roles_required('superuser')
def edit_users():
    ''' AJAX Handler for user dataTable '''
    
    return user_edit(request)

@app_admin.route('/admin/modify', methods=['POST'])
@login_required
@roles_required('superuser')
def admin_modify_role():
    ''' AJAX Handler for user dataTable role '''

    return modify_user_role(request)

@app_admin.route('/admin/adduser', methods=['POST'])
@login_required
@roles_required('superuser')
def admin_add_user():
    ''' AJAX Handler to add a new user '''

    return create_new_user(request)

@app_admin.route('/admin/deleteuser', methods=['POST'])
@login_required
@roles_required('superuser')
def admin_delete_user():
    ''' AJAX Handler to delete a user '''

    return delete_user(request)

"""
    : VALIDATE FORM DATA :

"""
@app_admin.route('/admin/validate/username', methods=['POST'])
@login_required
@roles_required('superuser')
def admin_validate_username():
    ''' AJAX Handler for user dataTable role '''

    return validate_new_username(request)

@app_admin.route('/admin/validate/email', methods=['POST'])
@login_required
@roles_required('superuser')
def admin_validate_email():
    ''' AJAX Handler for user dataTable role '''

    return validate_new_email(request)
    
@app_admin.route('/admin/validate/password', methods=['POST'])
@login_required
@roles_required('superuser')
def admin_validate_password():
    ''' AJAX Handler for user dataTable role '''

    return validate_new_password(request)

"""
    : USER MODIFICATIONS :
    
"""
@app_admin.route('/users/create', methods=['POST'])
@login_required
@roles_required('superuser')
def add_user():
    ''' Add user handler '''
    
    create_user(request)
    
    return render_template('admin.html')
   
@app_admin.route('/users/edit', methods=['POST'])
@login_required
@roles_required('superuser')
def admin_edit():
    ''' Edit user handler '''

    return edit_user(request)


@app_admin.route('/users/delete', methods=['POST'])
@login_required
@roles_required('superuser')
def admin_delete():
    ''' Delete user handler '''
    
    return delete_user(request)

@app_admin.route('/users/grouplist', methods=['POST'])
@login_required
@roles_accepted('superuser', 'admin')
def list_groups():
    ''' List all groups '''
    
    return list_user_groups(request)

@app_admin.route('/user/profile', methods=['GET', 'POST'])
@login_required
def profile():
    ''' User view profile Handler '''
    
    return user_profile()

@app_admin.route('/user/alert', methods=['POST'])
@login_required
@roles_required('superuser', 'admin')
def client_alert_handler():
    
    return handle_client_alert_event(request)

@app_admin.route('/unsubscribe')
def email_unsubscribe():
    
    return render_template('unsub.html')


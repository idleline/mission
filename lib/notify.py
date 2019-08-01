'''
    dmarc.lib.notify
'''
from flask_security import current_user
from dmarc.lib.database import db_session
from dmarc.mod_auth.models import User, Role, Notification

def notify_admins(message):
    ''' Notify all Admins '''
    
    superusers = User.query.filter(User.roles.contains(Role.query.filter(Role.name=='superuser').first())).all()
    
    for su in superusers:
        db_session.add(Notification(creator='System', title=message['title'], content=message['body'], user=su, was_read=False))

    db_session.commit()

def notify_users(message):
    
    this_user = current_user.username
    
    notified_users = User.query.filter(User.username!=this_user).all()
    
    for user in notified_users:
        db_session.add(Notification(creator=this_user, title=message['title'], content=message['body'], user=user, was_read=False))
    
    db_session.commit()
    
    
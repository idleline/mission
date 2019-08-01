'''

    dmarc.lib.database

'''
import os, sys

from sqlalchemy import create_engine, exc, event
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import Pool
from sqlalchemy.ext.declarative import declarative_base

'''
    : DATABASE ENGINE CONFIG :
    
    These constants must be set to your database values
    
    Examples:
    
    db_platform = 'mysql'
    db_user = 'web_user'
    db_host = 'sqlserver.example.com'
    db_port = '3306'
    db_name = 'dmarc_db'
    
    engine = mysql://web_user@
'''
############## 
# SET CONFIG #
##############
db_platform = None
db_user = None
db_password = None
db_host = None
db_port = None
db_name = None

db_engine = '{0}://{1}:{2}@{3}:{4}/{5}'.format(db_platform, db_user, db_password, db_host, db_port, db_name)

@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):

    cursor = dbapi_connection.cursor()

    try:
        cursor.execute("SELECT 1")

    except:
        raise exc.DisconnectionError()

    cursor.close()


'''
engine = create_engine(
    db_engine,
    convert_unicode=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=100,
    max_overflow=0,
    )
'''
engine = create_engine('mysql://root@localhost:3306/ruatest')

'''
    : DB SESSION CONFIG :
    
    Set up SQLALCHEMY Session() object
'''
db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
        )
    )

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    Base.metadata.create_all(bind=engine)
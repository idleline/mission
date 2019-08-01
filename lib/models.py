from sqlalchemy import create_engine, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .database import Base, db_session, init_db

'''
    : Association Tables :
    
    Domain to IPAddress (M2M)
    Selector to IPAddress (M2M)

     
'''
domain_ip_table = Table('domain_sending_ip', Base.metadata,
    Column('domain_id', Integer, ForeignKey('domains.id')),
    Column('ip_id', Integer, ForeignKey('ipaddresses.id'))
)

selector_ip_table = Table('selector_ip', Base.metadata,
    Column('selector_id', Integer, ForeignKey('selectors.id')),
    Column('ip_id', Integer, ForeignKey('ipaddresses.id'))
)
'''
class IPAddress(Base):
    __tablename__ = 'ipaddresses'

    id = Column(Integer, primary_key=True)
    address = Column(String(255))
    domains = relationship(
        'Domain',
        secondary = domain_ip_table,
        back_populates = 'ips')
    selectors = relationship(
        'Selector',
        secondary = selector_ip_table,
        back_populates = 'ips')
    dmarc_records = relationship('DMARCRecord', back_populates='source_ip')
'''

class DMARCOrg(Base):
    __tablename__ = 'dmarc_orgs'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    reports = relationship('DMARCReport', back_populates = 'org')

class DMARCReport(Base):
    __tablename__ = 'dmarc_reports'

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey('dmarc_orgs.id'))
    org = relationship('DMARCOrg', back_populates = 'reports')
    report_id = Column(String(255))
    report_date_start = Column(Integer)
    report_date_end = Column(Integer)
    records = relationship('DMARCRecord', back_populates='report')
    policy_domain_id = Column(Integer, ForeignKey('domains.id'))
    policy_domain = relationship('Domain', back_populates='reports')

class DMARCRecord(Base):
    __tablename__ = 'dmarc_records'

    id = Column(Integer, primary_key=True)
    guid = Column(String(128))
    report_id = Column(Integer, ForeignKey('dmarc_reports.id'))
    report = relationship('DMARCReport', back_populates='records')
    count = Column(Integer)
    policy_disposition = Column(String(255), nullable=True)
    policy_dkim = Column(String(64))
    policy_spf = Column(String(64))
    id_header_from_id = Column(Integer, ForeignKey('domains.id'))
    id_header_from = relationship('Domain')
    source_ip_id = Column(Integer, ForeignKey('ipaddresses.id'))
    source_ip = relationship('IPAddress', back_populates='dmarc_records')
    selector_id = Column(Integer, ForeignKey('selectors.id'))
    selector = relationship('Selector', )

class Domain(Base):
    __tablename__ = 'domains'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    ips = relationship(
        'IPAddress',
        secondary = domain_ip_table,
        back_populates = 'domains')
    selectors = relationship('Selector', back_populates='domain')
    reports = relationship('DMARCReport', back_populates='policy_domain')

class Selector(Base):
    __tablename__ = 'selectors'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    domain_id = Column(Integer, ForeignKey('domains.id'))
    domain = relationship('Domain', back_populates='selectors')
    records = relationship('DMARCRecord', back_populates='selector')
    ips = relationship(
        'IPAddress',
        secondary = selector_ip_table,
        back_populates = 'selectors')    

class Registry(Base):
    __tablename__ = 'registries'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    asns = relationship('ASN', back_populates='registry')

class ASN(Base):
    __tablename__ = 'asns'
    
    id = Column(Integer, primary_key=True)
    asn = Column(Integer)
    handle = Column(String(255))
    description = Column(String(255))
    networks = relationship('Network', back_populates='asn')
    country = Column(String(64))
    registry_id = Column(Integer, ForeignKey('registries.id'))
    registry = relationship('Registry', back_populates='asns')

class Network(Base):
    __tablename__ = 'networks'
    
    id = Column(Integer, primary_key=True)
    cidr = Column(String(64))
    asn_id = Column(Integer, ForeignKey('asns.id'))
    asn = relationship('ASN', back_populates='networks')
    ips = relationship('IPAddress', back_populates='network')
    links = Column(String(1024))

class IPAddress(Base):
    __tablename__ = 'ipaddresses'
    __table_args__ = {'extend_existing':True}

    id = Column(Integer, primary_key=True)
    address = Column(String(255))
    domains = relationship(
        'Domain',
        secondary = domain_ip_table,
        back_populates = 'ips')
    selectors = relationship(
        'Selector',
        secondary = selector_ip_table,
        back_populates = 'ips')
    dmarc_records = relationship('DMARCRecord', back_populates='source_ip')
    network_id = Column(Integer, ForeignKey('networks.id'))
    network = relationship('Network', back_populates='ips')

init_db()

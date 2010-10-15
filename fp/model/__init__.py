"""
Database objects
"""
# Import system modules
import sqlalchemy as sa
from sqlalchemy import orm
import hashlib
import datetime
# Import custom modules
from fp.lib import store
from fp.model import meta
from fp.config import parameter


[
    job_defineRegions, 
    job_sampleWindows, 
    job_combineDatasets, 
    job_trainClassifiers, 
    job_scanRegions, 
    job_clusterProbabilities, 
    job_analyzeScans,
] = xrange(7)


# Define methods

def init_model(engine):
    'Call me before using any of the tables or classes in the model'
    meta.Session.configure(bind=engine)
    meta.engine = engine

def hashString(string): 
    'Return a hash of the string'
    return hashlib.sha256(string).digest()


# Define tables

people_table = sa.Table('people', meta.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('username', sa.String(parameter.USERNAME_LENGTH_MAXIMUM), unique=True),
    sa.Column('password_hash', sa.Binary(32)),
    sa.Column('nickname', sa.Unicode(parameter.NICKNAME_LENGTH_MAXIMUM), unique=True),
    sa.Column('email', sa.String(parameter.EMAIL_LENGTH_MAXIMUM), unique=True),
    sa.Column('email_sms', sa.String(parameter.EMAIL_LENGTH_MAXIMUM)),
    sa.Column('is_super', sa.Boolean),
    sa.Column('offset_in_minutes', sa.Integer, default=0),
    sa.Column('rejection_count', sa.Integer, default=0),
)
person_confirmations_table = sa.Table('person_confirmations', meta.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('username', sa.String(parameter.USERNAME_LENGTH_MAXIMUM)),
    sa.Column('password_hash', sa.Binary(32)),
    sa.Column('nickname', sa.Unicode(parameter.NICKNAME_LENGTH_MAXIMUM)),
    sa.Column('email', sa.String(parameter.EMAIL_LENGTH_MAXIMUM)),
    sa.Column('email_sms', sa.String(parameter.EMAIL_LENGTH_MAXIMUM)),
    sa.Column('person_id', sa.ForeignKey('people.id')),
    sa.Column('ticket', sa.String(parameter.TICKET_LENGTH), unique=True),
    sa.Column('when_expired', sa.DateTime),
)
jobs_table = sa.Table('jobs', meta.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('owner_id', sa.ForeignKey('people.id')),
    sa.Column('type', sa.Integer),
    sa.Column('pickled_input', sa.types.Binary),
    sa.Column('pickled_output', sa.types.Binary),
)
images_table = sa.Table('images', meta.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('owner_id', sa.ForeignKey('people.id')),
    sa.Column('name', sa.String(parameter.NAME_LENGTH_MAXIMUM), unique=True),
    sa.Column('is_complete', sa.Boolean, default=False),
    sa.Column('multispectral_path', sa.Text),
    sa.Column('panchromatic_path', sa.Text),
    sa.Column('spatial_reference', sa.Text),
)
regions_table = sa.Table('regions', meta.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('owner_id', sa.ForeignKey('people.id')),
    sa.Column('name', sa.String(parameter.NAME_LENGTH_MAXIMUM), unique=True),
    sa.Column('is_complete', sa.Boolean, default=False),
    sa.Column('image_id', sa.ForeignKey('images.id')),
)
classifiers_table = sa.Table('classifiers', meta.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('owner_id', sa.ForeignKey('people.id')),
    sa.Column('name', sa.String(parameter.NAME_LENGTH_MAXIMUM), unique=True),
)
windows_table = sa.Table('windows', meta.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('owner_id', sa.ForeignKey('people.id')),
    sa.Column('name', sa.String(parameter.NAME_LENGTH_MAXIMUM), unique=True),
    sa.Column('region_id', sa.ForeignKey('regions.id')),
    sa.Column('is_complete', sa.Boolean, default=False),
)
datasets_table = sa.Table('datasets', meta.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('owner_id', sa.ForeignKey('people.id')),
    sa.Column('name', sa.String(parameter.NAME_LENGTH_MAXIMUM), unique=True),
    sa.Column('window_id', sa.ForeignKey('windows.id')),
    sa.Column('is_complete', sa.Boolean, default=False),
)


# Define classes

class Person(object):

    def __init__(self, username, password_hash, nickname, email, email_sms='', is_super=False):
        self.username = username
        self.password_hash = password_hash
        self.nickname = nickname
        self.email = email
        self.email_sms = email_sms
        self.is_super = is_super

    def __repr__(self):
        return "<Person('%s')>" % self.username


class PersonConfirmation(Person):

    def __repr__(self):
        return "<PersonConfirmation('%s')>" % self.username


class Job(store.Pickle):

    def __init__(self, type, owner_id):
        self.type = type
        self.owner_id = owner_id

    def __repr__(self):
        return "<Job('%s')>" % self.name


class Image(object):

    def __init__(self, name, owner_id):
        self.name = name
        self.owner_id = owner_id

    def __repr__(self):
        return "<Image('%s')>" % self.name


class Region(object):

    def __init__(self, name, owner_id, image_id):
        self.name = name
        self.owner_id = owner_id
        self.image_id = image_id

    def __repr__(self):
        return "<Region('%s')>" % self.name


class Classifier(object):

    def __init__(self, name, owner_id):
        self.name = name
        self.owner_id = owner_id

    def __repr__(self):
        return "<Classifier('%s')>" % self.name


class Window(object):

    def __init__(self, name, owner_id, region_id):
        self.name = name
        self.owner_id = owner_id
        self.region_id = region_id

    def __repr__(self):
        return "<Window('%s')>" % self.name


class Dataset(object):

    def __init__(self, name, owner_id, window_id):
        self.name = name
        self.owner_id = owner_id
        self.window_id = window_id

    def __repr__(self):
        return "<Window('%s')>" % self.name


orm.mapper(Person, people_table, properties={
    'jobs': orm.relation(Job, backref='owner'),
})
orm.mapper(PersonConfirmation, person_confirmations_table)
orm.mapper(Job, jobs_table)
orm.mapper(Image, images_table, properties={
    'owner': orm.relation(Person, backref='images'),
})
orm.mapper(Region, regions_table, properties={
    'owner': orm.relation(Person, backref='regions'),
    'image': orm.relation(Image, backref='regions'),
})
orm.mapper(Classifier, classifiers_table, properties={
    'owner': orm.relation(Person, backref='classifiers'),
})
orm.mapper(Window, windows_table, properties={
    'owner': orm.relation(Person, backref='windows'),
    'region': orm.relation(Region, backref='windows'),
})
orm.mapper(Dataset, datasets_table, properties={
    'owner': orm.relation(Person, backref='datasets'),
    'window': orm.relation(Window, backref='datasets'),
})

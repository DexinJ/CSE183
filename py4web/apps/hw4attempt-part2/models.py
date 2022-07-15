"""
This file defines the database models
"""

from .common import db, Field, auth
from pydal.validators import *

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#

def get_user_email():
     return auth.current_user.get('email')

db.define_table(
    'contact',
    Field('first_name', requires=IS_NOT_EMPTY()),
    Field('last_name', requires=IS_NOT_EMPTY()),
    Field('user_email', default=get_user_email)
)

# We do not want these fields to appear in forms by default.
db.contact.id.readable = False
db.contact.id.writable = False
db.contact.user_email.readable = False
db.contact.user_email.writable = False

db.define_table(
    'phoneNumber',
    Field('phone_number','string', requires=IS_NOT_EMPTY()),
    Field('phone_name', 'string', requires=IS_NOT_EMPTY()),
    Field('contact_id', 'reference contact')
)
db.phoneNumber.id.readable = False
db.phoneNumber.id.writable = False
db.phoneNumber.contact_id.readable = False
db.phoneNumber.contact_id.writable = False
db.phoneNumber.contact_id.ondelete = 'CASCADE'

db.commit()
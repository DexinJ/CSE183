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
    Field('first_name'),
    Field('last_name'),
    Field('user_email', default=get_user_email)
)

# We do not want these fields to appear in forms by default.
db.contact.id.readable = False
db.contact.id.writable = False
db.contact.user_email.readable = False
db.contact.user_email.writable = False
db.commit()
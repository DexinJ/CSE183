"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

#from py4web import action, request, abort, redirect, URL
#from yatl.helpers import A
#from .common import db, session, T, cache, auth, authenticated, unauthenticated, flash
import uuid

from py4web import action, request, abort, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner

from yatl.helpers import A
from . common import db, session, T, cache, auth, signed_url


#@unauthenticated("index", "index.html")
url_signer = URLSigner(session)

@action('index')
@action.uses(auth.user, 'index.html')
def index():
    user_email = auth.current_user.get('email')
    rows = db(db.contact.user_email==user_email).select()
    return dict(rows=rows, url_signer=url_signer)

@action('delete_contact/<contact_id>',method=['GET','POST'])
@action.uses(session, db, url_signer.verify())
def delete_contact(contact_id=None):
    p = db.contact[contact_id]
    if p is None:
        redirect(URL('index'))
    else:
        db(db.contact.id == contact_id).delete()
        redirect(URL('index'))
    
@action('add_contact', method=['GET', 'POST'])
@action.uses(auth.user,'contact_form.html', session, db)
def add_contact():
    form = Form(db.contact, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form)

@action('edit_contact/<contact_id>', method=['GET', 'POST'])
@action.uses(auth.user,'contact_form.html', session, db)
def edit_contact(contact_id=None):
    """Note that in the above declaration, the product_id argument must match
    the <product_id> argument of the @action."""
    # We read the product.
    p = db.contact[contact_id]
    if p is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    form = Form(db.contact, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form)
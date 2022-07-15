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
    # For every row that is one of the contacts. 
    # We get all the rows out as a list (see below).
    user_email = auth.current_user.get('email')
    rows = db(db.contact.user_email==user_email).select()
    # and then we iterate on each one
    s=''
    for row in rows:
    # Here we must fish out of the db the phone numbers
    # attached to the contact, and produce a nice string like
    # "354242 (Home), 34343423 (Vacation)" for the contact. 
        #a =db(db.phoneNumber.contact_id == db.contact.id).select()
        a =db(db.phoneNumber.contact_id == row.id).select()
        b=''
        for wor in a:
            #!!
            #if wor.phoneNumber.phone_number is not None and wor.phoneNumber.phone_name is not None:
            #if wor is not None:
                #b=wor
            b+=str(wor.phone_number)+' ('+str(wor.phone_name)+')'
            b+=', '
            
        s=b.rstrip(' ,')
    # and we can simply assign the nice string to a field of the row! 
    # No matter that the field did not originally exist in the database.
        row["phone_numbers"] = s
    # So at the end, we can return "nice" rows, each one with our nice string.
    #return dict(rows=rows, ...)
    
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
@action.uses(url_signer.verify(),'contact_form.html', session, db)
def add_contact():
    form = Form(db.contact, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form)

@action('edit_contact/<contact_id>', method=['GET', 'POST'])
@action.uses(auth,url_signer.verify(),'contact_form.html', session, db)
def edit_contact(contact_id=None):
    """Note that in the above declaration, the product_id argument must match
    the <product_id> argument of the @action."""
    # We read the product.
    p = db.contact[contact_id]
    if p is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('index'))
    user_email = auth.current_user.get('email')
    if p.user_email != user_email:
        redirect(URL('index'))
    form = Form(db.contact, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We always want POST requests to be redirected as GETs.
        redirect(URL('index'))
    return dict(form=form)

@action('edit_phone/<contact_id>')
@action.uses(url_signer.verify(),'phone.html', session, db)
def edit_phone(contact_id=None):
    contact=db(db.contact.id == contact_id).select()
    for row in contact:
        name=row.first_name+' '+row.last_name
        cont=row.id
    rows = db(db.phoneNumber.contact_id == contact_id).select()
    return dict(name=name, rows=rows, contact=cont, url_signer=url_signer)
    
@action('add_number/<contact_id>', method=['GET', 'POST'])
@action.uses(url_signer.verify(),'phone_form.html', session, db)
def add_contact(contact_id=None):
    form = Form([Field('phone'), Field('kind')], csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        db.phoneNumber.insert(phone_number=form.vars["phone"] , phone_name=form.vars["kind"],contact_id=contact_id)
        # We always want POST requests to be redirected as GETs.
        redirect(URL('edit_phone', contact_id, signer=url_signer))
    return dict(form=form)
    
@action('delete_number/<phone_id>/<contact_id>',method=['GET','POST'])
@action.uses(session, db, url_signer.verify())
def delete_number(phone_id=None,contact_id=None):
    p = db.phoneNumber[phone_id]
    if p is None:
        redirect(URL('edit_phone', contact_id, signer=url_signer))
    else:
        db(db.phoneNumber.id == phone_id).delete()
        redirect(URL('edit_phone', contact_id, signer=url_signer))

@action('edit_number/<phone_id>/<contact_id>', method=['GET', 'POST'])
@action.uses(url_signer.verify(),'phone_form.html', session, db)
def edit_contact(phone_id=None,contact_id=None):
    """Note that in the above declaration, the product_id argument must match
    the <product_id> argument of the @action."""
    # We read the product.
    p = db.phoneNumber[phone_id]
    if p is None:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('edit_phone', contact_id, signer=url_signer))
    form = Form([Field('phone'), Field('kind')], csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        db.phoneNumber(phone_id).update_record(phone_number=form.vars["phone"] , phone_name=form.vars["kind"])
        # We always want POST requests to be redirected as GETs.
        redirect(URL('edit_phone', contact_id, signer=url_signer))
    return dict(form=form)
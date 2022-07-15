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

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email

from py4web.utils.form import Form, FormStyleBulma
from .common import Field

url_signer = URLSigner(session)

@action('index')
@action.uses(db, auth, 'index.html')
def index():
    print("User:", get_user_email())
    rows = db(db.contact.user_email == get_user_email()).select()
    return dict(rows=rows, url_signer=url_signer)

@action('add_contact', method=["GET", "POST"]) # the :int means: please convert this to an int.
@action.uses(db, session, auth.user, 'add_contact.html')
def add():
    form = Form(db.contact, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)

@action('edit_contact/<contact_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'edit_contact.html')
def edit(contact_id=None):
    assert contact_id is not None
    assert get_user_email() is not None
    p = db.contact[contact_id]
    print(p)
    if p is None:
        redirect(URL('index'))
    form = Form(db.contact, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)

@action('delete_contact/<contact_id:int>')
@action.uses(db, session, auth.user)
def delete(contact_id=None):
    assert contact_id is not None
    assert get_user_email() is not None
    p = db.contact[contact_id]
    # print(db.bird[bird_id]['bird'])
    # print(db.bird[bird_id]['n_sightings'])
    # db.bird.update_or_insert(
    #     db.bird.bird==db.bird[bird_id]['bird'],
    #     bird=db.bird[bird_id]['bird'],
    #     n_sightings=db.bird[bird_id]['n_sightings'] + 1
    # )
    p.delete_record()
    redirect(URL('index'))

@action('edit_phones/<contact_id:int>')
@action.uses(db, auth.user, 'edit_phones.html')
def editphones(contact_id=None):
    assert contact_id is not None
    assert get_user_email() is not None
    #print("User:", get_user_email())
    rows = db(db.phone.contact_id == contact_id).select()
    return dict(rows=rows, contact_id=contact_id, url_signer=url_signer)

@action('add_phone/<contact_id:int>', method=["GET", "POST"])
@action.uses(db, auth.user, session, 'add_phone.html')
def addphone(contact_id=None):
    assert contact_id is not None
    assert get_user_email() is not None
    #print("User:", get_user_email())
    form = Form([Field('phone_number'), Field('phone_name')], csrf_session=session,
                formstyle=FormStyleBulma)
    if form.accepted:
        db.phone.insert(
            contact_id=contact_id,
            phone_number=form.vars["phone_number"],
            phone_name=form.vars["phone_name"]
        )
        redirect(URL('index'))
    return dict(form=form)

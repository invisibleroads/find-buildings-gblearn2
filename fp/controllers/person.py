"""
Manage user account information.
"""
# Import pylons modules
from pylons import request, session, tmpl_context as c, config
from pylons.controllers.util import redirect_to
from pylons.decorators import jsonify
import formencode
from formencode import validators, htmlfill
# Import system modules
import logging; log = logging.getLogger(__name__)
import datetime
import sqlalchemy as sa
import recaptcha.client.captcha as captcha
import StringIO
import re
# Import custom modules
from fp import model
from fp.model import meta
from fp.config import parameter
from fp.lib import mail, store, helpers as h
from fp.lib.base import BaseController, render


class PersonController(BaseController):
    """
    Handle registration, authentication and account modification.
    """

    def index(self):
        """
        Show information about people registered in the database.
        """
        # Initialize
        query = meta.Session.query(model.Person)
        # Get
        c.person_count = query.count()
        c.random_people = query.order_by(sa.func.random()).limit(10).all()
        # Return
        return render('/people/index.mako')

    def register(self):
        """
        Show account registration page.
        """
        c.title = 'Registration'
        c.button_label = 'Register'
        c.save_url_name = 'person_register_'
        c.success_message = 'Please check your email to create your account.'
        return render('/people/change.mako')

    @jsonify
    def register_(self):
        """
        Store proposed changes and send confirmation email.
        """
        # Return
        return changeAccount(dict(request.POST), 'registration', '/people/confirm_email.mako')

    def confirm(self, ticket):
        """
        Confirm changes.
        """
        # Send feedback
        confirmation = executePersonConfirmation(ticket)
        # If the confirmation exists,
        if confirmation:
            messageCode = 'updated' if confirmation.person_id else 'created'
        else:
            messageCode = 'expired'
        # Return
        return redirect_to('person_login', url=h.encodeURL('/'), messageCode=messageCode)

    def update(self):
        """
        Show account update page.
        """
        # If the person is not logged in,
        if not h.isPerson():
            return ''
        # Get
        person = meta.Session.query(model.Person).get(session['personID'])
        # Render
        c.title = 'Update'
        c.button_label = 'Update'
        c.save_url_name = 'person_update_'
        c.success_message = 'Please check your email to finalize changes to your account.'
        form = render('/people/change.mako')
        # Return
        return htmlfill.render(form, {
            'username': person.username,
            'nickname': person.nickname,
            'email': person.email,
            'email_sms': person.email_sms,
        })

    @jsonify
    def update_(self):
        """
        Send update confirmation email
        """
        # If the person is not logged in,
        if not h.isPerson():
            return {'isOk': 0}
        # Load
        person = meta.Session.query(model.Person).get(session['personID'])
        # Return
        return changeAccount(dict(request.POST), 'update', '/people/confirm_email.mako', person)

    def login(self, url=h.encodeURL('/')):
        """
        Show login form
        """
        c.messageCode = request.GET.get('messageCode')
        c.url = h.decodeURL(url)
        c.publicKey = config['extra']['recaptcha']['public']
        return render('/people/login.mako')

    @jsonify
    def login_(self):
        """
        Process login credentials.
        """
        # Check username
        username = str(request.POST.get('username', ''))
        person = meta.Session.query(model.Person).filter_by(username=username).first()
        # If the username does not exist,
        if not person:
            return dict(isOk=0)
        # Check password
        password_hash = model.hashString(str(request.POST.get('password', '')))
        # If the password is incorrect,
        if password_hash != StringIO.StringIO(person.password_hash).read():
            person.rejection_count += 1
            meta.Session.commit()
            return dict(isOk=0)
        # If there have been too many rejections,
        if person.rejection_count >= parameter.REJECTION_LIMIT:
            # Expect a recaptcha
            challenge = request.POST.get('recaptcha_challenge_field', '')
            response = request.POST.get('recaptcha_response_field', '')
            privateKey = config['extra']['recaptcha']['private']
            remoteIP = request.environ['REMOTE_ADDR']
            # Validate recaptcha
            result = captcha.submit(challenge, response, privateKey, remoteIP)
            # If the recaptcha is invalid,
            if not result.is_valid:
                return dict(isOk=0)
        # Compute offset_in_minutes
        clientTimezoneOffset = int(request.POST.getone('offset_in_minutes'))
        clientNow = datetime.datetime.utcnow() - datetime.timedelta(minutes=clientTimezoneOffset)
        serverNow = datetime.datetime.now()
        offset_in_minutes = (clientNow - serverNow).seconds / 60
        # Round to the nearest five minutes modulo the number of minutes in a day
        offset_in_minutes = (int(round(offset_in_minutes / 5.)) * 5) % 1440
        # Save session
        session['offset_in_minutes'] = offset_in_minutes
        session['personID'] = person.id
        session['nickname'] = person.nickname
        session['is_super'] = person.is_super
        session.save()
        # Save person
        person.offset_in_minutes = offset_in_minutes
        person.rejection_count = 0
        meta.Session.commit()
        # Return
        return dict(isOk=1)

    def logout(self, url=h.encodeURL('/')):
        """
        Logout
        """
        # If the person is logged in,
        if h.isPerson():
            del session['offset_in_minutes']
            del session['personID']
            del session['nickname']
            del session['is_super']
            session.save()
        # Redirect
        return redirect_to(h.decodeURL(url))

    @jsonify
    def reset(self):
        """
        Reset password
        """
        # Get email
        email = request.POST.get('email')
        # Try to load the person
        person = meta.Session.query(model.Person).filter(model.Person.email==email).first()
        # If the email is not in our database,
        if not person: 
            return {'isOk': 0}
        # Reset account
        c.password = store.makeRandomString(parameter.PASSWORD_LENGTH_AVERAGE)
        return changeAccount(dict(
            username=person.username,
            password=c.password,
            nickname=person.nickname,
            email=person.email,
            email_sms=person.email_sms,
        ), 'reset', '/people/confirm_email.mako', person)


# Validators

class Unique(validators.FancyValidator):
    """
    Check whether a value exists in the database.
    """

    def __init__(self, fieldName, errorMessage):
        """
        Store fieldName and errorMessage.
        """
        super(Unique, self).__init__()
        self.fieldName = fieldName
        self.errorMessage = errorMessage

    def _to_python(self, value, person):
        """
        Check whether the value is unique.
        """
        # If the person is new or the value changed,
        if not person or getattr(person, self.fieldName) != value:
            # Make sure the value is unique
            if meta.Session.query(model.Person).filter(getattr(model.Person, self.fieldName)==value).first():
                # Raise
                raise formencode.Invalid(self.errorMessage, value, person)
        # Return
        return value

class SecurePassword(validators.FancyValidator):
    """
    Check whether a password is secure.
    """

    def _to_python(self, value, person):
        """
        Check whether a password is strong enough.
        """
        if len(set(value)) < 4:
            raise formencode.Invalid('That password needs more variety', value, person)
        if not re.search(r'\d', value):
            raise formencode.Invalid('Passwords must contain numbers', value, person)
        if not re.search(r'[a-zA-Z]', value):
            raise formencode.Invalid('Passwords must contain letters', value, person)
        return value

class PersonForm(formencode.Schema):
    """
    Validate user credentials.
    """

    username = formencode.All(
        validators.String(
            min=parameter.USERNAME_LENGTH_MINIMUM,
            max=parameter.USERNAME_LENGTH_MAXIMUM,
        ),
        Unique('username', 'That username already exists'),
    )
    password = formencode.All(
        validators.MinLength(parameter.PASSWORD_LENGTH_MINIMUM, not_empty=True), 
        SecurePassword(),
    )
    nickname = formencode.All(
        validators.PlainText(), 
        validators.UnicodeString(
            min=parameter.NICKNAME_LENGTH_MINIMUM, 
            max=parameter.NICKNAME_LENGTH_MAXIMUM,
        ),
        Unique('nickname', 'That nickname already exists'),
    )
    email = formencode.All(
        validators.Email(not_empty=True),
        Unique('email', 'That email is reserved for another account'),
    )
    email_sms = formencode.All(
        validators.Email(),
        Unique('email_sms', 'That SMS address is reserved for another account'),
    )


# Helpers

def changeAccount(valueByName, action, templatePath, person=None):
    """
    Validate values and send confirmation email if values are okay.
    """
    try:
        # Validate form
        form = PersonForm().to_python(valueByName, person)
    except formencode.Invalid, error:
        return {'isOk': 0, 'errorByID': error.unpack_errors()}
    else:
        # Purge expired confirmations
        purgeExpiredPersonConfirmations()
        # Prepare confirmation
        confirmation = model.PersonConfirmation(form['username'],
            model.hashString(form['password']), form['nickname'],
            form['email'], form['email_sms'])
        confirmation.person_id = person.id if person else None
        confirmation.ticket = store.makeRandomUniqueTicket(parameter.TICKET_LENGTH, meta.Session.query(model.PersonConfirmation))
        confirmation.when_expired = datetime.datetime.now() + datetime.timedelta(days=parameter.TICKET_LIFESPAN_IN_DAYS)
        meta.Session.add(confirmation) 
        meta.Session.commit()
        # Prepare recipient
        toByValue = dict(nickname=form['nickname'], email=form['email'])
        # Prepare subject
        subject = '[%s] Confirm %s' % (parameter.SITE_NAME, action)
        # Prepare body
        c.ticket = confirmation.ticket
        c.when_expired = confirmation.when_expired
        c.username = form['username']
        c.action = action
        body = render(templatePath)
        # Send
        try:
            mail.sendMessage(config['extra']['mail_support'], toByValue, subject, body)
        except mail.Error:
            return dict(isOk=0, errorByID={
                'status': 'Unable to send confirmation email; please try again later.'
            })
        # Return
        return {'isOk': 1}


def purgeExpiredPersonConfirmations():
    """
    Delete confirmations that have expired
    """
    meta.Session.execute(model.person_confirmations_table.delete().where(model.PersonConfirmation.when_expired<datetime.datetime.now()))

def executePersonConfirmation(ticket):
    """
    Move changes from the PersonConfirmation table into the Person table
    """
    # Query
    confirmation = meta.Session.query(model.PersonConfirmation).filter(model.PersonConfirmation.ticket==ticket).filter(model.PersonConfirmation.when_expired>=datetime.datetime.now()).first()
    # If the ticket exists,
    if confirmation:
        # Create person
        if confirmation.person_id:
            person = meta.Session.query(model.Person).get(confirmation.person_id)
            person.username = confirmation.username
            person.password_hash = confirmation.password_hash
            person.nickname = confirmation.nickname
            person.email = confirmation.email
            person.email_sms = confirmation.email_sms
        else:
            meta.Session.add(model.Person(confirmation.username, confirmation.password_hash, confirmation.nickname, confirmation.email, confirmation.email_sms))
        # Delete ticket
        meta.Session.delete(confirmation)
        # Commit
        meta.Session.commit()
    # Return
    return confirmation

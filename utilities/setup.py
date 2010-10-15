#!/usr/bin/env python2.6
"""
Add an account
"""
# Import system modules
import getpass
import ConfigParser
import os
# Import custom modules
import script_process
from fp import model
from fp.model import meta


def run():
    """
    Add an account
    """
    # Initialize
    personPacks = []
    newPersonCount = 0
    peoplePath = '.people.cfg'
    # If a configuration file exists,
    if os.path.exists(peoplePath):
        configuration = ConfigParser.ConfigParser()
        configuration.read(peoplePath)
        for sectionName in configuration.sections():
            personPacks.append((
                configuration.get(sectionName, 'username'),
                configuration.get(sectionName, 'password'),
                sectionName,
                configuration.get(sectionName, 'email'),
                configuration.get(sectionName, 'email_sms'),
                configuration.get(sectionName, 'is_super', '').capitalize() == 'True',
            ))
    # Otherwise, 
    else:
        print 'Missing person configuration path: ' + peoplePath
        # Prompt for information
        personPacks.append((
            raw_input('Username: '),
            getpass.getpass(),
            raw_input('Nickname: '),
            raw_input('Email: '),
            raw_input('Email SMS: '),
            raw_input('Super (y/[n])? ').lower() == 'y'))
    # For each person,
    for personPack in personPacks:
        # Extract
        username, password, nickname, email, email_sms, is_super = personPack
        # If the person exists,
        if meta.Session.query(model.Person).filter_by(username=username).first():
            continue
        # Add the person
        person = model.Person(
            username=username, 
            password_hash=model.hashString(password), 
            nickname=unicode(nickname), 
            email=email, 
            email_sms=email_sms,
            is_super=is_super,
        )
        meta.Session.add(person)
        newPersonCount += 1
    # Return
    return '%s people added' % newPersonCount


# If we are running standalone,
if __name__ == '__main__':
    # Parse
    optionParser = script_process.buildOptionParser()
    options, arguments = optionParser.parse_args()
    # Initialize
    script_process.connect(options)
    # Run
    print run()
    meta.Session.commit()

"""
Make sure that we can send messages using IMAP.
"""
# Import pylons modules
from pylons import config
# Import system modules
import imaplib
import unittest
import random
# Import custom modules
from fp.lib import mail, store


class TestMail(unittest.TestCase):
    """
    Test mail helper library.
    """

    def test_sendMessage(self):
        """
        Ensure that we can send messages successfully.
        """
        # Prepare
        fromPack = config['extra']['mail_support']
        toPack = config['extra']['mail_test']
        subject = store.makeRandomString(16)
        # Send message
        mail.sendMessage(fromPack, toPack, subject, '')
        # Check that the message exists on the server
        server = imaplib.IMAP4(toPack['imap'])
        server.login(toPack['username'], toPack['password'])
        server.select()
        self.assertNotEqual(server.search(None, '(SUBJECT "%s")' % subject)[1], [''])

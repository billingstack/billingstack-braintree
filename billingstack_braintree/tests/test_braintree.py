import os.path
import unittest2

from billingstack.openstack.common import jsonutils
from billingstack.openstack.common import log
from billingstack.tests.base import TestCase

from billingstack_braintree.provider import BraintreeProvider


LOG = log.getLogger(__name__)


PATH = os.path.expanduser('~')
CREDS_PATH = os.environ.get('BRAINTREE_RC', PATH + '/braintree.json')


def credentials():
    if not os.path.exists(CREDS_PATH):
        LOG.warn('Credentials path %s not found, skipping.' % CREDS_PATH)
        return False
    f = open(CREDS_PATH)
    return jsonutils.loads(f.read())


@unittest2.skipUnless(credentials(), "Missing Braintree Credentialsi")
class BraintreeTestCase(TestCase):
    __test__ = True
    def setUp(self):
        cfg = {'environment': 'sandbox'}
        cfg.update(credentials())

        self.provider = BraintreeProvider(cfg)
        super(BraintreeTestCase, self).__init__()

    def test_account_create(self):
        pass

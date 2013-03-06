import os.path
import unittest2

from braintree.exceptions import NotFoundError

from billingstack.openstack.common import jsonutils
from billingstack.openstack.common import log
from billingstack.tests.payment_gateway.base import ProviderTestCase

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
class BraintreeTestCase(ProviderTestCase):
    __test__ = True

    def setUp(self):
        cfg = {'environment': 'sandbox'}
        cfg.update(credentials())

        self.pgp = BraintreeProvider(cfg)
        super(BraintreeTestCase, self).setUp()

    def tearDown(self):
        super(BraintreeTestCase, self).tearDown()
        try:
            self.pgp.account_delete(self.customer['id'])
        except NotFoundError:
            return

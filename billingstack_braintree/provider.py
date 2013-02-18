import braintree

from billingstack.payment_gateway.base import Provider


class BraintreeProvider(Provider):
    __plugin_name__ = 'braintree'
    __title__ = 'Braintree PGP'
    __description__ = 'Braintree - www.braintree.com creditcard gateway'

    env_map = {
        'production': braintree.Environment.Production,
        'development': braintree.Environment.Development,
        'sandbox': braintree.Environment.Sandbox}

    def get_client(self):
        env = self.env_map.get(self.config['environment'], 'production')

        braintree.Configuration.configure(
            env,
            merchant_id=self.config['merchant_id'],
            public_key=self.config['public_key'],
            private_key=self.config['private_key'])
        return braintree

    def account_create(self, values):
        result = braintree.Customer.create(values)

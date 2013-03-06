import braintree

from billingstack import exceptions
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

    @staticmethod
    def methods():
        return [
            {"name": "visa", "type": "creditcard"},
            {"name": "mastercard", "type": "creditcard"}]

    def purge(self, resource, local, remote):
        """
        Given a resource and local and remote dicts of it's we can delete what
        exists on the remote side and keep what's local

        :param resource: A Braintree resource like Customer
        :param local: The local IDs to compare against
        :param remote: The remote id's to compare with
        """
        for id in remote:
            if id not in local:
                resource.delete(id)

    def _account_to_bs(self, obj):
        return {"id": obj.id}

    def account_add(self, values):
        obj = braintree.Customer.create({'id': values['id']}).customer
        return self._account_to_bs(obj)

    def account_list(self):
        result = braintree.Customer.all()
        return [self._account_to_bs(i) for i in result.items]

    def account_get(self, id_):
        obj = braintree.Customer.find(id_)
        return self._account_to_bs(obj)

    def account_delete(self, id_):
        braintree.Customer.delete(id_)

    def _method_to_bs(self, obj):
        """
        Helper to convert the data from BT to BS
        """
        data = {
            'id': obj.token,
            'customer_id': obj.customer_id,
            'type': obj.card_type.lower(),
            'expires': obj.expiration_date
        }
        return data

    def _method_to_bt(self, values):
        """
        Helper to convert the data from BS to BT
        """
        return {
            'token': values['id'],
            'customer_id': values['customer_id'],
            'number': values['identifier'],
            'expiration_date': values['expires'],
            'cardholder_name': values['data']['cardholder'],
            'cvv': values['data']['cvv']}

    def payment_method_add(self, values, verify=False):
        data = self._method_to_bt(values)
        data['options'] = {'verify_card': verify}
        obj = braintree.CreditCard.create(data).credit_card
        return self._method_to_bs(obj)

    def payment_method_list(self, account_id):
        result = braintree.Customer.find(account_id)
        return dict([(i.token, self._method_to_bs(i)) for i in result.credit_cards])

    def payment_method_get(self, id_):
        obj = braintree.CreditCard.find(id_)
        return self._method_to_bs(obj)

    def payment_method_delete(self, id_):
        braintree.CreditCard.delete(id_)

    def _transaction_to_bt(self, values):
        return {
            'order_id': values['id'],
            'amount': values['values'],
            'customer_id': values['customer_id']}

    def _transaction_to_bs(self, obj):
        return {'id': obj.order_id}

    def transaction_add(self, values, settle=True):
        data = self._transaction_to_bt(values)
        data['options']['submit_for_settlement'] = settle

        braintree.Transaction.sale(data)

    def transaction_show(self, id_):
        obj = braintree.Transaction.find(id_)
        return self._transaction_to_bs(obj)

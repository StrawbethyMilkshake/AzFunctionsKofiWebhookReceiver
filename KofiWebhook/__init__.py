import azure.functions as func

import os
import json
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity


def main(req: func.HttpRequest) -> func.HttpResponse:
    table_service = TableService(connection_string=os.environ["WEBSITE_CONTENTAZUREFILECONNECTIONSTRING"])

    # Read the verification token from environment variables
    expected_token = os.environ["KOFI_VERIFICATION_TOKEN"]

    # Parse the request data
    data_str = req.form.get('data')
    data = json.loads(data_str)

    # Verify the request
    received_token = data['verification_token']
    if received_token != expected_token:
        return func.HttpResponse(status_code=401)

    # Extract payment information
    payment_type = data['type']
    payment_amount = float(data['amount'])
    payment_currency = data['currency']
    payment_id = data['kofi_transaction_id']

    # Set the table name depending on the payment type
    if payment_type == 'Donation':
        table_name = 'donations'
    elif payment_type == 'Subscription':
        table_name = 'subscriptions'
    elif payment_type == 'Commission':
        table_name = 'commissions'
    elif payment_type == 'Shop Order':
        table_name = 'shop_orders'
    else:
        return func.HttpResponse(status_code=400)

    # Log the payment to the Azure Table Storage table
    table_service.create_table(table_name.replace('_', ''))
    payment_entity = Entity()
    payment_entity.PartitionKey = payment_currency
    payment_entity.paymentAmount = payment_amount

    # Add fields from the JSON
    payment_entity.MessageId = data['message_id']
    payment_entity.Timestamp = data['timestamp']
    payment_entity.IsPublic = data['is_public']
    payment_entity.FromName = data['from_name']
    payment_entity.Message = data['message']
    payment_entity.Url = data['url']
    payment_entity.Email = data['email']
    payment_entity.Currency = data['currency']
    payment_entity.IsSubscriptionPayment = data['is_subscription_payment']
    payment_entity.IsFirstSubscriptionPayment = data['is_first_subscription_payment']
    payment_entity.KofiTransactionId = data['kofi_transaction_id']
    payment_entity.TierName = data['tier_name']

    # Expand the shipping field
    if data['shipping'] is not None:
        payment_entity.ShippingFullName = data['shipping']['full_name']
        payment_entity.ShippingStreetAddress = data['shipping']['street_address']
        payment_entity.ShippingCity = data['shipping']['city']
        payment_entity.ShippingStateOrProvince = data['shipping']['state_or_province']
        payment_entity.ShippingPostalCode = data['shipping']['postal_code']
        payment_entity.ShippingCountry = data['shipping']['country']
        payment_entity.ShippingCountryCode = data['shipping']['country_code']
        payment_entity.ShippingTelephone = data['shipping']['telephone']

    if data['shop_items'] is not None:
        if os.environ["SPLIT_SHOP_ITEM_RECORDS"] == '1':
            for item in data['shop_items']:
                payment_entity.RowKey = f"{payment_id}+{item['direct_link_code']}+{item['variation_name']}"
                payment_entity.DirectLinkCode = item['direct_link_code']
                payment_entity.VariationName = item['variation_name']
                payment_entity.Quantity = item['quantity']
                table_service.insert_entity(table_name.replace('_', ''), payment_entity)
        else:
            payment_entity.RowKey = payment_id
            payment_entity.Items = str(data['shop_items'])
            table_service.insert_entity(table_name.replace('_', ''), payment_entity)
    else:
        payment_entity.RowKey = payment_id
        table_service.insert_entity(table_name.replace('_', ''), payment_entity)

    # Return a success response
    return func.HttpResponse(status_code=200)

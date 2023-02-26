# Azure Functions Ko-fi Webhook Receiver

This is an Azure Function that receives webhook notifications from Ko-fi, a platform that allows content creators to receive payments from their audience. The function extracts payment information from the webhook notification and logs it to an Azure Table Storage table.

## Prerequisites
Before deploying and running this function, make sure you have the following:

 - An Azure account with an active subscription.
 - A Ko-fi account.
 - An Azure Table Storage account.

## Configuration
To configure the function, you need to set the following environment variables:

 - WEBSITE_CONTENTAZUREFILECONNECTIONSTRING: The connection string for your Azure Table Storage account.
 - KOFI_VERIFICATION_TOKEN: The verification token provided by Ko-fi.

Additionally, you may set the following environment variables to customize the behavior of the function:

 - SPLIT_SHOP_ITEM_RECORDS: If set to 1, each item in a shop order will be logged as a separate entity in the Azure Table Storage table.
> Note: Since Ko-fi only sends the total order cost we cannot break down the amount spent on each item

## Usage
To use this function, you need to configure a webhook notification in your Ko-fi account. Follow these steps:

1. Log in to your Ko-fi account.
2. Navigate to the [API Settings](https://ko-fi.com/manage/webhooks) page.
3. Enter the URL of your Azure Function in the "Webhook URL" field.
4. Copy the verification token provided by Ko-fi under the "Advanced" section.
5. Set the `KOFI_VERIFICATION_TOKEN` environment variable in the function app configuration.
6. Click on the webhook test buttons in the Ko-fi webhooks page.
7. Verify that the relevant tables have been created and that the records exist. 
> Note: There will only be one record for the subscription test buttons as they share a transaction ID

After configuring the webhook, your Azure Function will receive notifications whenever a payment is made to your Ko-fi account. The payment information will be logged to the Azure Table Storage table that you specified in the function code.
import json
import time
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import stripe
from django.views.decorators.csrf import csrf_exempt

from service.models import Order, Transaction



# Using Django
@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    signature_header = request.META['HTTP_STRIPE_SIGNATURE']
    payload = request.body
    event = None
      
    try:
        event = stripe.Webhook.construct_event(payload, signature_header, settings.STRIPE_WEBHOOK)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
      
    if event['type'] == 'checkout.session.completed':
      # Payment is successful and the subscription is created.
      # You should provision the subscription and save the customer ID to your database.
      session = event['data']['object']     
   
      session_id = session.get('id', None)
      subscription_id = session.get('subscription', None)
      invoice_id = session.get('invoice', None)
      payment_intent = session.get('payment_intent', None)
      
      customer = session.get('customer', None)
      order_id = session.get('client_reference_id', None)
      
      
      time.sleep(15)
      
      order = Order.objects.get(gateway_reference = session_id)      
      order.status = 'processing'
      
      
      if subscription_id is not None:
        # subscription = Subscription.objects.get(gateway_reference = subscription_id)
        order.subscription_active = True   
        
      order.save()   
      
      if payment_intent is not None:
        transaction = Transaction.objects.get(gateway_reference = payment_intent)
       
      elif invoice_id is not None:
        transaction = Transaction.objects.get(gateway_invoice = invoice_id)
      transaction.payment_status = 'captured'          
      transaction.save()
      
      # receipt email to customer.
      
      # create a project
      
      # notification to admin
    elif event['type'] == 'invoice.paid':
      # Continue to provision the subscription as payments continue to be made.
      # Store the status in your database and check when a user accesses your service.
      # This approach helps you avoid hitting rate limits.
      print('data')
    elif event['type'] == 'invoice.payment_failed':
      # The payment failed or the customer does not have a valid payment method.
      # The subscription becomes past_due. Notify your customer and send them to the
      # customer portal to update their payment information.
      print('data')
    elif event.type == 'customer.subscription.created':
        # Handle subscription created event
        pass
    elif event.type == 'customer.subscription.updated':
        # Handle subscription updated event
        pass
    elif event.type == 'customer.subscription.deleted':
        # Handle subscription deleted event
        pass
   
    
    elif event.type == 'customer.updated':
        # Handle customer information update event
        pass

    else:
      print('Unhandled event type {}'.format(event['type']))
        
    # print(event)
      
    # if event['type'] == 'checkout.session.completed':
      
      
    #   session = event['data']['object']
      
    #   print(session)
    #   session_id = session.get('id', None)
    #   subscription_id = session.get('subscription', None)
    #   invoice_id = session.get('invoice', None)
    #   payment_intent = session.get('payment_intent', None)
      
    #   customer = session.get('customer', None)
    #   order_id = session.get('client_reference_id', None)
      
      
    #   time.sleep(15)
      
    #   order = Order.objects.get(gateway_reference = session_id)      
    #   order.order_status = 'processing'
    #   order.save()
      
    #   if subscription_id is not None:
    #     subscription = Subscription.objects.get(gateway_reference = subscription_id)
    #     subscription.is_active = True      
      
    #   if payment_intent is not None:
    #     transaction = Transaction.objects.get(gateway_reference = payment_intent)
    #     transaction.payment_status = 'captured'
    #   elif invoice_id is not None:
    #     transaction = Transaction.objects.get(gateway_invoice = invoice_id)
    #     transaction.payment_status = 'captured'
          
    #   transaction.save()
      
    #   # receipt email to customer.
      
    #   # create a project
      
    #   # notification to admin
      
      
      
      
    #   #   # Save a copy of the order in your own database. This will give you a record of the order, even if the Stripe Checkout session expires or is canceled.
    #   #   # Send the customer a receipt email. This will confirm the order and provide the customer with their order details.
    #   #   # Fulfill the order. This may involve shipping the product, providing access to a digital product, or completing some other action.
    #   #   # Update your inventory levels. If you are selling physical products, you will need to update your inventory levels to reflect the fact that one has been sold.
    #   #   # Send a notification to your team. This may be useful for alerting your team that a new order has been placed.
      
    # elif event['type'] == 'invoice.payment_succeeded':
    #   # stripe.webhooks.acknowledge(event['id'])
      
    #   invoice = event['data']['object']
    #   print(invoice)
      
    #   invoice_id = invoice.get('id')
    #   hosted_invoice_id = invoice.get('hosted_invoice_url')
    #   invoice_pdf = invoice.get('invoice_pdf')
      
    #   # Acknowledge the event. This tells Stripe that you have received the event and that you are processing it. You can do this by calling the stripe.webhooks.acknowledge() method with the event ID.
    #   # Update your records. This may involve updating your customer database, inventory system, or other systems that are affected by invoices.
    #   # Send the customer a notification. This notification can inform the customer that their invoice has been paid.
    #   # Provide the customer with access to the goods or services that they have paid for. This may involve activating their subscription, shipping their product, or providing them with access to digital goods.
            
      
    # elif event['type'] == 'invoice.payment_failed':
    #   invoice = event['data']['object']
      
      
    # elif event['type'] == 'customer.subscription.updated':
    #   subscription = event['data']['object']
      
      
    # elif event['type'] == 'customer.subscription.deleted':
    #   subscription = event['data']['object']
    
    
    # # Handle the event
    # if event['type'] == 'account.updated':
    #   account = event['data']['object']
    # elif event['type'] == 'account.external_account.created':
    #   external_account = event['data']['object']
    # elif event['type'] == 'account.external_account.deleted':
    #   external_account = event['data']['object']
    # elif event['type'] == 'account.external_account.updated':
    #   external_account = event['data']['object']
    # elif event['type'] == 'balance.available':
    #   balance = event['data']['object']
    # elif event['type'] == 'billing_portal.configuration.created':
    #   configuration = event['data']['object']
    # elif event['type'] == 'billing_portal.configuration.updated':
    #   configuration = event['data']['object']
    # elif event['type'] == 'billing_portal.session.created':
    #   session = event['data']['object']
    # elif event['type'] == 'capability.updated':
    #   capability = event['data']['object']
    # elif event['type'] == 'cash_balance.funds_available':
    #   cash_balance = event['data']['object']
    # elif event['type'] == 'charge.captured':
    #   charge = event['data']['object']
    # elif event['type'] == 'charge.expired':
    #   charge = event['data']['object']
    # elif event['type'] == 'charge.failed':
    #   charge = event['data']['object']
    # elif event['type'] == 'charge.pending':
    #   charge = event['data']['object']
    # elif event['type'] == 'charge.refunded':
    #   charge = event['data']['object']
    # elif event['type'] == 'charge.succeeded':
    #   charge = event['data']['object']
    # elif event['type'] == 'charge.updated':
    #   charge = event['data']['object']
    # elif event['type'] == 'charge.dispute.closed':
    #   dispute = event['data']['object']
    # elif event['type'] == 'charge.dispute.created':
    #   dispute = event['data']['object']
    # elif event['type'] == 'charge.dispute.funds_reinstated':
    #   dispute = event['data']['object']
    # elif event['type'] == 'charge.dispute.funds_withdrawn':
    #   dispute = event['data']['object']
    # elif event['type'] == 'charge.dispute.updated':
    #   dispute = event['data']['object']
    # elif event['type'] == 'charge.refund.updated':
    #   refund = event['data']['object']
    # elif event['type'] == 'checkout.session.async_payment_failed':
    #   session = event['data']['object']
    # elif event['type'] == 'checkout.session.async_payment_succeeded':
    #   session = event['data']['object']
    # elif event['type'] == 'checkout.session.completed':
    #   session = event['data']['object']
      
    #   session_id = session.get('id', None)
      
    #   # Save a copy of the order in your own database. This will give you a record of the order, even if the Stripe Checkout session expires or is canceled.
    #   # Send the customer a receipt email. This will confirm the order and provide the customer with their order details.
    #   # Fulfill the order. This may involve shipping the product, providing access to a digital product, or completing some other action.
    #   # Update your inventory levels. If you are selling physical products, you will need to update your inventory levels to reflect the fact that one has been sold.
    #   # Send a notification to your team. This may be useful for alerting your team that a new order has been placed.
      
      
    # elif event['type'] == 'checkout.session.expired':
    #   session = event['data']['object']
      
    #   session_id = session.get('id', None)
      
    #   # Remove items from the customer's cart.
    #   # Send a cart abandonment email to the customer.
    #   # Offer a discount to the customer to encourage them to complete their purchase.
    #   # Log the event for analytics purposes.
      
    # elif event['type'] == 'coupon.created':
    #   coupon = event['data']['object']
    # elif event['type'] == 'coupon.deleted':
    #   coupon = event['data']['object']
    # elif event['type'] == 'coupon.updated':
    #   coupon = event['data']['object']
    # elif event['type'] == 'credit_note.created':
    #   credit_note = event['data']['object']
    # elif event['type'] == 'credit_note.updated':
    #   credit_note = event['data']['object']
    # elif event['type'] == 'credit_note.voided':
    #   credit_note = event['data']['object']
    # elif event['type'] == 'customer.created':
    #   customer = event['data']['object']
    # elif event['type'] == 'customer.deleted':
    #   customer = event['data']['object']
    # elif event['type'] == 'customer.updated':
    #   customer = event['data']['object']
    # elif event['type'] == 'customer.discount.created':
    #   discount = event['data']['object']
    # elif event['type'] == 'customer.discount.deleted':
    #   discount = event['data']['object']
    # elif event['type'] == 'customer.discount.updated':
    #   discount = event['data']['object']
    # elif event['type'] == 'customer.source.created':
    #   source = event['data']['object']
    # elif event['type'] == 'customer.source.deleted':
    #   source = event['data']['object']
    # elif event['type'] == 'customer.source.expiring':
    #   source = event['data']['object']
    # elif event['type'] == 'customer.source.updated':
    #   source = event['data']['object']
    # elif event['type'] == 'customer.subscription.created':
    #   subscription = event['data']['object']
      
      
    #   # Acknowledge the event.
    #   # stripe.webhooks.acknowledge(event['id'])

    #   # Update your internal state to reflect the new subscription.
    #   # subscription = stripe.Subscription.retrieve(event['data']['object']['id'])
    #   # ...

    #   # Send the customer a welcome email.
    #   # ...

    #   # Start the first billing cycle.
    #   # ...

    #   # Start providing the customer with the benefits of their subscription.
    #   # ...
      
      
    # elif event['type'] == 'customer.subscription.deleted':
    #   subscription = event['data']['object']
      
    #   # Acknowledge the event.
    #   #stripe.webhooks.acknowledge(event['id'])

    #   # Revoke access to the customer's subscription.
    #   # ...

    #   # Send the customer a notification that their subscription has been canceled.
    #   # ...

    #   # Update your records to reflect the canceled subscription.
    #   # ...

      
      
    # elif event['type'] == 'customer.subscription.paused':
    #   subscription = event['data']['object']
      
      
    #   # Acknowledge the event.
    #   # stripe.webhooks.acknowledge(event['id'])

    #   # Update your internal records.
    #   # ...

    #   # Notify the customer.
    #   # ...

    #   # Offer the customer a way to resume their subscription.
    #   # ...
      
      
    # elif event['type'] == 'customer.subscription.pending_update_applied':
    #   subscription = event['data']['object']
    # elif event['type'] == 'customer.subscription.pending_update_expired':
    #   subscription = event['data']['object']
    # elif event['type'] == 'customer.subscription.resumed':
    #   subscription = event['data']['object']
      
    #   # Acknowledge the event.
    #   # stripe.webhooks.acknowledge(event['id'])

    #   # Update the customer's subscription status to active.
    #   # subscription = stripe.Subscription.retrieve(event['data']['object']['id'])
    #   # subscription.status = 'active'
    #   # subscription.save()

    #   # Send the customer a notification that their subscription has been resumed.
    #   # ...

    #   # Take any other necessary actions.
    #   # ...
      
      
    # elif event['type'] == 'customer.subscription.trial_will_end':
    #   subscription = event['data']['object']
    # elif event['type'] == 'customer.subscription.updated':
    #   subscription = event['data']['object']
      
    #   # Acknowledge the event.
    #   # stripe.webhooks.acknowledge(event['id'])

    #   # Get the updated subscription object.
    #   # subscription = stripe.Subscription.retrieve(event['data']['object']['id'])

    #   # Update your internal database to reflect the updated subscription state.
    #   # ...

    #   # Update the customer's account status.
    #   # ...

    #   # Send the customer a notification about the change.
    #   # ...
          
       
    # elif event['type'] == 'customer.tax_id.created':
    #   tax_id = event['data']['object']
    # elif event['type'] == 'customer.tax_id.deleted':
    #   tax_id = event['data']['object']
    # elif event['type'] == 'customer.tax_id.updated':
    #   tax_id = event['data']['object']
    # elif event['type'] == 'customer_cash_balance_transaction.created':
    #   customer_cash_balance_transaction = event['data']['object']
    # elif event['type'] == 'file.created':
    #   file = event['data']['object']
    # elif event['type'] == 'financial_connections.account.created':
    #   account = event['data']['object']
    # elif event['type'] == 'financial_connections.account.deactivated':
    #   account = event['data']['object']
    # elif event['type'] == 'financial_connections.account.disconnected':
    #   account = event['data']['object']
    # elif event['type'] == 'financial_connections.account.reactivated':
    #   account = event['data']['object']
    # elif event['type'] == 'financial_connections.account.refreshed_balance':
    #   account = event['data']['object']
    # elif event['type'] == 'identity.verification_session.canceled':
    #   verification_session = event['data']['object']
    # elif event['type'] == 'identity.verification_session.created':
    #   verification_session = event['data']['object']
    # elif event['type'] == 'identity.verification_session.processing':
    #   verification_session = event['data']['object']
    # elif event['type'] == 'identity.verification_session.requires_input':
    #   verification_session = event['data']['object']
    # elif event['type'] == 'identity.verification_session.verified':
    #   verification_session = event['data']['object']
    # elif event['type'] == 'invoice.created':
    #   invoice = event['data']['object']
    # elif event['type'] == 'invoice.deleted':
    #   invoice = event['data']['object']
    # elif event['type'] == 'invoice.finalization_failed':
    #   invoice = event['data']['object']
    # elif event['type'] == 'invoice.finalized':
    #   invoice = event['data']['object']
    # elif event['type'] == 'invoice.marked_uncollectible':
    #   invoice = event['data']['object']
    # elif event['type'] == 'invoice.paid':
    #   invoice = event['data']['object']
      
    #   # Acknowledge the event. This tells Stripe that you have received the event and that you are processing it. You can do this by calling the stripe.webhooks.acknowledge() method with the event ID.
    #   # Update your records. This may involve updating your customer database, inventory system, or other systems that are affected by subscriptions.
    #   # Send the customer a notification. This notification can inform the customer that their invoice has been paid and that their subscription is now active.
    #   # Provide the customer with access to the products or services that they have subscribed to.
            
      
      
    # elif event['type'] == 'invoice.payment_action_required':
    #   invoice = event['data']['object']
    # elif event['type'] == 'invoice.payment_failed':
    #   invoice = event['data']['object']
      
    #   # Acknowledge the event. This tells Stripe that you have received the event and that you are processing it. You can do this by calling the stripe.webhooks.acknowledge() method with the event ID.
    #   # Update your records. This may involve updating your customer database, inventory system, or other systems that are affected by invoices.
    #   # Send the customer a notification. This notification can inform the customer that their invoice payment has failed.
    #   # Take action to retry the payment. This may involve sending the customer a link to update their payment information or contacting them directly to collect payment.
    #   # Consider disabling the customer's subscription. If the customer has multiple failed payments, you may want to disable their subscription until they can successfully pay their invoice.
            
            
            
    # elif event['type'] == 'invoice.payment_succeeded':
    #   invoice = event['data']['object']
    # elif event['type'] == 'invoice.sent':
    #   invoice = event['data']['object']
    # elif event['type'] == 'invoice.upcoming':
    #   invoice = event['data']['object']
    # elif event['type'] == 'invoice.updated':
    #   invoice = event['data']['object']
    # elif event['type'] == 'invoice.voided':
    #   invoice = event['data']['object']
    # elif event['type'] == 'invoiceitem.created':
    #   invoiceitem = event['data']['object']
    # elif event['type'] == 'invoiceitem.deleted':
    #   invoiceitem = event['data']['object']
    # elif event['type'] == 'issuing_authorization.created':
    #   issuing_authorization = event['data']['object']
    # elif event['type'] == 'issuing_authorization.updated':
    #   issuing_authorization = event['data']['object']
    # elif event['type'] == 'issuing_card.created':
    #   issuing_card = event['data']['object']
    # elif event['type'] == 'issuing_card.updated':
    #   issuing_card = event['data']['object']
    # elif event['type'] == 'issuing_cardholder.created':
    #   issuing_cardholder = event['data']['object']
    # elif event['type'] == 'issuing_cardholder.updated':
    #   issuing_cardholder = event['data']['object']
    # elif event['type'] == 'issuing_dispute.closed':
    #   issuing_dispute = event['data']['object']
    # elif event['type'] == 'issuing_dispute.created':
    #   issuing_dispute = event['data']['object']
    # elif event['type'] == 'issuing_dispute.funds_reinstated':
    #   issuing_dispute = event['data']['object']
    # elif event['type'] == 'issuing_dispute.submitted':
    #   issuing_dispute = event['data']['object']
    # elif event['type'] == 'issuing_dispute.updated':
    #   issuing_dispute = event['data']['object']
    # elif event['type'] == 'issuing_transaction.created':
    #   issuing_transaction = event['data']['object']
    # elif event['type'] == 'issuing_transaction.updated':
    #   issuing_transaction = event['data']['object']
    # elif event['type'] == 'mandate.updated':
    #   mandate = event['data']['object']
    # elif event['type'] == 'payment_intent.amount_capturable_updated':
    #   payment_intent = event['data']['object']
    # elif event['type'] == 'payment_intent.canceled':
    #   payment_intent = event['data']['object']
    # elif event['type'] == 'payment_intent.created':
    #   payment_intent = event['data']['object']
    # elif event['type'] == 'payment_intent.partially_funded':
    #   payment_intent = event['data']['object']
    # elif event['type'] == 'payment_intent.payment_failed':
    #   payment_intent = event['data']['object']
    # elif event['type'] == 'payment_intent.processing':
    #   payment_intent = event['data']['object']
    # elif event['type'] == 'payment_intent.requires_action':
    #   payment_intent = event['data']['object']
    # elif event['type'] == 'payment_intent.succeeded':
    #   payment_intent = event['data']['object']
    # elif event['type'] == 'payment_link.created':
    #   payment_link = event['data']['object']
    # elif event['type'] == 'payment_link.updated':
    #   payment_link = event['data']['object']
    # elif event['type'] == 'payment_method.attached':
    #   payment_method = event['data']['object']
    # elif event['type'] == 'payment_method.card_automatically_updated':
    #   payment_method = event['data']['object']
    # elif event['type'] == 'payment_method.detached':
    #   payment_method = event['data']['object']
    # elif event['type'] == 'payment_method.updated':
    #   payment_method = event['data']['object']
    # elif event['type'] == 'payout.canceled':
    #   payout = event['data']['object']
    # elif event['type'] == 'payout.created':
    #   payout = event['data']['object']
    # elif event['type'] == 'payout.failed':
    #   payout = event['data']['object']
    # elif event['type'] == 'payout.paid':
    #   payout = event['data']['object']
    # elif event['type'] == 'payout.reconciliation_completed':
    #   payout = event['data']['object']
    # elif event['type'] == 'payout.updated':
    #   payout = event['data']['object']
    # elif event['type'] == 'person.created':
    #   person = event['data']['object']
    # elif event['type'] == 'person.deleted':
    #   person = event['data']['object']
    # elif event['type'] == 'person.updated':
    #   person = event['data']['object']
    # elif event['type'] == 'plan.created':
    #   plan = event['data']['object']
    # elif event['type'] == 'plan.deleted':
    #   plan = event['data']['object']
    # elif event['type'] == 'plan.updated':
    #   plan = event['data']['object']
    # elif event['type'] == 'price.created':
    #   price = event['data']['object']
    # elif event['type'] == 'price.deleted':
    #   price = event['data']['object']
    # elif event['type'] == 'price.updated':
    #   price = event['data']['object']
    # elif event['type'] == 'product.created':
    #   product = event['data']['object']
    # elif event['type'] == 'product.deleted':
    #   product = event['data']['object']
    # elif event['type'] == 'product.updated':
    #   product = event['data']['object']
    # elif event['type'] == 'promotion_code.created':
    #   promotion_code = event['data']['object']
    # elif event['type'] == 'promotion_code.updated':
    #   promotion_code = event['data']['object']
    # elif event['type'] == 'quote.accepted':
    #   quote = event['data']['object']
    # elif event['type'] == 'quote.canceled':
    #   quote = event['data']['object']
    # elif event['type'] == 'quote.created':
    #   quote = event['data']['object']
    # elif event['type'] == 'quote.finalized':
    #   quote = event['data']['object']
    # elif event['type'] == 'radar.early_fraud_warning.created':
    #   early_fraud_warning = event['data']['object']
    # elif event['type'] == 'radar.early_fraud_warning.updated':
    #   early_fraud_warning = event['data']['object']
    # elif event['type'] == 'refund.created':
    #   refund = event['data']['object']
    # elif event['type'] == 'refund.updated':
    #   refund = event['data']['object']
    # elif event['type'] == 'reporting.report_run.failed':
    #   report_run = event['data']['object']
    # elif event['type'] == 'reporting.report_run.succeeded':
    #   report_run = event['data']['object']
    # elif event['type'] == 'review.closed':
    #   review = event['data']['object']
    # elif event['type'] == 'review.opened':
    #   review = event['data']['object']
    # elif event['type'] == 'setup_intent.canceled':
    #   setup_intent = event['data']['object']
    # elif event['type'] == 'setup_intent.created':
    #   setup_intent = event['data']['object']
    # elif event['type'] == 'setup_intent.requires_action':
    #   setup_intent = event['data']['object']
    # elif event['type'] == 'setup_intent.setup_failed':
    #   setup_intent = event['data']['object']
    # elif event['type'] == 'setup_intent.succeeded':
    #   setup_intent = event['data']['object']
    # elif event['type'] == 'sigma.scheduled_query_run.created':
    #   scheduled_query_run = event['data']['object']
    # elif event['type'] == 'source.canceled':
    #   source = event['data']['object']
    # elif event['type'] == 'source.chargeable':
    #   source = event['data']['object']
    # elif event['type'] == 'source.failed':
    #   source = event['data']['object']
    # elif event['type'] == 'source.mandate_notification':
    #   source = event['data']['object']
    # elif event['type'] == 'source.refund_attributes_required':
    #   source = event['data']['object']
    # elif event['type'] == 'source.transaction.created':
    #   transaction = event['data']['object']
    # elif event['type'] == 'source.transaction.updated':
    #   transaction = event['data']['object']
    # elif event['type'] == 'subscription_schedule.aborted':
    #   subscription_schedule = event['data']['object']
      
      
    #   # When you receive a subscription_schedule.aborted webhook event, it means that the customer's subscription has been canceled due to a payment failure. This can happen for a number of reasons, such as:

    #   # The customer's credit card has expired.
    #   # The customer's credit card has been declined.
    #   # The customer has insufficient funds in their account.
    #   # When a subscription is aborted, the customer's subscription schedule will be canceled and their subscription will be moved to the incomplete state.

    #   # Here are some steps you can take in your project when you receive a subscription_schedule.aborted webhook event:

    #   # Acknowledge the event. This tells Stripe that you have received the event and that you are processing it. You can do this by calling the stripe.webhooks.acknowledge() method with the event ID.
    #   # Update your records. This may involve updating your customer database, inventory system, or other systems that are affected by subscriptions.
    #   # Send the customer a notification. This notification can inform the customer that their subscription has been canceled due to a payment failure.
    #   # Take steps to collect payment from the customer. You may want to send the customer a reminder email or try to collect payment through a different payment method.
    #   # If the customer does not pay, you may need to cancel their subscription.
    #   # Here is an example of a Python code snippet for handling a subscription_schedule.aborted webhook event:
            
            
    #   # Acknowledge the event.
    #   # stripe.webhooks.acknowledge(event['id'])

    #   # Update your records.
    #   # ...

    #   # Send the customer a notification.
    #   # ...

    #   # Take steps to collect payment from the customer.
    #   # ...

    #   # If the customer does not pay, you may need to cancel their subscription.
    #   # ...
              
      
    # elif event['type'] == 'subscription_schedule.canceled':
    #   subscription_schedule = event['data']['object']
      
    #   # Acknowledge the event. This tells Stripe that you have received the event and that you are processing it. You can do this by calling the stripe.webhooks.acknowledge() method with the event ID.
    #   # Update your records. This may involve updating your customer database, inventory system, or other systems that are affected by subscriptions.
    #   # Send the customer a notification. This notification can inform the customer that their subscription schedule has been canceled.
    #   # Cancel any outstanding invoices.
      
      
    #   # You can customize this code snippet to meet the specific needs of your project. For example, you may want to send the customer a different type of notification or you may want to implement a different billing process.

    #   # It is important to note that when a subscription schedule is canceled, the customer's subscription will also be canceled. This means that the customer will no longer have access to your product or service.

    #   # You should also be aware that the customer may cancel their subscription at any time. If this happens, you should stop charging the customer and refund any outstanding payments.

    #   # Here are some additional things you may want to consider doing when handling a subscription_schedule.canceled webhook event:

    #   # Remove any associated discount codes or coupons.
    #   # Disable any access to premium features or content.
    #   # Send the customer a link to reactivate their subscription.
    #   # By taking these steps, you can ensure that your customers are properly notified and that their subscriptions are properly managed.



    # elif event['type'] == 'subscription_schedule.completed':
    #   subscription_schedule = event['data']['object']
      
    #   # Acknowledge the event.
    #   # stripe.webhooks.acknowledge(event['id'])

    #   # Update your records to reflect the completed subscription schedule.
    #   # ...

    #   # Send the customer a notification.
    #   # ...
    #   # If the customer has a subscription schedule that renews automatically, you may want to send them a notification about their next billing date.
    #   # If the customer has a subscription schedule that does not renew automatically, you may want to send them a notification about how to renew their subscription.
            
      
    # elif event['type'] == 'subscription_schedule.created':
    #   subscription_schedule = event['data']['object']
      
    #   # Acknowledge the event. This tells Stripe that you have received the event and that you are processing it. You can do this by calling the stripe.webhooks.acknowledge() method with the event ID.
    #   # Update your records. This may involve updating your customer database, inventory system, or other systems that are affected by subscriptions.
    #   # Send the customer a notification. This notification can inform the customer about the new subscription schedule, such as the start date, end date, and price.
    #   # Prepare for the first invoice. If the subscription schedule is set to charge automatically, you will need to prepare for the first invoice. This may involve updating your billing system or sending the customer a reminder email.
            
      
    # elif event['type'] == 'subscription_schedule.expiring':
    #   subscription_schedule = event['data']['object']
      
    #   # Acknowledge the event. This tells Stripe that you have received the event and that you are processing it. You can do this by calling the stripe.webhooks.acknowledge() method with the event ID.
    #   # Update your records. This may involve updating your customer database, inventory system, or other systems that are affected by subscriptions.
    #   # Send the customer a notification. This notification can inform the customer that their subscription schedule is expiring and that they need to take action to renew their subscription.
    #   # Prepare for the next invoice. If the customer does not renew their subscription schedule, you will need to prepare for the next invoice. This may involve updating your billing system or sending the customer a reminder email.
            
      
    # elif event['type'] == 'subscription_schedule.released':
    #   subscription_schedule = event['data']['object']
      
    #   # There are a few reasons why a customer might release their subscription schedule:

    #   # They may want to manually manage their subscription and make payments on their own.
    #   # They may be switching to a different payment method.
    #   # They may be canceling their subscription altogether.
      
    #   # Acknowledge the event. This tells Stripe that you have received the event and that you are processing it. You can do this by calling the stripe.webhooks.acknowledge() method with the event ID.
    #   # Update your records. This may involve updating your customer database, inventory system, or other systems that are affected by subscriptions.
    #   # Send the customer a notification. This notification can inform the customer that their subscription schedule has been released.
    #   # Prepare for the customer to manually manage their subscription. If the customer was using the subscription schedule to automatically manage their subscription, they will now need to manually manage it by making payments on their own.
            
      
    # elif event['type'] == 'subscription_schedule.updated':
    #   subscription_schedule = event['data']['object']
      
    #   # The customer changes their payment method.
    #   # The customer changes the frequency of their billing.
    #   # The customer changes the amount of their billing.
    #   # The customer adds or removes a product from their subscription.
      
    #   # Acknowledge the event. This tells Stripe that you have received the event and that you are processing it. You can do this by calling the stripe.webhooks.acknowledge() method with the event ID.
    #   # Update your records. This may involve updating your customer database, inventory system, or other systems that are affected by subscriptions.
    #   # Send the customer a notification. This notification can inform the customer of the changes that have been made to their subscription schedule.
                  
            
    # elif event['type'] == 'tax.settings.updated':
    #   settings = event['data']['object']
    # elif event['type'] == 'tax_rate.created':
    #   tax_rate = event['data']['object']
    # elif event['type'] == 'tax_rate.updated':
    #   tax_rate = event['data']['object']
    # elif event['type'] == 'terminal.reader.action_failed':
    #   reader = event['data']['object']
    # elif event['type'] == 'terminal.reader.action_succeeded':
    #   reader = event['data']['object']
    # elif event['type'] == 'test_helpers.test_clock.advancing':
    #   test_clock = event['data']['object']
    # elif event['type'] == 'test_helpers.test_clock.created':
    #   test_clock = event['data']['object']
    # elif event['type'] == 'test_helpers.test_clock.deleted':
    #   test_clock = event['data']['object']
    # elif event['type'] == 'test_helpers.test_clock.internal_failure':
    #   test_clock = event['data']['object']
    # elif event['type'] == 'test_helpers.test_clock.ready':
    #   test_clock = event['data']['object']
    # elif event['type'] == 'topup.canceled':
    #   topup = event['data']['object']
    # elif event['type'] == 'topup.created':
    #   topup = event['data']['object']
    # elif event['type'] == 'topup.failed':
    #   topup = event['data']['object']
    # elif event['type'] == 'topup.reversed':
    #   topup = event['data']['object']
    # elif event['type'] == 'topup.succeeded':
    #   topup = event['data']['object']
    # elif event['type'] == 'transfer.created':
    #   transfer = event['data']['object']
    # elif event['type'] == 'transfer.reversed':
    #   transfer = event['data']['object']
    # elif event['type'] == 'transfer.updated':
    #   transfer = event['data']['object']
    # # ... handle other event types
    # else:
    #   print('Unhandled event type {}'.format(event['type']))

    
    
    
    return HttpResponse(status=200)
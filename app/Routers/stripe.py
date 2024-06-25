import os
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import JSONResponse

import stripe
from dotenv import load_dotenv

from app.Models.StripeModel import StripeModel


load_dotenv()

router = APIRouter()

stripe.api_key = os.getenv('STRIPE_API_KEY')

endpoint_secret = 'whsec_MrPR7F0F75yPfAi4wJyZ4EtdC4TFs4Cc'

print(stripe.api_key)

YOUR_DOMAIN = 'http://95.164.44.248:3001'

Platinum_Price_Id = "price_1PV6WHAZfjTlvHBoMdUxAcCJ"
Gold_Price_Id = "price_1PV6VgAZfjTlvHBo6XIjxJUM"
Silver_Price_Id = "price_1PV6UpAZfjTlvHBorhDSu5N7"

@router.post('/checkout')
def create_checkout_session(model: StripeModel):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': model.plan_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=YOUR_DOMAIN + '/dashboard/billing',
            cancel_url=YOUR_DOMAIN + '/dashboard/billing',
        )
    except Exception as e:
        return str(e)
    print(checkout_session.url)
    # return RedirectResponse(url=checkout_session.url, status_code=303)
    return checkout_session.url


@router.post('/webhook')
async def webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        handle_subscription_created(subscription)

    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)

    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        handle_payment_succeeded(invoice)

    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        handle_payment_failed(invoice)

    else:
        print('Unhandled event type {}'.format(event['type']))

    return JSONResponse(status_code=200, content={"success": True})

def handle_subscription_created(subscription):
    # Example logic for handling subscription created
    customer_id = subscription['customer']
    plan_id = subscription['items']['data'][0]['plan']['id']
    start_date = subscription['start_date']

    # Update your database with subscription details
    print("Subscription created:", subscription)

    # Provision services, send notifications, etc.
    # ...

def handle_subscription_updated(subscription):
    # Example logic for handling subscription updated
    print("Subscription updated:", subscription)

def handle_subscription_deleted(subscription):
    # Example logic for handling subscription deleted
    print("Subscription deleted:", subscription)

def handle_payment_succeeded(invoice):
    
    line_item = invoice['lines']['data'][0]
    plan_id = line_item['plan']['id']
    
    if plan_id == Silver_Price_Id:
        crud.update_usertype()
    
    print("Payment succeeded:", invoice)

def handle_payment_failed(invoice):
    # Example logic for handling payment failed
    print("Payment failed:", invoice)
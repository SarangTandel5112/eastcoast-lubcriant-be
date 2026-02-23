from loguru import logger
from app.tasks.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_payment(self, order_id: str, amount: float, payment_method: str):
    """
    Process payment via Stripe or any payment gateway.
    Retries up to 3 times on failure.
    """
    try:
        logger.info("Processing payment | order_id={} amount={} method={}", order_id, amount, payment_method)

        # ── Replace with actual Stripe logic ─────────────
        # import stripe
        # stripe.api_key = settings.stripe_secret_key
        # intent = stripe.PaymentIntent.create(
        #     amount=int(amount * 100),  # Stripe uses cents
        #     currency="usd",
        #     payment_method=payment_method,
        #     confirm=True,
        # )
        # payment_intent_id = intent.id
        # ─────────────────────────────────────────────────

        logger.info("Payment successful | order_id={}", order_id)
        return {"status": "success", "order_id": order_id}

    except Exception as exc:
        logger.error("Payment failed | order_id={} error={}", order_id, str(exc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2)
def process_refund(self, order_id: str, payment_intent_id: str, amount: float):
    try:
        logger.info("Processing refund | order_id={} amount={}", order_id, amount)
        # stripe.Refund.create(payment_intent=payment_intent_id, amount=int(amount * 100))
        logger.info("Refund successful | order_id={}", order_id)
        return {"status": "refunded", "order_id": order_id}

    except Exception as exc:
        logger.error("Refund failed | order_id={} error={}", order_id, str(exc))
        raise self.retry(exc=exc)

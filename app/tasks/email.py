from loguru import logger
from app.tasks.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_confirmation_email(self, user_id: str, order_id: str):
    """
    Send order confirmation email via SendGrid or any SMTP provider.
    Retries up to 3 times on failure with 60s delay.
    """
    try:
        logger.info("Sending order confirmation | user_id={} order_id={}", user_id, order_id)

        # ── Replace with actual email logic ──────────────
        # import sendgrid
        # sg = sendgrid.SendGridAPIClient(api_key=settings.sendgrid_api_key)
        # message = Mail(from_email="no-reply@yourstore.com", to_emails=user_email, ...)
        # sg.send(message)
        # ─────────────────────────────────────────────────

        logger.info("Order confirmation email sent | order_id={}", order_id)
        return {"status": "sent", "order_id": order_id}

    except Exception as exc:
        logger.error("Email failed | order_id={} error={}", order_id, str(exc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def send_password_reset_email(self, email: str, reset_token: str):
    try:
        logger.info("Sending password reset email | email={}", email)
        # Add your email logic here
        logger.info("Password reset email sent | email={}", email)
        return {"status": "sent"}

    except Exception as exc:
        logger.error("Password reset email failed | email={} error={}", email, str(exc))
        raise self.retry(exc=exc)

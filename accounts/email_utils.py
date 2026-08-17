from decouple import config
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_verification_email(to_email, code):
    """
    Sends the verification code via SendGrid's HTTPS API (port 443),
    instead of Django's SMTP email backend (port 587). Render's free
    tier blocks outbound SMTP connections, but HTTPS API calls work
    fine everywhere — this bypasses the block entirely.
    """
    message = Mail(
        from_email=config('DEFAULT_FROM_EMAIL'),
        to_emails=to_email,
        subject='Your MiAbbie verification code',
        plain_text_content=f'Your verification code is: {code}',
    )

    sg = SendGridAPIClient(config('SENDGRID_API_KEY'))
    sg.send(message)
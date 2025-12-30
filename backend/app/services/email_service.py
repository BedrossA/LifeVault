"""Email service for sending emails"""
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for sending transactional emails"""
    
    # In production, replace this with a real email service like:
    # - SendGrid
    # - AWS SES
    # - Mailgun
    # - SMTP server
    
    @staticmethod
    async def send_password_reset_email(
        email: str,
        reset_token: str,
        reset_url: Optional[str] = None
    ) -> bool:
        """
        Send password reset email
        
        Args:
            email: User's email address
            reset_token: Password reset token
            reset_url: Optional custom reset URL (defaults to app URL)
        
        Returns:
            bool: True if email was sent successfully
        """
        try:
            # Generate reset URL
            if not reset_url:
                # In production, use your actual frontend URL
                base_url = "http://localhost:5173"  # Replace with actual frontend URL
                reset_url = f"{base_url}/reset-password?token={reset_token}"
            
            # Email content
            subject = f"{settings.APP_NAME} - Password Reset Request"
            body = f"""
Hello,

You requested a password reset for your {settings.APP_NAME} account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this password reset, please ignore this email.

Best regards,
{settings.APP_NAME} Team
"""
            
            # In development, just log the email
            # In production, send actual email using your email service
            logger.info(f"Password reset email for {email}:")
            logger.info(f"Reset URL: {reset_url}")
            logger.info(f"Token: {reset_token}")
            
            # TODO: Replace with actual email sending
            # Example with SendGrid:
            # import sendgrid
            # sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            # message = sendgrid.Mail(
            #     from_email='noreply@lifevault.com',
            #     to_emails=email,
            #     subject=subject,
            #     plain_text_content=body
            # )
            # response = sg.send(message)
            # return response.status_code == 202
            
            # For now, return True to indicate "sent" (in dev mode)
            # In production, this should actually send the email
            return True
            
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            return False
    
    @staticmethod
    async def send_welcome_email(email: str, username: str) -> bool:
        """Send welcome email to new user"""
        try:
            subject = f"Welcome to {settings.APP_NAME}!"
            body = f"""
Hello {username},

Welcome to {settings.APP_NAME}! We're excited to have you on board.

Your account has been successfully created. You can now start using all the features.

If you have any questions, please don't hesitate to contact our support team.

Best regards,
{settings.APP_NAME} Team
"""
            
            logger.info(f"Welcome email for {email} (username: {username})")
            # TODO: Implement actual email sending
            return True
            
        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
            return False


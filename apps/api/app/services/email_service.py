import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    @staticmethod
    def generate_reset_token() -> str:
        """Generate a secure random token for password reset"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def _create_reset_email_html(reset_url: str, user_name: Optional[str] = None) -> str:
        """Create HTML email content for password reset"""
        greeting = f"Hi {user_name}," if user_name else "Hi there,"
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset Request</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #ffffff; padding: 30px; border: 1px solid #e9ecef; }}
                .footer {{ background-color: #f8f9fa; padding: 15px; border-radius: 0 0 8px 8px; font-size: 12px; color: #666; }}
                .button {{ display: inline-block; background-color: #007bff; color: white; text-decoration: none; padding: 12px 24px; border-radius: 4px; margin: 20px 0; }}
                .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 4px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; color: #007bff;">Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>{greeting}</p>
                    <p>You recently requested to reset your password for your account. Click the button below to reset it:</p>
                    <a href="{reset_url}" class="button">Reset Your Password</a>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #007bff;">{reset_url}</p>
                    <div class="warning">
                        <strong>⚠️ Important:</strong>
                        <ul>
                            <li>This link will expire in 1 hour for security reasons</li>
                            <li>If you didn't request this reset, please ignore this email</li>
                            <li>Never share this link with anyone</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>This email was sent automatically from {settings.EMAIL_FROM_NAME}. Please do not reply to this email.</p>
                    <p>If you're having trouble clicking the button, copy and paste the URL above into your web browser.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _create_reset_email_text(reset_url: str, user_name: Optional[str] = None) -> str:
        """Create plain text email content for password reset"""
        greeting = f"Hi {user_name}," if user_name else "Hi there,"
        
        return f"""
{greeting}

You recently requested to reset your password for your account.

To reset your password, please click on the following link or copy and paste it into your browser:

{reset_url}

IMPORTANT:
- This link will expire in 1 hour for security reasons
- If you didn't request this reset, please ignore this email
- Never share this link with anyone

---
This email was sent automatically from {settings.EMAIL_FROM_NAME}.
Please do not reply to this email.
        """
    
    @staticmethod
    async def send_password_reset_email(
        to_email: str, 
        reset_token: str, 
        user_name: Optional[str] = None
    ) -> bool:
        """Send password reset email with reset link"""
        try:
            # Validate email configuration
            if not settings.SMTP_USER or not settings.SMTP_PASSWORD or not settings.EMAIL_FROM:
                logger.error("Email configuration is incomplete. Please set SMTP_USER, SMTP_PASSWORD, and EMAIL_FROM.")
                return False
            
            # Create reset URL
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Reset Your Password - {settings.EMAIL_FROM_NAME}"
            msg['From'] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
            msg['To'] = to_email
            
            # Create both plain text and HTML versions
            text_content = EmailService._create_reset_email_text(reset_url, user_name)
            html_content = EmailService._create_reset_email_html(reset_url, user_name)
            
            # Attach parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.success(f"Password reset email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    def validate_email_config() -> tuple[bool, str]:
        """Validate email configuration"""
        missing_configs = []
        
        if not settings.SMTP_USER:
            missing_configs.append("SMTP_USER")
        if not settings.SMTP_PASSWORD:
            missing_configs.append("SMTP_PASSWORD")
        if not settings.EMAIL_FROM:
            missing_configs.append("EMAIL_FROM")
            
        if missing_configs:
            return False, f"Missing email configuration: {', '.join(missing_configs)}"
        
        return True, "Email configuration is valid"
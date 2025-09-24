import os
import logging
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from typing import List
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configuration email
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fm = FastMail(conf)

class EmailService:
    @staticmethod
    async def send_password_reset_email(user_email: str, user_name: str, reset_token: str) -> bool:
        """
        Envoie un email de réinitialisation de mot de passe
        """
        try:
            # URL de reset - ajustez selon votre domaine
            reset_url = f"https://votre-domaine.com/reset-password?token={reset_token}"
            
            # Template HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Réinitialisation de mot de passe</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f8f9fa; }}
                    .button {{ 
                        display: inline-block; 
                        padding: 12px 24px; 
                        background-color: #007bff; 
                        color: white; 
                        text-decoration: none; 
                        border-radius: 5px; 
                        margin: 20px 0;
                    }}
                    .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Réinitialisation de mot de passe</h1>
                    </div>
                    <div class="content">
                        <p>Bonjour {user_name},</p>
                        <p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
                        <p>Cliquez sur le bouton ci-dessous pour créer un nouveau mot de passe :</p>
                        <p style="text-align: center;">
                            <a href="{reset_url}" class="button">Réinitialiser mon mot de passe</a>
                        </p>
                        <p><strong>Ce lien expire dans 30 minutes.</strong></p>
                        <p>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.</p>
                        <p>Cordialement,<br>L'équipe de votre application</p>
                    </div>
                    <div class="footer">
                        <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Version texte simple
            text_content = f"""
            Bonjour {user_name},
            
            Vous avez demandé la réinitialisation de votre mot de passe.
            
            Cliquez sur le lien ci-dessous pour créer un nouveau mot de passe :
            {reset_url}
            
            Ce lien expire dans 30 minutes.
            
            Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
            
            Cordialement,
            L'équipe de votre application
            """

            message = MessageSchema(
                subject="Réinitialisation de votre mot de passe",
                recipients=[user_email],
                body=text_content,
                html=html_content,
                subtype=MessageType.html
            )

            await fm.send_message(message)
            logger.info(f"Email de reset envoyé à {user_email}")
            return True

        except Exception as e:
            logger.error(f"Erreur envoi email à {user_email}: {e}")
            return False

    @staticmethod
    async def send_password_changed_confirmation(user_email: str, user_name: str) -> bool:
        """
        Envoie un email de confirmation après changement de mot de passe
        """
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Mot de passe modifié</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f8f9fa; }}
                    .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Mot de passe modifié avec succès</h1>
                    </div>
                    <div class="content">
                        <p>Bonjour {user_name},</p>
                        <p>Votre mot de passe a été modifié avec succès.</p>
                        <p>Si vous n'êtes pas à l'origine de cette modification, contactez-nous immédiatement.</p>
                        <p>Cordialement,<br>L'équipe de votre application</p>
                    </div>
                    <div class="footer">
                        <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            message = MessageSchema(
                subject="Votre mot de passe a été modifié",
                recipients=[user_email],
                body=f"Bonjour {user_name},\n\nVotre mot de passe a été modifié avec succès.\n\nCordialement,\nL'équipe de votre application",
                html=html_content,
                subtype=MessageType.html
            )

            await fm.send_message(message)
            logger.info(f"Email de confirmation envoyé à {user_email}")
            return True

        except Exception as e:
            logger.error(f"Erreur envoi email de confirmation à {user_email}: {e}")
            return False
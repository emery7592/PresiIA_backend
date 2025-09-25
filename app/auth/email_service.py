import os
import logging
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from typing import List
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
logger = logging.getLogger(__name__)

# Configuration email mise à jour pour Brevo (contourne le blocage DigitalOcean)
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("BREVO_USERNAME", os.getenv("MAIL_USERNAME")),  # Fallback vers ancienne config
    MAIL_PASSWORD=os.getenv("BREVO_PASSWORD", os.getenv("MAIL_PASSWORD")),  # Clé API Brevo ou ancien mot de passe
    MAIL_FROM=os.getenv("BREVO_FROM_EMAIL", os.getenv("MAIL_FROM")),        # Email expéditeur
    MAIL_FROM_NAME=os.getenv("BREVO_FROM_NAME", os.getenv("MAIL_FROM_NAME", "RedPill IA")),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp-relay.brevo.com"),  # Nouveau serveur par défaut
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=None
)

fm = FastMail(conf)

class EmailService:
    @staticmethod
    async def send_password_reset_email(user_email: str, user_name: str, reset_token: str) -> bool:
        """
        Envoie un email de réinitialisation de mot de passe via Brevo
        """
        try:
            # URL de reset - ajustez selon votre domaine
            reset_url = f"https://redpill-ia.app/reset-password?token={reset_token}"
            
            # Template HTML professionnel
            html_content = f"""
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Réinitialisation de mot de passe - RedPill IA</title>
                <style>
                    body {{ 
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        line-height: 1.6; 
                        color: #333333; 
                        margin: 0;
                        padding: 0;
                        background-color: #f8fafc;
                    }}
                    .email-container {{ 
                        max-width: 600px; 
                        margin: 20px auto; 
                        background-color: #ffffff;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                    }}
                    .header {{ 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; 
                        padding: 40px 30px; 
                        text-align: center; 
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-weight: 700;
                        letter-spacing: -0.5px;
                    }}
                    .header p {{
                        margin: 8px 0 0 0;
                        opacity: 0.9;
                        font-size: 16px;
                    }}
                    .content {{ 
                        padding: 40px 30px; 
                    }}
                    .greeting {{
                        font-size: 18px;
                        margin-bottom: 20px;
                        color: #1f2937;
                    }}
                    .message {{
                        font-size: 16px;
                        line-height: 1.7;
                        color: #4b5563;
                        margin-bottom: 30px;
                    }}
                    .cta-button {{ 
                        display: inline-block; 
                        padding: 16px 32px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white !important; 
                        text-decoration: none; 
                        border-radius: 8px; 
                        font-weight: 600;
                        font-size: 16px;
                        text-align: center;
                        transition: transform 0.2s ease, box-shadow 0.2s ease;
                        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                    }}
                    .cta-button:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
                    }}
                    .button-container {{
                        text-align: center;
                        margin: 32px 0;
                    }}
                    .warning-box {{
                        background-color: #fef3c7;
                        border-left: 4px solid #f59e0b;
                        border-radius: 6px;
                        padding: 16px;
                        margin: 24px 0;
                        color: #92400e;
                    }}
                    .warning-box strong {{
                        color: #78350f;
                    }}
                    .link-fallback {{
                        background-color: #f9fafb;
                        border: 1px solid #e5e7eb;
                        border-radius: 6px;
                        padding: 16px;
                        margin: 20px 0;
                        word-break: break-all;
                        font-family: 'SF Mono', Consolas, monospace;
                        font-size: 14px;
                        color: #6b7280;
                    }}
                    .footer {{ 
                        text-align: center; 
                        padding: 32px 30px; 
                        font-size: 14px; 
                        color: #9ca3af; 
                        background-color: #f9fafb;
                        border-top: 1px solid #e5e7eb;
                    }}
                    .footer a {{
                        color: #667eea;
                        text-decoration: none;
                    }}
                    .brand {{
                        color: #667eea;
                        font-weight: 700;
                    }}
                    .security-notice {{
                        font-size: 14px;
                        color: #6b7280;
                        margin-top: 24px;
                        padding-top: 20px;
                        border-top: 1px solid #e5e7eb;
                    }}
                    @media (max-width: 600px) {{
                        .email-container {{
                            margin: 0;
                            border-radius: 0;
                        }}
                        .content {{
                            padding: 30px 20px;
                        }}
                        .header {{
                            padding: 30px 20px;
                        }}
                        .cta-button {{
                            display: block;
                            width: calc(100% - 64px);
                            margin: 0 auto;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="header">
                        <h1>🔐 Réinitialisation</h1>
                        <p>Sécurisez votre compte en quelques clics</p>
                    </div>
                    <div class="content">
                        <div class="greeting">
                            Bonjour <strong>{user_name}</strong> ! 👋
                        </div>
                        
                        <div class="message">
                            Vous avez demandé la réinitialisation de votre mot de passe pour votre compte <span class="brand">RedPill IA</span>.
                        </div>
                        
                        <div class="button-container">
                            <a href="{reset_url}" class="cta-button">
                                Réinitialiser mon mot de passe
                            </a>
                        </div>
                        
                        <div class="warning-box">
                            <strong>⚠️ Important :</strong> Ce lien expire dans <strong>30 minutes</strong> pour votre sécurité.
                        </div>
                        
                        <p style="font-size: 15px; color: #6b7280;">
                            Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :
                        </p>
                        <div class="link-fallback">
                            {reset_url}
                        </div>
                        
                        <div class="security-notice">
                            <p><strong>Vous n'avez pas demandé cette réinitialisation ?</strong><br>
                            Vous pouvez ignorer cet email en toute sécurité. Votre mot de passe reste inchangé.</p>
                        </div>
                        
                        <p style="margin-top: 32px; color: #4b5563;">
                            Cordialement,<br>
                            L'équipe <span class="brand">RedPill IA</span> ✨
                        </p>
                    </div>
                    <div class="footer">
                        <p>Cet email a été envoyé automatiquement par <span class="brand">RedPill IA</span></p>
                        <p>Merci de ne pas répondre directement à cet email.</p>
                        <p>&copy; 2025 RedPill IA. Tous droits réservés.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Version texte simple améliorée
            text_content = f"""
🔐 RÉINITIALISATION DE MOT DE PASSE - RedPill IA

Bonjour {user_name} !

Vous avez demandé la réinitialisation de votre mot de passe pour votre compte RedPill IA.

➡️ CLIQUEZ SUR CE LIEN POUR CRÉER UN NOUVEAU MOT DE PASSE :
{reset_url}

⚠️ IMPORTANT : Ce lien expire dans 30 minutes pour votre sécurité.

Si vous n'avez pas demandé cette réinitialisation, vous pouvez ignorer cet email en toute sécurité.

Cordialement,
L'équipe RedPill IA ✨

---
Cet email a été envoyé automatiquement par RedPill IA.
Merci de ne pas répondre directement à cet email.
            """

            message = MessageSchema(
                subject="🔐 Réinitialisation de votre mot de passe - RedPill IA",
                recipients=[user_email],
                body=text_content,
                html=html_content,
                subtype=MessageType.html
            )

            await fm.send_message(message)
            logger.info(f"✅ Email de reset envoyé avec succès via Brevo à {user_email}")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'envoi via Brevo à {user_email}: {str(e)}")
            return False

    @staticmethod
    async def send_password_changed_confirmation(user_email: str, user_name: str) -> bool:
        """
        Envoie un email de confirmation après changement de mot de passe
        """
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Mot de passe modifié avec succès - RedPill IA</title>
                <style>
                    body {{ 
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        line-height: 1.6; 
                        color: #333333; 
                        margin: 0;
                        padding: 0;
                        background-color: #f8fafc;
                    }}
                    .email-container {{ 
                        max-width: 600px; 
                        margin: 20px auto; 
                        background-color: #ffffff;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                    }}
                    .header {{ 
                        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                        color: white; 
                        padding: 40px 30px; 
                        text-align: center; 
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-weight: 700;
                        letter-spacing: -0.5px;
                    }}
                    .header p {{
                        margin: 8px 0 0 0;
                        opacity: 0.9;
                        font-size: 16px;
                    }}
                    .content {{ 
                        padding: 40px 30px; 
                    }}
                    .success-box {{
                        background-color: #d1fae5;
                        border-left: 4px solid #10b981;
                        border-radius: 6px;
                        padding: 20px;
                        margin: 24px 0;
                        text-align: center;
                    }}
                    .success-box h3 {{
                        margin: 0 0 8px 0;
                        color: #065f46;
                        font-size: 18px;
                    }}
                    .success-box p {{
                        margin: 0;
                        color: #047857;
                        font-size: 15px;
                    }}
                    .security-alert {{
                        background-color: #fef3c7;
                        border-left: 4px solid #f59e0b;
                        border-radius: 6px;
                        padding: 16px;
                        margin: 24px 0;
                        color: #92400e;
                    }}
                    .security-alert strong {{
                        color: #78350f;
                    }}
                    .security-tips {{
                        background-color: #f0f9ff;
                        border: 1px solid #0ea5e9;
                        border-radius: 6px;
                        padding: 20px;
                        margin: 24px 0;
                    }}
                    .security-tips h4 {{
                        margin: 0 0 12px 0;
                        color: #0369a1;
                        font-size: 16px;
                    }}
                    .security-tips ul {{
                        margin: 0;
                        padding-left: 20px;
                        color: #0c4a6e;
                    }}
                    .security-tips li {{
                        margin-bottom: 6px;
                    }}
                    .timestamp {{
                        font-size: 14px;
                        color: #6b7280;
                        background-color: #f9fafb;
                        padding: 12px;
                        border-radius: 4px;
                        margin: 20px 0;
                        text-align: center;
                    }}
                    .footer {{ 
                        text-align: center; 
                        padding: 32px 30px; 
                        font-size: 14px; 
                        color: #9ca3af; 
                        background-color: #f9fafb;
                        border-top: 1px solid #e5e7eb;
                    }}
                    .footer a {{
                        color: #10b981;
                        text-decoration: none;
                    }}
                    .brand {{
                        color: #10b981;
                        font-weight: 700;
                    }}
                    @media (max-width: 600px) {{
                        .email-container {{
                            margin: 0;
                            border-radius: 0;
                        }}
                        .content {{
                            padding: 30px 20px;
                        }}
                        .header {{
                            padding: 30px 20px;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="header">
                        <h1>✅ Mot de passe modifié</h1>
                        <p>Votre compte est maintenant sécurisé</p>
                    </div>
                    <div class="content">
                        <p style="font-size: 18px; margin-bottom: 20px; color: #1f2937;">
                            Bonjour <strong>{user_name}</strong> ! 👋
                        </p>
                        
                        <div class="success-box">
                            <h3>🎉 Succès !</h3>
                            <p>Votre mot de passe a été modifié avec succès.</p>
                        </div>
                        
                        <div class="timestamp">
                            <strong>📅 Date de modification :</strong><br>
                            {datetime.now().strftime('%d/%m/%Y à %H:%M')} (heure française)
                        </div>
                        
                        <p style="color: #4b5563; margin: 20px 0;">
                            Votre mot de passe pour <span class="brand">RedPill IA</span> a été mis à jour avec succès. 
                            Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.
                        </p>
                        
                        <div class="security-alert">
                            <strong>🔒 Sécurité :</strong> Si vous n'êtes pas à l'origine de cette modification, 
                            contactez-nous <strong>immédiatement</strong> à 
                            <a href="mailto:support@redpill-ia.app" style="color: #dc2626;">support@redpill-ia.app</a>
                        </div>
                        
                        <div class="security-tips">
                            <h4>🛡️ Conseils de sécurité :</h4>
                            <ul>
                                <li>Ne partagez jamais votre mot de passe avec qui que ce soit</li>
                                <li>Utilisez un mot de passe unique et complexe pour chaque service</li>
                                <li>Déconnectez-vous toujours des appareils partagés</li>
                                <li>Activez l'authentification à deux facteurs si disponible</li>
                                <li>Surveillez régulièrement l'activité de votre compte</li>
                            </ul>
                        </div>
                        
                        <p style="margin-top: 32px; color: #4b5563;">
                            Merci de faire confiance à <span class="brand">RedPill IA</span> pour vos besoins en IA ! 🚀
                        </p>
                        
                        <p style="color: #4b5563;">
                            Cordialement,<br>
                            L'équipe <span class="brand">RedPill IA</span> ✨
                        </p>
                    </div>
                    <div class="footer">
                        <p>Cet email a été envoyé automatiquement par <span class="brand">RedPill IA</span></p>
                        <p>Merci de ne pas répondre directement à cet email.</p>
                        <p>Des questions ? Contactez-nous à <a href="mailto:support@redpill-ia.app">support@redpill-ia.app</a></p>
                        <p>&copy; 2025 RedPill IA. Tous droits réservés.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            text_content = f"""
✅ MOT DE PASSE MODIFIÉ AVEC SUCCÈS - RedPill IA

Bonjour {user_name} !

🎉 Votre mot de passe a été modifié avec succès !

📅 Date de modification : {datetime.now().strftime('%d/%m/%Y à %H:%M')} (heure française)

Votre mot de passe pour RedPill IA a été mis à jour avec succès. 
Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.

🔒 SÉCURITÉ : Si vous n'êtes pas à l'origine de cette modification, 
contactez-nous IMMÉDIATEMENT à support@redpill-ia.app

🛡️ CONSEILS DE SÉCURITÉ :
• Ne partagez jamais votre mot de passe avec qui que ce soit
• Utilisez un mot de passe unique et complexe pour chaque service
• Déconnectez-vous toujours des appareils partagés
• Activez l'authentification à deux facteurs si disponible
• Surveillez régulièrement l'activité de votre compte

Merci de faire confiance à RedPill IA pour vos besoins en IA ! 🚀

Cordialement,
L'équipe RedPill IA ✨

---
Cet email a été envoyé automatiquement par RedPill IA.
Des questions ? Contactez-nous à support@redpill-ia.app
            """

            message = MessageSchema(
                subject="✅ Votre mot de passe a été modifié avec succès - RedPill IA",
                recipients=[user_email],
                body=text_content,
                html=html_content,
                subtype=MessageType.html
            )

            await fm.send_message(message)
            logger.info(f"✅ Email de confirmation envoyé avec succès via Brevo à {user_email}")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'envoi de confirmation via Brevo à {user_email}: {str(e)}")
            return False

    @staticmethod
    async def send_welcome_email(user_email: str, user_name: str) -> bool:
        """
        Envoie un email de bienvenue lors de l'inscription (bonus)
        """
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Bienvenue sur RedPill IA !</title>
                <style>
                    body {{ 
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        line-height: 1.6; 
                        color: #333333; 
                        margin: 0;
                        padding: 0;
                        background-color: #f8fafc;
                    }}
                    .email-container {{ 
                        max-width: 600px; 
                        margin: 20px auto; 
                        background-color: #ffffff;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                    }}
                    .header {{ 
                        background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
                        color: white; 
                        padding: 40px 30px; 
                        text-align: center; 
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 32px;
                        font-weight: 700;
                    }}
                    .content {{ 
                        padding: 40px 30px; 
                    }}
                    .welcome-message {{
                        font-size: 18px;
                        color: #1f2937;
                        margin-bottom: 24px;
                        text-align: center;
                    }}
                    .features-list {{
                        background-color: #f8fafc;
                        border-radius: 8px;
                        padding: 24px;
                        margin: 24px 0;
                    }}
                    .features-list h3 {{
                        margin: 0 0 16px 0;
                        color: #1f2937;
                        text-align: center;
                    }}
                    .feature {{
                        display: flex;
                        align-items: center;
                        margin-bottom: 12px;
                    }}
                    .feature-icon {{
                        font-size: 20px;
                        margin-right: 12px;
                        width: 24px;
                    }}
                    .brand {{
                        color: #8b5cf6;
                        font-weight: 700;
                    }}
                    .footer {{ 
                        text-align: center; 
                        padding: 32px 30px; 
                        font-size: 14px; 
                        color: #9ca3af; 
                        background-color: #f9fafb;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="header">
                        <h1>🎉 Bienvenue !</h1>
                    </div>
                    <div class="content">
                        <div class="welcome-message">
                            Salut <strong>{user_name}</strong> ! 👋<br>
                            Bienvenue dans l'univers de <span class="brand">RedPill IA</span> !
                        </div>
                        
                        <p>Félicitations ! Votre compte a été créé avec succès. Vous faites maintenant partie de notre communauté d'utilisateurs qui explorent le potentiel de l'IA.</p>
                        
                        <div class="features-list">
                            <h3>🚀 Ce que vous pouvez faire maintenant :</h3>
                            <div class="feature">
                                <span class="feature-icon">💬</span>
                                <span>Poser des questions illimitées à notre IA</span>
                            </div>
                            <div class="feature">
                                <span class="feature-icon">🧠</span>
                                <span>Accéder à des modèles d'IA avancés</span>
                            </div>
                            <div class="feature">
                                <span class="feature-icon">📱</span>
                                <span>Synchroniser sur tous vos appareils</span>
                            </div>
                            <div class="feature">
                                <span class="feature-icon">🔒</span>
                                <span>Profiter d'une expérience sécurisée</span>
                            </div>
                        </div>
                        
                        <p>Si vous avez des questions ou besoin d'aide, n'hésitez pas à nous contacter.</p>
                        
                        <p style="margin-top: 32px; text-align: center;">
                            Prêt à découvrir le futur de l'IA ? 🚀<br>
                            <strong>L'équipe <span class="brand">RedPill IA</span></strong> ✨
                        </p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2025 RedPill IA. Tous droits réservés.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            text_content = f"""
🎉 BIENVENUE SUR REDPILL IA !

Salut {user_name} ! 👋

Bienvenue dans l'univers de RedPill IA !

Félicitations ! Votre compte a été créé avec succès. Vous faites maintenant partie de notre communauté d'utilisateurs qui explorent le potentiel de l'IA.

🚀 CE QUE VOUS POUVEZ FAIRE MAINTENANT :
💬 Poser des questions illimitées à notre IA
🧠 Accéder à des modèles d'IA avancés
📱 Synchroniser sur tous vos appareils
🔒 Profiter d'une expérience sécurisée

Si vous avez des questions ou besoin d'aide, n'hésitez pas à nous contacter.

Prêt à découvrir le futur de l'IA ? 🚀

L'équipe RedPill IA ✨

---
© 2025 RedPill IA. Tous droits réservés.
            """

            message = MessageSchema(
                subject="🎉 Bienvenue sur RedPill IA ! Votre aventure IA commence maintenant",
                recipients=[user_email],
                body=text_content,
                html=html_content,
                subtype=MessageType.html
            )

            await fm.send_message(message)
            logger.info(f"✅ Email de bienvenue envoyé avec succès via Brevo à {user_email}")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'envoi de bienvenue via Brevo à {user_email}: {str(e)}")
            return False
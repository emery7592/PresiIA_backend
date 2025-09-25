import os
import logging
import httpx
from typing import Dict, Any
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
logger = logging.getLogger(__name__)

class EmailService:
    """Service d'envoi d'email via l'API Brevo (remplace SMTP)"""
    
    def __init__(self):
        self.api_key = os.getenv("BREVO_PASSWORD")  # Utilise la même variable
        self.from_email = os.getenv("BREVO_FROM_EMAIL", os.getenv("MAIL_FROM", "redipill.ia@gmail.com"))
        self.from_name = os.getenv("BREVO_FROM_NAME", os.getenv("MAIL_FROM_NAME", "RedPill IA"))
        self.base_url = "https://api.brevo.com/v3"
        
        if not self.api_key:
            logger.error("BREVO_PASSWORD (clé API) manquante dans les variables d'environnement")
            raise ValueError("Clé API Brevo manquante")
    
    async def _send_email_via_api(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Envoie un email via l'API Brevo"""
        try:
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "sender": {
                    "name": self.from_name,
                    "email": self.from_email
                },
                "to": [
                    {
                        "email": to_email
                    }
                ],
                "subject": subject,
                "htmlContent": html_content
            }
            
            # Ajouter le contenu texte si fourni
            if text_content:
                payload["textContent"] = text_content
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/smtp/email",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 201:
                    logger.info(f"✅ Email envoyé avec succès via API Brevo à {to_email}")
                    return True
                else:
                    logger.error(f"❌ Erreur API Brevo: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'envoi via API Brevo à {to_email}: {str(e)}")
            return False
    
    async def send_password_reset_email(self, user_email: str, user_name: str, reset_token: str) -> bool:
        """Envoie un email de réinitialisation de mot de passe"""
        try:
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
            
            # Version texte simple
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
            
            return await self._send_email_via_api(
                to_email=user_email,
                subject="🔐 Réinitialisation de votre mot de passe - RedPill IA",
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur dans send_password_reset_email: {str(e)}")
            return False
    
    async def send_password_changed_confirmation(self, user_email: str, user_name: str) -> bool:
        """Envoie un email de confirmation après changement de mot de passe"""
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
                    .brand {{
                        color: #10b981;
                        font-weight: 700;
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
                        
                        <div class="security-alert">
                            <strong>🔒 Sécurité :</strong> Si vous n'êtes pas à l'origine de cette modification, 
                            contactez-nous <strong>immédiatement</strong> à 
                            <a href="mailto:support@redpill-ia.app" style="color: #dc2626;">support@redpill-ia.app</a>
                        </div>
                        
                        <p style="margin-top: 32px; color: #4b5563;">
                            Cordialement,<br>
                            L'équipe <span class="brand">RedPill IA</span> ✨
                        </p>
                    </div>
                    <div class="footer">
                        <p>Cet email a été envoyé automatiquement par <span class="brand">RedPill IA</span></p>
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

🔒 SÉCURITÉ : Si vous n'êtes pas à l'origine de cette modification, 
contactez-nous IMMÉDIATEMENT à support@redpill-ia.app

Cordialement,
L'équipe RedPill IA ✨
            """
            
            return await self._send_email_via_api(
                to_email=user_email,
                subject="✅ Votre mot de passe a été modifié avec succès - RedPill IA",
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur dans send_password_changed_confirmation: {str(e)}")
            return False

# Instance globale
email_service = EmailService()
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["pages"])

@router.get("/delete-account", response_class=HTMLResponse)
async def delete_account_page():
    """Page de suppression de compte - Clarity"""
    
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Suppression de compte - Clarity</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }

            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 600px;
                width: 100%;
                padding: 40px;
                animation: slideIn 0.5s ease-out;
            }

            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(-30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .header {
                text-align: center;
                margin-bottom: 30px;
            }

            .header h1 {
                font-size: 32px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: 700;
                margin-bottom: 8px;
            }

            .header p {
                color: #6b7280;
                font-size: 16px;
            }

            .former-name {
                color: #9ca3af;
                font-size: 13px;
                font-style: italic;
                margin-top: 4px;
            }

            .warning-box {
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 16px;
                border-radius: 8px;
                margin-bottom: 24px;
            }

            .warning-box h3 {
                color: #92400e;
                font-size: 18px;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
            }

            .warning-box h3::before {
                content: "⚠️";
                margin-right: 8px;
                font-size: 24px;
            }

            .warning-box p {
                color: #78350f;
                font-size: 14px;
                line-height: 1.6;
            }

            h2 {
                color: #1f2937;
                font-size: 22px;
                margin-bottom: 16px;
                margin-top: 24px;
            }

            .info-section {
                background: #f3f4f6;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 24px;
            }

            .info-section h3 {
                color: #374151;
                font-size: 16px;
                margin-bottom: 12px;
                font-weight: 600;
            }

            .info-section ul {
                list-style: none;
                padding: 0;
            }

            .info-section li {
                color: #4b5563;
                padding: 8px 0;
                padding-left: 24px;
                position: relative;
            }

            .info-section li::before {
                content: "✓";
                position: absolute;
                left: 0;
                color: #10b981;
                font-weight: bold;
            }

            .deletion-methods {
                margin-top: 24px;
            }

            .method-card {
                background: white;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
                transition: all 0.3s ease;
            }

            .method-card:hover {
                border-color: #667eea;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
            }

            .method-card h3 {
                color: #1f2937;
                font-size: 18px;
                margin-bottom: 12px;
                display: flex;
                align-items: center;
            }

            .method-card h3 .icon {
                font-size: 24px;
                margin-right: 12px;
            }

            .method-card ol {
                margin-left: 20px;
                color: #4b5563;
            }

            .method-card li {
                margin-bottom: 8px;
                line-height: 1.6;
            }

            .email-box {
                background: #667eea;
                color: white;
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                margin: 24px 0;
            }

            .email-box h3 {
                font-size: 18px;
                margin-bottom: 12px;
            }

            .email-link {
                display: inline-block;
                background: white;
                color: #667eea;
                padding: 12px 24px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
            }

            .email-link:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
            }

            .timeline {
                background: #f3f4f6;
                padding: 20px;
                border-radius: 12px;
                margin-top: 24px;
            }

            .timeline h3 {
                color: #1f2937;
                font-size: 18px;
                margin-bottom: 16px;
            }

            .timeline-item {
                display: flex;
                margin-bottom: 12px;
                align-items: center;
            }

            .timeline-item .step {
                background: #667eea;
                color: white;
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                margin-right: 12px;
                flex-shrink: 0;
            }

            .timeline-item p {
                color: #4b5563;
                font-size: 14px;
            }

            .footer-links {
                margin-top: 32px;
                padding-top: 24px;
                border-top: 1px solid #e5e7eb;
                text-align: center;
            }

            .footer-links a {
                color: #667eea;
                text-decoration: none;
                margin: 0 12px;
                font-size: 14px;
            }

            .footer-links a:hover {
                text-decoration: underline;
            }

            .tech-note {
                color: #9ca3af;
                font-size: 12px;
                margin-top: 8px;
                text-align: center;
            }

            @media (max-width: 768px) {
                .container {
                    padding: 30px 20px;
                }

                .header h1 {
                    font-size: 24px;
                }

                h2 {
                    font-size: 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🗑️ Suppression de compte</h1>
                <p>Clarity</p>
                <p class="former-name">(Anciennement RedPill IA)</p>
            </div>

            <div class="warning-box">
                <h3>Attention</h3>
                <p>
                    La suppression de votre compte est <strong>définitive et irréversible</strong>. 
                    Toutes vos données seront définitivement effacées de nos serveurs sous 30 jours maximum.
                </p>
            </div>

            <div class="info-section">
                <h3>Que se passe-t-il quand vous supprimez votre compte ?</h3>
                <ul>
                    <li>Votre adresse e-mail et votre compte seront définitivement supprimés</li>
                    <li>Vous n'aurez plus accès à l'application Clarity</li>
                    <li>Toutes vos données personnelles seront effacées</li>
                    <li>Votre abonnement sera annulé (s'il est actif)</li>
                    <li>Cette action est irréversible</li>
                </ul>
            </div>

            <h2>Comment supprimer votre compte</h2>

            <div class="deletion-methods">
                <div class="method-card">
                    <h3><span class="icon">📱</span> Méthode 1 : Depuis l'application</h3>
                    <ol>
                        <li>Ouvrez l'application <strong>Clarity</strong></li>
                        <li>Accédez aux <strong>Paramètres</strong> de votre compte</li>
                        <li>Sélectionnez <strong>"Supprimer mon compte"</strong></li>
                        <li>Confirmez la suppression en suivant les instructions</li>
                    </ol>
                </div>

                <div class="method-card">
                    <h3><span class="icon">✉️</span> Méthode 2 : Par e-mail</h3>
                    <p style="color: #4b5563; margin-bottom: 16px;">
                        Envoyez-nous un e-mail avec les informations suivantes :
                    </p>
                    <ul style="color: #4b5563; margin-left: 20px;">
                        <li>Votre adresse e-mail enregistrée</li>
                        <li>Objet : "Demande de suppression de compte Clarity"</li>
                        <li>Confirmation explicite de votre demande</li>
                    </ul>
                </div>
            </div>

            <div class="email-box">
                <h3>Contactez-nous pour supprimer votre compte</h3>
                <a href="mailto:redipill.ia@gmail.com?subject=Demande%20de%20suppression%20de%20compte%20Clarity&body=Bonjour,%0A%0AJe%20souhaite%20supprimer%20mon%20compte%20Clarity.%0A%0AMon%20adresse%20e-mail%20:%20[VOTRE_EMAIL]%0A%0AJe%20confirme%20que%20je%20comprends%20que%20cette%20action%20est%20définitive%20et%20irréversible.%0A%0AMerci" 
                   class="email-link">
                    Envoyer un e-mail
                </a>
            </div>

            <div class="timeline">
                <h3>⏱️ Délai de suppression</h3>
                <div class="timeline-item">
                    <div class="step">1</div>
                    <p>Votre demande est reçue et traitée sous <strong>48 heures</strong></p>
                </div>
                <div class="timeline-item">
                    <div class="step">2</div>
                    <p>Vous recevez une confirmation par e-mail</p>
                </div>
                <div class="timeline-item">
                    <div class="step">3</div>
                    <p>Vos données sont définitivement supprimées sous <strong>30 jours maximum</strong></p>
                </div>
            </div>

            <div class="info-section" style="margin-top: 24px;">
                <h3>ℹ️ Suppression automatique</h3>
                <p style="color: #4b5563;">
                    Notez que votre compte sera automatiquement supprimé après <strong>90 jours d'inactivité</strong> 
                    conformément à notre politique de confidentialité.
                </p>
            </div>

            <div class="footer-links">
                <a href="https://redpill-ia.app/privacy-policy">Politique de confidentialité</a>
                <a href="mailto:redipill.ia@gmail.com">Nous contacter</a>
            </div>

            <p class="tech-note">
                Domaine technique : redpill-ia.app | Application : Clarity
            </p>
        </div>
    </body>
    </html>
    """
    
    return html_content
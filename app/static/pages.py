from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["pages"])

@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page():
    """Page web de réinitialisation de mot de passe"""
    
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Réinitialisation de mot de passe - RedPill IA</title>
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
                max-width: 450px;
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

            .logo {
                text-align: center;
                margin-bottom: 30px;
            }

            .logo h1 {
                font-size: 32px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: 700;
                margin-bottom: 8px;
            }

            .logo p {
                color: #6b7280;
                font-size: 14px;
            }

            h2 {
                color: #1f2937;
                font-size: 24px;
                margin-bottom: 10px;
                text-align: center;
            }

            .subtitle {
                color: #6b7280;
                font-size: 14px;
                text-align: center;
                margin-bottom: 30px;
            }

            .form-group {
                margin-bottom: 20px;
            }

            label {
                display: block;
                color: #374151;
                font-weight: 500;
                margin-bottom: 8px;
                font-size: 14px;
            }

            input {
                width: 100%;
                padding: 12px 16px;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                font-size: 16px;
                transition: all 0.3s ease;
                font-family: inherit;
            }

            input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }

            .password-requirements {
                background: #f3f4f6;
                border-radius: 8px;
                padding: 12px;
                margin-top: 10px;
                font-size: 13px;
                color: #6b7280;
            }

            .requirement {
                display: flex;
                align-items: center;
                margin-bottom: 6px;
            }

            .requirement:last-child {
                margin-bottom: 0;
            }

            .requirement.valid {
                color: #10b981;
            }

            .requirement .icon {
                margin-right: 8px;
                width: 16px;
                height: 16px;
            }

            button {
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 20px;
            }

            button:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
            }

            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }

            .message {
                padding: 12px 16px;
                border-radius: 8px;
                margin-bottom: 20px;
                display: none;
                animation: fadeIn 0.3s ease-out;
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            .message.error {
                background: #fee2e2;
                color: #991b1b;
                border: 1px solid #fecaca;
            }

            .message.success {
                background: #d1fae5;
                color: #065f46;
                border: 1px solid #a7f3d0;
            }

            .message.info {
                background: #dbeafe;
                color: #1e40af;
                border: 1px solid #bfdbfe;
            }

            .success-animation {
                text-align: center;
                display: none;
            }

            .checkmark {
                width: 80px;
                height: 80px;
                margin: 0 auto 20px;
                border-radius: 50%;
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                animation: scaleIn 0.5s ease-out;
            }

            @keyframes scaleIn {
                from {
                    transform: scale(0);
                }
                to {
                    transform: scale(1);
                }
            }

            .checkmark svg {
                width: 50px;
                height: 50px;
                stroke: white;
                stroke-width: 3;
                stroke-linecap: round;
                stroke-linejoin: round;
                fill: none;
                stroke-dasharray: 100;
                stroke-dashoffset: 100;
                animation: draw 0.8s ease-out 0.3s forwards;
            }

            @keyframes draw {
                to {
                    stroke-dashoffset: 0;
                }
            }

            .success-text {
                color: #1f2937;
                font-size: 24px;
                font-weight: 600;
                margin-bottom: 10px;
            }

            .success-message {
                color: #6b7280;
                font-size: 14px;
                margin-bottom: 20px;
            }

            .back-link {
                display: inline-block;
                color: #667eea;
                text-decoration: none;
                font-weight: 500;
                padding: 10px 20px;
                border-radius: 8px;
                transition: all 0.3s ease;
            }

            .back-link:hover {
                background: #f3f4f6;
            }

            .loader {
                border: 3px solid #f3f4f6;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                animation: spin 0.8s linear infinite;
                display: inline-block;
                margin-left: 10px;
                vertical-align: middle;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            @media (max-width: 480px) {
                .container {
                    padding: 30px 20px;
                }

                h2 {
                    font-size: 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <h1>🔐 RedPill IA</h1>
                <p>Réinitialisation sécurisée</p>
            </div>

            <div id="resetForm">
                <h2>Nouveau mot de passe</h2>
                <p class="subtitle">Choisissez un mot de passe fort et unique</p>

                <div id="messageBox" class="message"></div>

                <form id="passwordForm">
                    <div class="form-group">
                        <label for="newPassword">Nouveau mot de passe</label>
                        <input 
                            type="password" 
                            id="newPassword" 
                            name="newPassword"
                            placeholder="Entrez votre nouveau mot de passe"
                            required
                            minlength="6"
                        >
                    </div>

                    <div class="form-group">
                        <label for="confirmPassword">Confirmer le mot de passe</label>
                        <input 
                            type="password" 
                            id="confirmPassword" 
                            name="confirmPassword"
                            placeholder="Confirmez votre mot de passe"
                            required
                            minlength="6"
                        >
                    </div>

                    <div class="password-requirements">
                        <div class="requirement" id="req-length">
                            <span class="icon">○</span>
                            <span>Au moins 6 caractères</span>
                        </div>
                        <div class="requirement" id="req-match">
                            <span class="icon">○</span>
                            <span>Les mots de passe correspondent</span>
                        </div>
                    </div>

                    <button type="submit" id="submitBtn">
                        Réinitialiser le mot de passe
                    </button>
                </form>
            </div>

            <div id="successAnimation" class="success-animation">
                <div class="checkmark">
                    <svg viewBox="0 0 52 52">
                        <path d="M14 27l8 8 16-16"/>
                    </svg>
                </div>
                <div class="success-text">Mot de passe modifié !</div>
                <div class="success-message">
                    Votre mot de passe a été mis à jour avec succès.<br>
                    Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.
                </div>
                <a href="#" class="back-link" onclick="openApp()">Ouvrir l'application</a>
            </div>
        </div>

        <script>
            const urlParams = new URLSearchParams(window.location.search);
            const token = urlParams.get('token');

            const form = document.getElementById('passwordForm');
            const newPasswordInput = document.getElementById('newPassword');
            const confirmPasswordInput = document.getElementById('confirmPassword');
            const messageBox = document.getElementById('messageBox');
            const submitBtn = document.getElementById('submitBtn');
            const resetForm = document.getElementById('resetForm');
            const successAnimation = document.getElementById('successAnimation');

            if (!token) {
                showMessage('Lien invalide. Veuillez demander un nouveau lien de réinitialisation.', 'error');
                submitBtn.disabled = true;
            } else {
                validateToken();
            }

            newPasswordInput.addEventListener('input', updateRequirements);
            confirmPasswordInput.addEventListener('input', updateRequirements);

            function updateRequirements() {
                const password = newPasswordInput.value;
                const confirm = confirmPasswordInput.value;

                const reqLength = document.getElementById('req-length');
                if (password.length >= 6) {
                    reqLength.classList.add('valid');
                    reqLength.querySelector('.icon').textContent = '✓';
                } else {
                    reqLength.classList.remove('valid');
                    reqLength.querySelector('.icon').textContent = '○';
                }

                const reqMatch = document.getElementById('req-match');
                if (password && confirm && password === confirm) {
                    reqMatch.classList.add('valid');
                    reqMatch.querySelector('.icon').textContent = '✓';
                } else {
                    reqMatch.classList.remove('valid');
                    reqMatch.querySelector('.icon').textContent = '○';
                }
            }

            async function validateToken() {
                try {
                    const response = await fetch(`/api/auth/validate-reset-token/${token}`);
                    const data = await response.json();

                    if (!data.valid) {
                        showMessage('Ce lien a expiré ou est invalide. Veuillez demander un nouveau lien.', 'error');
                        submitBtn.disabled = true;
                    } else {
                        showMessage('Lien valide. Vous pouvez créer votre nouveau mot de passe.', 'info');
                    }
                } catch (error) {
                    console.error('Erreur validation token:', error);
                }
            }

            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                const newPassword = newPasswordInput.value;
                const confirmPassword = confirmPasswordInput.value;

                if (newPassword.length < 6) {
                    showMessage('Le mot de passe doit contenir au moins 6 caractères.', 'error');
                    return;
                }

                if (newPassword !== confirmPassword) {
                    showMessage('Les mots de passe ne correspondent pas.', 'error');
                    return;
                }

                submitBtn.disabled = true;
                submitBtn.innerHTML = 'Réinitialisation en cours...<span class="loader"></span>';

                try {
                    const response = await fetch('/api/auth/reset-password', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            token: token,
                            new_password: newPassword
                        })
                    });

                    const data = await response.json();

                    if (data.success) {
                        resetForm.style.display = 'none';
                        successAnimation.style.display = 'block';
                    } else {
                        showMessage(data.message || 'Une erreur est survenue. Veuillez réessayer.', 'error');
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Réinitialiser le mot de passe';
                    }
                } catch (error) {
                    showMessage('Erreur de connexion. Veuillez vérifier votre connexion internet.', 'error');
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Réinitialiser le mot de passe';
                }
            });

            function showMessage(message, type) {
                messageBox.textContent = message;
                messageBox.className = `message ${type}`;
                messageBox.style.display = 'block';

                if (type !== 'error') {
                    setTimeout(() => {
                        messageBox.style.display = 'none';
                    }, 5000);
                }
            }

            function openApp() {
                window.location.href = 'redpillia://login';
                
                setTimeout(() => {
                    alert('Veuillez ouvrir votre application RedPill IA pour vous connecter avec votre nouveau mot de passe.');
                }, 2000);
            }
        </script>
    </body>
    </html>
    """
    
    return html_content


@router.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy_page():
    """Page de politique de confidentialité"""
    
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Politique de Confidentialité - RedPill IA</title>
        <meta name="description" content="Politique de confidentialité de l'application RedPill IA">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #1f2937;
                background: #f9fafb;
            }

            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 20px;
                text-align: center;
            }

            .header h1 {
                font-size: 32px;
                font-weight: 700;
                margin-bottom: 10px;
            }

            .header p {
                font-size: 16px;
                opacity: 0.9;
            }

            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: white;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }

            .last-updated {
                background: #f3f4f6;
                padding: 12px 16px;
                border-radius: 8px;
                margin-bottom: 30px;
                font-size: 14px;
                color: #6b7280;
            }

            h2 {
                color: #111827;
                font-size: 24px;
                margin-top: 40px;
                margin-bottom: 16px;
                padding-bottom: 8px;
                border-bottom: 2px solid #667eea;
            }

            h3 {
                color: #374151;
                font-size: 18px;
                margin-top: 24px;
                margin-bottom: 12px;
            }

            p {
                margin-bottom: 16px;
                color: #4b5563;
            }

            ul, ol {
                margin-left: 24px;
                margin-bottom: 16px;
                color: #4b5563;
            }

            li {
                margin-bottom: 8px;
            }

            .highlight {
                background: #fef3c7;
                padding: 16px;
                border-left: 4px solid #f59e0b;
                border-radius: 4px;
                margin: 20px 0;
            }

            .contact-box {
                background: #f3f4f6;
                padding: 20px;
                border-radius: 8px;
                margin: 30px 0;
            }

            .contact-box h3 {
                margin-top: 0;
            }

            .email-link {
                color: #667eea;
                text-decoration: none;
                font-weight: 500;
            }

            .email-link:hover {
                text-decoration: underline;
            }

            .footer {
                text-align: center;
                padding: 20px;
                color: #6b7280;
                font-size: 14px;
            }

            @media (max-width: 768px) {
                .header h1 {
                    font-size: 24px;
                }

                h2 {
                    font-size: 20px;
                }

                .container {
                    padding: 30px 16px;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔐 Politique de Confidentialité</h1>
            <p>RedPill IA - Application de conseil relationnel</p>
        </div>

        <div class="container">
            <div class="last-updated">
                <strong>Dernière mise à jour :</strong> 2 novembre 2025
            </div>

            <p>
                Chez <strong>RedPill IA</strong>, nous prenons très au sérieux la protection de vos données personnelles. 
                Cette politique de confidentialité explique quelles données nous collectons, pourquoi nous les collectons, 
                et comment nous les utilisons.
            </p>

            <h2>1. Responsable du traitement des données</h2>
            <p>
                <strong>Redpill IA</strong><br>
                Email de contact : <a href="mailto:redipill.ia@gmail.com" class="email-link">redipill.ia@gmail.com</a>
            </p>

            <h2>2. Données collectées</h2>
            <p>Notre application collecte uniquement les données suivantes :</p>

            <h3>2.1 Données d'identification et d'authentification</h3>
            <ul>
                <li><strong>Adresse e-mail</strong> : utilisée pour créer votre compte et vous permettre de vous connecter</li>
                <li><strong>Mot de passe</strong> : stocké de manière sécurisée sous forme hachée (jamais en clair)</li>
            </ul>

            <div class="highlight">
                <strong>Important :</strong> Les conversations que vous avez avec notre assistant IA ne sont PAS sauvegardées. 
                Elles sont traitées en temps réel et ne sont pas conservées sur nos serveurs.
            </div>

            <h2>3. Finalité du traitement</h2>
            <p>Nous utilisons vos données uniquement pour :</p>
            <ul>
                <li>Vous permettre de créer un compte et de vous authentifier</li>
                <li>Assurer la sécurité de votre compte</li>
                <li>Vous fournir l'accès à notre assistant IA de conseil relationnel</li>
                <li>Gérer votre abonnement (via Google Play ou App Store)</li>
            </ul>

            <h2>4. Stockage et sécurité des données</h2>
            
            <h3>4.1 Lieu de stockage</h3>
            <p>
                Vos données sont stockées de manière sécurisée sur des serveurs hébergés par <strong>DigitalOcean</strong>.
            </p>

            <h3>4.2 Mesures de sécurité</h3>
            <ul>
                <li>Toutes les données sont chiffrées en transit (HTTPS/TLS)</li>
                <li>Les mots de passe sont hachés avec des algorithmes cryptographiques robustes</li>
                <li>Accès aux serveurs strictement contrôlé</li>
                <li>Surveillance continue de la sécurité</li>
            </ul>

            <h2>5. Durée de conservation</h2>
            <p>
                Vos données personnelles sont conservées tant que votre compte est actif. 
                Si vous supprimez votre compte ou si votre compte reste inactif pendant plus de <strong>90 jours</strong>, 
                vos données seront automatiquement supprimées de nos serveurs.
            </p>

            <h2>6. Partage des données</h2>
            <p><strong>Nous ne vendons jamais vos données.</strong></p>
            
            <p>Vos données peuvent être partagées uniquement avec :</p>
            <ul>
                <li><strong>DigitalOcean</strong> : hébergement sécurisé de nos serveurs</li>
                <li><strong>Google Play / Apple App Store</strong> : gestion des paiements d'abonnement (nous ne recevons aucune donnée bancaire)</li>
            </ul>

            <p>
                Nous ne partageons vos données avec des tiers que si requis par la loi ou pour protéger nos droits légaux.
            </p>

            <h2>7. Vos droits (RGPD)</h2>
            <p>Conformément au Règlement Général sur la Protection des Données (RGPD), vous disposez des droits suivants :</p>
            
            <ul>
                <li><strong>Droit d'accès</strong> : obtenir une copie de vos données personnelles</li>
                <li><strong>Droit de rectification</strong> : corriger vos données inexactes</li>
                <li><strong>Droit à l'effacement</strong> : supprimer votre compte et toutes vos données</li>
                <li><strong>Droit à la portabilité</strong> : récupérer vos données dans un format structuré</li>
                <li><strong>Droit d'opposition</strong> : vous opposer au traitement de vos données</li>
                <li><strong>Droit de limitation</strong> : limiter le traitement de vos données</li>
            </ul>

            <p>
                Pour exercer ces droits, contactez-nous à : 
                <a href="mailto:redipill.ia@gmail.com" class="email-link">redipill.ia@gmail.com</a>
            </p>

            <h2>8. Suppression de votre compte</h2>
            <p>
                Vous pouvez demander la suppression de votre compte et de toutes vos données à tout moment en suivant 
                la procédure décrite sur notre page : 
                <a href="https://redpill-ia.app/delete-account" class="email-link">https://redpill-ia.app/delete-account</a>
            </p>

            <p>
                Votre compte et toutes les données associées seront définitivement supprimés sous <strong>30 jours maximum</strong>.
            </p>

            <h2>9. Cookies et technologies similaires</h2>
            <p>
                Notre application n'utilise pas de cookies de suivi ou de technologies publicitaires. 
                Nous utilisons uniquement des cookies techniques strictement nécessaires au fonctionnement de l'application 
                (session d'authentification).
            </p>

            <h2>10. Modifications de cette politique</h2>
            <p>
                Nous pouvons mettre à jour cette politique de confidentialité. En cas de modifications importantes, 
                nous vous informerons via l'application ou par e-mail. La date de dernière mise à jour est indiquée en haut de cette page.
            </p>

            <h2>11. Mineurs</h2>
            <p>
                Notre application est destinée aux personnes âgées de <strong>18 ans et plus</strong>. 
                Nous ne collectons pas sciemment de données auprès de mineurs.
            </p>

            <h2>12. Données sensibles</h2>
            <p>
                Bien que notre assistant IA traite des conversations sur les relations personnelles, 
                <strong>aucune conversation n'est sauvegardée ou stockée</strong>. Toutes les interactions sont traitées 
                en temps réel et sont immédiatement supprimées après traitement.
            </p>

            <div class="contact-box">
                <h3>📧 Nous contacter</h3>
                <p>
                    Pour toute question concernant cette politique de confidentialité ou pour exercer vos droits, 
                    vous pouvez nous contacter à :
                </p>
                <p>
                    <strong>Email :</strong> <a href="mailto:redipill.ia@gmail.com" class="email-link">redipill.ia@gmail.com</a><br>
                    <strong>Entreprise :</strong> Redpill IA<br>
                    <strong>Site web :</strong> <a href="https://redpill-ia.app" class="email-link">https://redpill-ia.app</a>
                </p>
            </div>

            <h2>13. Autorité de contrôle</h2>
            <p>
                Si vous estimez que vos droits ne sont pas respectés, vous avez le droit de déposer une plainte 
                auprès de votre autorité de protection des données locale (CNIL en France).
            </p>
        </div>

        <div class="footer">
            <p>© 2025 Redpill IA - Tous droits réservés</p>
        </div>
    </body>
    </html>
    """
    
    return html_content


@router.get("/delete-account", response_class=HTMLResponse)
async def delete_account_page():
    """Page de suppression de compte"""
    
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Suppression de compte - RedPill IA</title>
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
                <p>RedPill IA</p>
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
                    <li>Vous n'aurez plus accès à l'application</li>
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
                        <li>Ouvrez l'application RedPill IA</li>
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
                        <li>Objet : "Demande de suppression de compte"</li>
                        <li>Confirmation explicite de votre demande</li>
                    </ul>
                </div>
            </div>

            <div class="email-box">
                <h3>Contactez-nous pour supprimer votre compte</h3>
                <a href="mailto:redipill.ia@gmail.com?subject=Demande%20de%20suppression%20de%20compte&body=Bonjour,%0A%0AJe%20souhaite%20supprimer%20mon%20compte%20RedPill%20IA.%0A%0AMon%20adresse%20e-mail%20:%20[VOTRE_EMAIL]%0A%0AJe%20confirme%20que%20je%20comprends%20que%20cette%20action%20est%20définitive%20et%20irréversible.%0A%0AMerci" 
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
        </div>
    </body>
    </html>
    """
    
    return html_content
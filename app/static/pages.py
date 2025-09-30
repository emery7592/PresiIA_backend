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
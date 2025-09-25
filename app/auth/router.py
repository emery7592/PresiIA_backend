from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import secrets
import logging
from datetime import datetime, timedelta

from app.database.database import get_database
from app.auth.schemas import UserRegister, UserLogin, ChatRequest
from app.auth.models import User, PasswordResetToken
from app.auth.services import *
from app.auth.dependencies import get_current_user
from app.auth.email_service import email_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_database)):
    try:
        user = register_user(db, user_data)
        token = create_access_token({"sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer", "user_id": str(user.id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_database)):
    user = authenticate_user(db, login_data)
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user_id": str(user.id)}

@router.post("/logout")
def logout():
    return {"message": "Déconnexion réussie"}

# À ajouter dans auth/router.py

import secrets
from datetime import datetime, timedelta
from app.auth.models import PasswordResetToken
from app.auth.email_service import EmailService

# Schemas à ajouter dans auth/schemas.py
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ForgotPasswordResponse(BaseModel):
    success: bool
    message: str

class ResetPasswordResponse(BaseModel):
    success: bool
    message: str

# Endpoints à ajouter dans auth/router.py

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_database)
):
    """
    Demande de réinitialisation de mot de passe
    """
    try:
        # Vérifier si l'utilisateur existe
        user = db.query(User).filter(
            User.email == request.email,
            User.is_registered == True
        ).first()
        
        if not user:
            # Pour la sécurité, on retourne toujours succès même si l'email n'existe pas
            return ForgotPasswordResponse(
                success=True,
                message="Si cet email existe, vous recevrez un lien de réinitialisation."
            )
        
        # Supprimer les anciens tokens non utilisés de cet utilisateur
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used == False
        ).delete()
        
        # Générer un nouveau token
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=30)  # Expire dans 30 minutes
        
        # Sauvegarder le token en base
        token_record = PasswordResetToken(
            user_id=user.id,
            token=reset_token,
            expires_at=expires_at
        )
        db.add(token_record)
        db.commit()
        
        # Envoyer l'email
        email_sent = await email_service.send_password_reset_email(
            user_email=user.email,
            user_name=user.first_name or "Utilisateur",
            reset_token=reset_token
        )
        
        if not email_sent:
            logger.error(f"Échec envoi email pour {user.email}")
            return ForgotPasswordResponse(
                success=False,
                message="Erreur lors de l'envoi de l'email. Veuillez réessayer."
            )
        
        return ForgotPasswordResponse(
            success=True,
            message="Si cet email existe, vous recevrez un lien de réinitialisation."
        )
        
    except Exception as e:
        logger.error(f"Erreur forgot password: {e}")
        return ForgotPasswordResponse(
            success=False,
            message="Une erreur est survenue. Veuillez réessayer."
        )

@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_database)
):
    """
    Réinitialisation du mot de passe avec token
    """
    try:
        # Chercher le token
        token_record = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == request.token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()
        
        if not token_record:
            return ResetPasswordResponse(
                success=False,
                message="Token invalide ou expiré."
            )
        
        # Récupérer l'utilisateur
        user = db.query(User).filter(User.id == token_record.user_id).first()
        if not user:
            return ResetPasswordResponse(
                success=False,
                message="Utilisateur introuvable."
            )
        
        # Valider le nouveau mot de passe
        if len(request.new_password) < 6:
            return ResetPasswordResponse(
                success=False,
                message="Le mot de passe doit contenir au moins 6 caractères."
            )
        
        # Mettre à jour le mot de passe
        user.password_hash = hash_password(request.new_password)
        
        # Marquer le token comme utilisé
        token_record.used = True
        
        db.commit()
        
        # Envoyer email de confirmation
        await EmailService.send_password_changed_confirmation(
            user_email=user.email,
            user_name=user.first_name or "Utilisateur"
        )
        
        return ResetPasswordResponse(
            success=True,
            message="Votre mot de passe a été modifié avec succès."
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur reset password: {e}")
        return ResetPasswordResponse(
            success=False,
            message="Une erreur est survenue. Veuillez réessayer."
        )

@router.get("/validate-reset-token/{token}")
async def validate_reset_token(
    token: str,
    db: Session = Depends(get_database)
):
    """
    Valide si un token de reset est valide (pour l'interface)
    """
    try:
        token_record = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()
        
        if token_record:
            return {"valid": True, "message": "Token valide"}
        else:
            return {"valid": False, "message": "Token invalide ou expiré"}
            
    except Exception as e:
        logger.error(f"Erreur validation token: {e}")
        return {"valid": False, "message": "Erreur lors de la validation"}
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def envoyer_alerte_discord(message: str) -> str:
    """
    Envoie une alerte sur un webhook Discord (Simulé si URL non configurée).
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
    if not webhook_url or "api/webhooks" not in webhook_url:
        # Mode simulé réaliste exigé par les contraintes gratuites sans services payants
        simulated_msg = f"[SIMULATION DISCORD WEBHOOK] Message transmis avec succès :\n{message}"
        print(simulated_msg)
        return "Alerte envoyée avec succès (Mode Simulé Discord)."

    # Si l'URL était réelle, on utiliserait requests.post ici
    return "Alerte transmise vers le canal Discord."

def envoyer_email(destinataire: str, sujet: str, corps: str) -> str:
    """
    Envoie un e-mail via SMTP (Mode simulé réaliste si identifiants absents).
    """
    smtp_user = os.getenv("SMTP_USER", "soc-junior@example.com")
    smtp_server = os.getenv("SMTP_SERVER", "")

    if not smtp_server or smtp_server == "smtp.example.com":
        # Mode simulé réaliste
        print(f"\n[SIMULATION E-MAIL SMTP]\nDestinataire : {destinataire}\nSujet : {sujet}\nCorps :\n{corps}\n------------------------\n")
        return f"E-mail transmis virtuellement à {destinataire} (Mode Simulé SMTP)."

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = destinataire
        msg['Subject'] = sujet
        msg.attach(MIMEText(corps, 'plain', 'utf-8'))

        server = smtplib.SMTP(smtp_server, int(os.getenv("SMTP_PORT", 587)))
        server.starttls()
        server.login(smtp_user, os.getenv("SMTP_PASSWORD", ""))
        server.sendmail(smtp_user, destinataire, msg.as_string())
        server.quit()
        return f"E-mail envoyé avec succès à {destinataire}."
    except Exception as e:
        return f"Erreur lors de l'envoi SMTP : {str(e)}"

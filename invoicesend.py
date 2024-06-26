import base64
from email.message import EmailMessage
from email.mime.application import MIMEApplication

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import mimetypes
import os
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText


def createDraft(service, toEmail, nom, company, filenames):
    try:
        mime_message = EmailMessage()

        mime_message["To"] = toEmail
        mime_message["From"] = "partenaires@jdglaval.com"
        mime_message["Subject"] = "Facture - Partenariat avec les Jeux de Génie"

        # text
        mime_message.set_content(
            f"""Bonjour {nom},

Nous sommes ravis d'apprendre que {company} soutiendra la Délégation des Jeux de Génie 2025 de l'Université Laval!

Vous trouverez ci-joint la facture à payer dans un délai de 30 jours soit par chèque adressé à "AESGUL (Jeux de Génie 2025)" soit par dépôt direct (le spécimen de chèque se trouve ci-joint).

S'il vous plaît envoyez-moi un avis de paiement une fois celui-ci fait.

N'hésitez pas à me contacter si vous avez des questions.

Au plaisir d'être partenaire avec vous!

Dan Lévy
Vice-Président au Partenariat
Délégation de l'Université Laval des Jeux de Génie 2025
partenariats@jdglaval.com
tél: 418-575-2913
www.jdglaval.com
"""
        )

        for filename in filenames:
            with open(filename, 'rb') as content_file:
                content = content_file.read()
                mime_message.add_attachment(content, maintype='application', subtype=(
                    filename.split('.')[1]), filename=filename.replace("factures/", ""))

        encoded_message = base64.urlsafe_b64encode(
            mime_message.as_bytes()).decode()

        create_draft_request_body = {"message": {"raw": encoded_message}}
        # pylint: disable=E1101
        draft = (
            service.users()
            .drafts()
            .create(userId="me", body=create_draft_request_body)
            .execute()
        )
    except HttpError as error:
        print(f"An error occurred: {error}")
        draft = None

    return draft


def sendDraft(service, draft_id):
    try:
        # pylint: disable=E1101
        send_message = (
            service.users().drafts().send(userId='me', body={
                'id': draft_id}).execute()
        )
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message


def sendPDF(service, toEmail, nom, company, filenames):
    draft = createDraft(service=service, toEmail=toEmail, nom=nom,
                        company=company, filenames=filenames)

    sendDraft(service=service, draft_id=draft["id"])

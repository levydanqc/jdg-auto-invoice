from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os

from invoicecreate import createPDF
from invoiceupload import uploadPDF
from invoicesignature import downloadSignature
from invoicesend import sendPDF


def getCreds(SCOPES, service):
    creds = None

    if (service == "sheets"):
        token_filename = "token_sheets.json"
    elif (service == "gmail"):
        token_filename = "token_gmail.json"
    else:
        token_filename = "token_drive.json"

    if os.path.exists(token_filename):
        creds = Credentials.from_authorized_user_file(token_filename, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_filename, "w") as token:
            token.write(creds.to_json())
    return creds


def getRows(service, id, range):
    try:
        gsheet = service.spreadsheets()
        result = (
            gsheet.values()
            .get(spreadsheetId=id, range=range)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        return values
    except HttpError as err:
        print(err)


def updateRow(service, id, range, row):
    try:
        values = [row]
        body = {"values": values}
        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=id,
                range=range,
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


if __name__ == "__main__":
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = getCreds(SCOPES, "sheets")
    sheets = build("sheets", "v4", credentials=creds)

    SCOPES = ["https://www.googleapis.com/auth/drive"]
    creds = getCreds(SCOPES, "drive")
    drive = build("drive", "v3", credentials=creds)

    SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]
    creds = getCreds(SCOPES, "gmail")
    gmail = build("gmail", "v1", credentials=creds)

    SPREADSHEET_ID = "1r73sRCD4PHWhCOqEiErmvdcmXnfTnpFRSdnEzRWlKx4"
    RANGE_NAME = "A1:W20"
    rows = getRows(service=sheets, id=SPREADSHEET_ID,
                   range=RANGE_NAME)

    for i, row in enumerate(rows):
        if (len(row) == 22):  # new commandite
            # Create PDF File
            pdf_name = createPDF(row)

            company = row[14]
            signature_name = downloadSignature(company=company, url=row[21])

            # Upload PDF to Google Drive
            uploadPDF(service=drive, company=company,
                      filenames=[pdf_name, signature_name])

            # Send PDF by email with Gmail
            sendPDF(service=gmail, toEmail=row[16], nom=row[15], company=company,
                    filenames=[f"factures/{pdf_name}", "Specimen-JDG-UL.pdf"])

            # Update row (Sent as True)
            row.append('TRUE')
            updateRow(service=sheets, id=SPREADSHEET_ID,
                      range=f"A{i+1}:W{i+1}", row=row)

from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def create_folder(service, folder):
    try:
        file_metadata = {
            "name": folder,
            "parents": ["1Z98M-8UwI2dKpW1_ykV11TV2Pfk77QQ_"],
            "mimeType": "application/vnd.google-apps.folder",
        }

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata,
                                      supportsAllDrives=True, fields="id").execute()

        return file.get("id")

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def upload_to_folder(service, filename, folder_id):
    try:
        file_metadata = {"name": filename, "parents": [folder_id]}
        media = MediaFileUpload(f"factures/{filename}")
        # pylint: disable=maybe-no-member
        file = (
            service.files()
            .create(body=file_metadata, supportsAllDrives=True, media_body=media, fields="id")
            .execute()
        )

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file.get("id")


def uploadPDF(service, filenames, company):
    folder_id = create_folder(
        service=service, folder=company)

    for filename in filenames:
        upload_to_folder(service=service, filename=filename,
                         folder_id=folder_id)

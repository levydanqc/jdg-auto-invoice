import requests


def downloadSignature(company, url):
    img_data = requests.get(url).content

    filename = f"{company}-signature.png"
    with open(f"factures/{filename}", 'wb') as file:
        file.write(img_data)

    return filename

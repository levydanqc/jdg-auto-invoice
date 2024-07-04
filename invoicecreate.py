from datetime import datetime, timedelta
import subprocess

items_doc = {
    "Publications sur les médias sociaux": "publications-ms",
    "Possibilité de parrainer un événement spécial": "parrainage",
    "Ajout d’une bannière publicitaire sur nos photos": "banniere-pub",
    "Participation à la soirée de réseautage": "reseautage",
    "Temps de parole durant la soirée de réseautage": "temps-parole",
    "Présentation d’une vidéo promotionnelle": "video-promo",
    "Visite des bureaux du partenaire": "visite",
    "Rencontre Machine  ou Entrep’": "rencontre",
}


def getDates(date_str):
    date_format = '%Y-%m-%d'
    date_obj = datetime.strptime(date_str, date_format)

    due_delta = timedelta(days=30)
    due_date = date_obj + due_delta
    return [date_obj.strftime('%d-%m-%Y'), due_date.strftime('%d-%m-%Y')]


def createInvoice(compagny, price, name, email, phone, date_str, address, plan, items, description):
    with open('tex/invoice.tex', 'r') as file:
        filedata = file.read()

    date, due = getDates(date_str)

    filedata = filedata.replace('[COMPANY]', compagny)
    filedata = filedata.replace('[TOTAL]', price)
    filedata = filedata.replace('[NOM]', name)
    filedata = filedata.replace('[EMAIL]', email)
    filedata = filedata.replace('[PHONE]', f"+ {phone[0]} {phone[1:]}")
    filedata = filedata.replace('[ADDRESS]', address)
    filedata = filedata.replace('[DATE]', date)
    filedata = filedata.replace('[DUE]', due)
    filedata = filedata.replace('[PLAN]', plan)
    filedata = filedata.replace('[ITEMS]', items)
    filedata = filedata.replace('[DESCRIPTION]', description)

    filename = f"invoice-{compagny.replace(' ', '-')}.tex"
    with open(f"tex/{filename}", 'w') as file:
        file.write(filedata)

    return filename


def generatePDF(filename):
    proc = subprocess.call(['pdflatex', filename], cwd='tex',
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cleanup(filename)


def cleanup(filename):
    subprocess.call(f'rm -f {filename} *.aux *.log', cwd='tex', shell=True)
    subprocess.call(
        f"mv tex/{filename.replace('.tex', '.pdf')} factures/", shell=True)


def getPlanTex(plan_name):
    with open(f'plan/{plan_name}.tex', 'r') as file:
        filedata = file.read()
    return filedata


def getItemsTex(items_names):
    tex = ""
    for item in items_names:
        with open(f'ajout/{item}.tex', 'r') as file:
            tex += file.read()
    return tex


def getDescription(plan_name, items_names):
    tex = ""
    if ("reseautage" in items_names or (plan_name != "matériel" and plan_name != "bronze")):
        with open('description/reseautage.tex', 'r') as file:
            tex += file.read()

    if ("visite" in items_names):
        with open('description/visite.tex', 'r') as file:
            tex += file.read()

    return tex


def getPlanItemsDescription(plan_str, items_str):
    plan_name = plan_str.replace('Partenariat ', '').lower()
    plan = getPlanTex(plan_name)

    if items_str != "":
        items_names = [items_doc[item] for item in items_str.split(', ')]
        items = getItemsTex(items_names)
    else:
        items_names = []
        items = ""

    description = getDescription(plan_name, items_names)
    return [plan, items, description]


def createPDF(row):
    plan, items, description = getPlanItemsDescription(
        plan_str=row[4], items_str=row[5])
    filename = createInvoice(compagny=row[14], price=row[3], name=row[15], email=row[16],
                             phone=row[17], date_str=row[18], address=row[19],
                             plan=plan, items=items, description=description)
    generatePDF(filename)

    pdf = filename.replace('.tex', '.pdf')

    return pdf

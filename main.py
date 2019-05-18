from src.api import WorkSession
from src.invoice import MyInvoice
import os
import sys
import csv
from datetime import datetime
from InvoiceGenerator.api import Invoice, Client, Provider, Creator
from config import *


# choose english as language
os.environ["INVOICE_LANG"] = "en"


# Parse infos from config
provider = Provider(**PROVIDER)
projects = {}
clients = {}
for k, v in CLIENTS.items():
    clients[k] = Client(**v)


# Read a Toggl csv report
with open(sys.argv[1], "r", encoding='utf-8-sig') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    columns = []

    # Parse work sessions and add them to their respective projects
    for row in csv_reader:
        if not columns:
            columns = row
        else:
            work_session = WorkSession(row, columns, HOURLY_RATE)
            if work_session.project not in projects:
                projects[work_session.project] = []
            projects[work_session.project].append(work_session)


for k, v in projects.items():
    # for each Project, create an invoice
    creator = Creator('me')
    invoice = Invoice(clients[k], provider, creator)
    invoice.date = datetime.now()
    invoice.number = datetime.now().strftime('%Y%m%d')
    invoice.currency = '$'
    invoice.currency_locale = 'en_US'
    invoice.title = k.capitalize()

    for item in v:
        # insert each work session in the invoice
        invoice.add_item(item)
    pdfInvoice = MyInvoice(invoice)
    pdfInvoice.gen("invoices/invoice-" + k + "-" +
                   datetime.now().strftime('%Y%m%d') + ".pdf")

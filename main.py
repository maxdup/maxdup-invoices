from git import *
from src.api import WorkSession
from src.invoice import MyInvoice
import re
import os
import sys
import csv
from datetime import datetime
from datetime import timedelta
from InvoiceGenerator.api import Invoice, Client, Provider, Creator
from config import *


# choose english as language
os.environ["INVOICE_LANG"] = "en"


# Parse infos from config
provider = Provider(**PROVIDER)
projects = {}
clients = {}
for k, v in CLIENTS.items():
    clients[k] = Client(**v['info'])


# Read a Toggl csv report
with open(sys.argv[1], "r", encoding='utf-8-sig') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    columns = []

    # Parse work sessions and add them to their respective projects
    for row in csv_reader:
        if not columns:
            columns = row
        else:
            work_session = WorkSession(row, columns)
            if work_session.project not in projects:
                projects[work_session.project] = []
            if 'rate' in CLIENTS[work_session.project]:
                work_session.price = CLIENTS[work_session.project]['rate']

            projects[work_session.project].append(work_session)


class Commit():

    def __init__(self, data):
        lines = data.split('\n')
        message = ''
        self.merge = False
        self.date = None
        for line in lines:
            if (line == '' or line == '\n') and not self.date:
                pass
            elif bool(re.match('merge:', line, re.IGNORECASE)):
                self.merge = True
                pass
            elif bool(re.match('author:', line, re.IGNORECASE)):
                self.author = line.split('Author: ')[1].strip().split(' ')[0]
                pass
            elif bool(re.match('date:', line, re.IGNORECASE)):
                self.date = line.split('Date: ')[1].strip().split(' ')[0]
                pass
            elif self.date:
                message += line
        self.message = message.strip()


for k, v in projects.items():
    # for each Project, find commits
    daily_log = ''

    repos = []
    if 'repos' not in CLIENTS[k]:
        pass

    for repo in CLIENTS[k]['repos']:
        repos.append(Git("../soulzone-web-shared"))

    for work_session in v:
        # for each session
        since = datetime.strftime(work_session.date, '"%Y-%m-%d"')
        until = datetime.strftime(
            work_session.date + timedelta(days=1), '"%Y-%m-%d"')

        # for each repo
        for repo in repos:
            daily_log = repo.log(since=since, until=until, date='raw')
            for raw_commit in daily_log.split('\ncommit'):
                commit = Commit(raw_commit)
                if commit.author == 'maxime' or\
                   commit.author == 'maxdup':
                    work_session.add_commit(commit)

for k, v in projects.items():
    # for each Project, create an invoice
    creator = Creator('me')
    invoice = Invoice(clients[k], provider, creator)
    invoice.date = datetime.now()
    invoice.number = datetime.now().strftime('%Y%m%d')
    invoice.currency = '$'
    invoice.currency_locale = 'en_US'
    invoice.title = k.capitalize()

    for work_session in v:
        # insert each work session in the invoice
        invoice.add_item(work_session)
    pdfInvoice = MyInvoice(invoice)
    pdfInvoice.gen("invoices/invoice-" + k + "-" +
                   datetime.now().strftime('%Y%m%d') + ".pdf")

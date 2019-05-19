from datetime import datetime

from InvoiceGenerator.api import Item

import re
from operator import mul
from decimal import Decimal
factors = (60, 1, 1/60)


class WorkSession(Item):

    def __init__(self, row, columns):

        self.count = row[columns.index('Duration')]
        self.price = 0
        self._description = row[columns.index('Title')]
        self.unit = ''
        self.tax = 0

        self.project = row[columns.index('Project')]
        self.client = row[columns.index('Client')]
        self.date = datetime.strptime(
            self._description.split(' - ')[0], '%Y/%m/%d')

        self.repo = ''
        self._commits = []

    def add_commit(self, commit):
        self._commits.append(commit)

    def sort_commits(self):
        self._commits.sort(key=lambda x: x.date)

    @property
    def commits(self):

        if not self._commits:
            return ''

        details = 'Commits:'
        for commit in self._commits:
            if not commit.merge:
                details += ('<br/>(' + commit.repo + ') ' + commit.message)
        return details

    @Item.count.setter
    def count(self, value):
        self._count = Decimal(
            sum(map(mul, map(int, value.split(':')), factors)) / 60)


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

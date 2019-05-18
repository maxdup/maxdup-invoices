from datetime import datetime

from InvoiceGenerator.api import Item

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

        self.commits = []

    def detailed_description(self):
        detailed_description = self._description
        if self.commits:
            detailed_description += '\nCommits:'
            for commit in self.commits:
                if not commit.merge:
                    detailed_description += ('\n' + commit.message)
        return detailed_description

    def add_commit(self, commit):
        self.commits.append(commit)

    @property
    def description(self):
        """ Short description of the item. """
        desc = self.detailed_description()
        return desc

    @Item.count.setter
    def count(self, value):
        self._count = Decimal(
            sum(map(mul, map(int, value.split(':')), factors)) / 60)

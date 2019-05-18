from datetime import datetime

from InvoiceGenerator.api import Item

from operator import mul
from decimal import Decimal
factors = (60, 1, 1/60)


class WorkSession(Item):

    _commits = []

    def __init__(self, row, columns, rate):

        self.count = row[columns.index('Duration')]
        self.price = rate
        self._description = row[columns.index('Title')]
        self.unit = ''
        self.tax = 0

        self.project = row[columns.index('Project')]
        self.client = row[columns.index('Client')]

    def detailed_description(self):
        detailed_description = self._description
        if self._commits:
            detailed_description += '\nCommits:'
            for commit in self._commits:
                detailed_description += ('\n' + commit.message)
        return detailed_description

    def add_commit(commit):
        self._commits.append(commit)

    @property
    def description(self):
        """ Short description of the item. """
        return self.detailed_description()

    @Item.count.setter
    def count(self, value):
        self._count = Decimal(
            sum(map(mul, map(int, value.split(':')), factors)) / 60)

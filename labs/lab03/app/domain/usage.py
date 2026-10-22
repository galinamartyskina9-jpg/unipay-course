from abc import ABC, abstractmethod
from app.support.types import CheckResult, checked, identifier, choice, boolean, date_only, Repository
from app.support.types import name as valid_name, country as valid_country
from app.support.errors import DomainError

class CardUsageRule:
    def check(self, entity, context):
        raise NotImplementedError

class AllowedCardTypeRule(CardUsageRule):
    def __init__(self, values):
        self._values = frozenset(values)
        for value in self._values:
            choice(value, ('STANDARD', 'VIRTUAL'), "INVALID_CONFIG")

    def check(self, entity, context):
        return CheckResult(True)  # ЛР3: перенести проверку

class OnlineUsageRule(CardUsageRule):
    def __init__(self):
        self._channel = "ONLINE"

    def check(self, entity, context):
        return CheckResult(True)  # ЛР3: перенести вторую проверку

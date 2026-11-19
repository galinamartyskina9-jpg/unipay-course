from app.support.types import CheckResult, checked
from abc import ABC, abstractmethod
from app.support.types import CheckResult, checked, identifier, choice, boolean, date_only, Repository
from app.support.types import name as valid_name, country as valid_country
from app.support.errors import DomainError

class CardUsageRule(ABC):
    @abstractmethod
    def check(self, entity, context):
        raise NotImplementedError

class AllowedCardTypeRule(CardUsageRule):
    def __init__(self, values):
        self._values = frozenset(values)
        for value in self._values:
            choice(value, ('STANDARD', 'VIRTUAL'), "INVALID_CONFIG")

    def check(self, entity, context):
        if entity.card_type not in self._values:
            return CheckResult(False, 'CARD_TYPE_DENIED')
        return CheckResult(True)

class OnlineUsageRule(CardUsageRule):
    def __init__(self):
        self._channel = "ONLINE"

    def check(self, entity, context):
        if context.channel == self._channel and not entity.online_enabled:
            return CheckResult(False, 'CARD_ONLINE_DISABLED')
        return CheckResult(True)

class ContactlessUsageRule(CardUsageRule):

    def check(self, entity, context):
        if context.contactless and not entity.contactless_enabled:
            return CheckResult(False, "CONTACTLESS_DISABLED")
        return CheckResult(True)


class UsageRuleGroup(CardUsageRule):
    """Последовательность правил: первый отказ, без изменения входных объектов."""

    def __init__(self, rules):
        rules_tuple = tuple(rules)
        for rule in rules_tuple:
            if not isinstance(rule, CardUsageRule):
                raise DomainError("INVALID_CONFIG")
        self._rules = rules_tuple

    def check(self, entity, context):
        for rule in self._rules:
            result = checked(rule.check(entity, context))
            if not result.allowed:
                return result
        return CheckResult(True)


class ExpiryBufferRule(CardUsageRule):
    def __init__(self, minimum_days):
        if isinstance(minimum_days, bool) or not isinstance(minimum_days, int) or minimum_days < 0:
            raise DomainError("INVALID_CONFIG")
        self._minimum_days = minimum_days

    def check(self, entity, context):
        date_only(context.as_of)
        if (entity.expiration_date - context.as_of).days < self._minimum_days:
            return CheckResult(False, "CARD_EXPIRING_SOON")
        return CheckResult(True)

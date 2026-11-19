import pytest
from datetime import date, datetime, timezone
from decimal import Decimal
from app import api
from app.support.errors import DomainError


def code(expected, operation):
    with pytest.raises(DomainError) as caught:
        operation()
    assert caught.value.code == expected

from app.domain.card import Card
from app.support.types import CardContext

def test_progression_availability_does_not_cache_state():
    service = api.create()
    item = Card("C", "U", "A", date(2030,4,30), "STANDARD")
    item.activate()
    service.register(item)
    first = service.check("C", CardContext(date(2030,4,29)))
    assert first.allowed
    item.block()
    assert service.check("C", CardContext(date(2030,4,29))).code == "CARD_BLOCKED"
    item.unblock()
    assert service.check("C", CardContext(date(2030,4,29))).allowed
    assert first.allowed and item.status == "ACTIVE"

from app.domain.usage import CardUsageRule
from app.support.types import Repository, CheckResult
from app.services.card_service import CardService

def test_progression_dependency_called_once_and_retained():
    calls = []
    class Once(CardUsageRule):
        def check(self, item, ctx):
            calls.append(item)
            if len(calls) == 1: raise DomainError("TEMPORARY")
            return CheckResult(True)
    rules = [Once()]
    repo = Repository("card_id")
    item = Card("C", "U", "A", date(2030,4,30), "STANDARD")
    item.activate()
    repo.add(item)
    service = CardService(repo, rules)
    rules.clear()
    code("TEMPORARY", lambda: service.check("C", CardContext(date(2030,4,29))))
    assert len(calls) == 1 and item.status == "ACTIVE"
    assert service.check("C", CardContext(date(2030,4,29))).allowed and calls == [item, item]

from app.domain.usage import UsageRuleGroup, CardUsageRule
from app.support.types import CheckResult

def test_progression_group_order_snapshot_and_identity():
    calls = []
    class Rule(CardUsageRule):
        def __init__(self, name, allowed=True): self.name, self.allowed = name, allowed
        def check(self, entity, context):
            calls.append(self.name)
            return CheckResult(True) if self.allowed else CheckResult(False, self.name)
    deny = Rule("DENIED", False)
    rules = [Rule("FIRST"), deny, Rule("NEVER")]
    group = UsageRuleGroup(rules)
    rules.clear()
    assert group.check(object(), object()).code == "DENIED"
    assert calls == ["FIRST", "DENIED"]
    calls.clear()
    deny.name = "SAME_INSTANCE"
    assert group.check(object(), object()).code == "SAME_INSTANCE"
    assert calls == ["FIRST", "SAME_INSTANCE"]
    assert UsageRuleGroup([]).check(object(), object()).allowed
    calls.clear()
    nested = UsageRuleGroup([UsageRuleGroup([Rule("A")]), Rule("B")])
    assert nested.check(object(), object()).allowed and calls == ["A", "B"]

def test_progression_group_bad_result_and_error():
    calls = []
    class Bad(CardUsageRule):
        def check(self, entity, context): calls.append("bad"); return None
    code("INVALID_RESULT", lambda: UsageRuleGroup([Bad()]).check(object(), object()))
    assert calls == ["bad"]
    class Broken(CardUsageRule):
        def check(self, entity, context): raise DomainError("RULE_FAILED")
    code("RULE_FAILED", lambda: UsageRuleGroup([Broken()]).check(object(), object()))
    code("INVALID_CONFIG", lambda: UsageRuleGroup([object()]))


def test_progression_default_assembly_uses_group(monkeypatch):
    calls = []
    def check(self, *args):
        calls.append(args)
        return CheckResult(False, "GROUP_USED")
    monkeypatch.setattr(UsageRuleGroup, "check", check)
    service = api.create()
    item = Card("C", "U", "A", date(2030,4,30), "STANDARD")
    item.activate()
    service.register(item)
    assert service.check("C", CardContext(date(2030,4,29))).code == "GROUP_USED"
    assert len(calls) == 1

from app.domain.usage import ExpiryBufferRule
from app.domain.card import Card
from app.support.types import CardContext

def test_progression_extra_lab06():
    card = Card("CARD", "C", "ACC", date(2030, 4, 30), "STANDARD")
    card.activate()
    rule = ExpiryBufferRule(3)
    assert rule.check(card, CardContext(date(2030, 4, 26))).allowed
    assert rule.check(card, CardContext(date(2030, 4, 28))).code == "CARD_EXPIRING_SOON"
    code("INVALID_CONFIG", lambda: ExpiryBufferRule(True))

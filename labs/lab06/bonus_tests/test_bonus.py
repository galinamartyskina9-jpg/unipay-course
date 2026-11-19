import pytest
from decimal import Decimal
from datetime import date, datetime, timezone, timedelta
from app import api
from app.support.errors import DomainError
from app.support.types import Repository, CheckResult, Money, money


def error(code, operation):
    with pytest.raises(DomainError) as caught:
        operation()
    assert caught.value.code == code


def invoke(service, method, *args, **kwargs):
    return api.call(service, method, *args, **kwargs)

def test_contactless_change_respects_state():
    item = api.make('CARD-1', "C1", "ACC-1", date(2030, 4, 30), "STANDARD")
    error("INVALID_STATE",lambda:item.set_contactless_enabled(False))
    item.activate()
    item.set_contactless_enabled(False)
    assert item.contactless_enabled is False

from app.services.card_service import CardService
from app.support.types import Repository
from app.domain.usage import AllowedCardTypeRule, OnlineUsageRule, ContactlessUsageRule, UsageRuleGroup

def build_service(repository=None, rules=None):
    repository = repository if repository is not None else Repository("card_id")
    if rules is None:
        rules = [UsageRuleGroup((AllowedCardTypeRule({"STANDARD"}), OnlineUsageRule(), ContactlessUsageRule()))]
    return CardService(repository, rules)

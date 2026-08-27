from datetime import datetime

from app.models.mixins import CommonMixin


def process_investments(
    target: CommonMixin, sources: list[CommonMixin]
) -> list[CommonMixin]:
    changed_sources = []
    for source in sources:
        if target.fully_invested:
            break
        investment = min(
            target.full_amount - target.invested_amount,
            source.full_amount - source.invested_amount,
        )
        for obj in (target, source):
            obj.invested_amount += investment
            if obj.invested_amount == obj.full_amount:
                obj.fully_invested = True
                obj.close_date = datetime.now()
        changed_sources.append(source)
    return changed_sources

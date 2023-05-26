import random
from _decimal import Decimal
from datetime import date

import pytest
from django.db import IntegrityError

from currency.models import CurrencyValue, CurrencyDate, CurrencyName


def test_add_one_currency_data(currency):
    currency_value = CurrencyValue.objects.filter(currency_date=currency).first()

    assert currency_value.currency_name.code == "USD"
    assert currency_value.currency_name.name == "dolar amerykański"
    assert currency_value.currency_date.date == currency.date


def test_get_values_by_date_range(currency, currency_2):
    dates = CurrencyDate.objects.filter(date__range=(date(2023, 5, 20), date(2023, 5, 23)))
    values = dates.filter(currency_values__currency_name__code="USD")

    assert len(values) == 2
    assert values.first().currency_values.first().exchange_rate == Decimal("0.20")


def test_add_two_values_for_date_for_one_currency(currency_date, currency_name):
    CurrencyValue.objects.create(
        exchange_rate=Decimal("1.00"), currency_name=currency_name, currency_date=currency_date
    )

    with pytest.raises(IntegrityError) as excinfo:
        CurrencyValue.objects.create(
            exchange_rate=Decimal("2.00"), currency_name=currency_name, currency_date=currency_date
        )

    assert "UNIQUE constraint failed" in str(excinfo)


def test_add_multiple_exchange_rate_at_once(currency_date):
    currency_names = CurrencyName.objects.all()
    currency_names_count = currency_names.count()
    values = [Decimal(round(random.uniform(0.1, 2), 4)) * 20 for _ in range(currency_names_count)]
    currency_values = [
        CurrencyValue(exchange_rate=value, currency_name=currency_names[index], currency_date=currency_date)
        for index, value in enumerate(values)
    ]
    CurrencyValue.objects.bulk_create(currency_values)

    currency_values_db = CurrencyValue.objects.all().count()

    assert currency_values_db == currency_names_count
    assert CurrencyDate.objects.get(date=currency_date.date).currency_values.count() == currency_names_count
    assert currency_names.first().currency_values.filter(currency_date=currency_date).count() == 1

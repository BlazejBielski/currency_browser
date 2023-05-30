import json
from datetime import datetime, timedelta

from django.views.generic import FormView
from urllib import request

from . import forms, models


def get_holidays(start_date, end_date):
    url = f"https://openholidaysapi.org/PublicHolidays?countryIsoCode=PL&languageIsoCode=PL&validFrom={start_date}&validTo={end_date}"
    with request.urlopen(url) as response:
        data = json.loads(response.read().decode())

    return [holiday["startDate"] for holiday in data]


def count_holidays_during_weekdays(start_date, end_date):
    holidays = get_holidays(start_date, end_date)

    count_weekday_holidays = 0

    for holiday in holidays:
        if datetime.strptime(holiday, "%Y-%m-%d").weekday() < 5:
            count_weekday_holidays += 1

    return count_weekday_holidays


def count_days_off(start_date, end_date):
    days_count = 0

    while start_date <= end_date:
        if start_date.weekday() >= 5:
            days_count += 1

        start_date += timedelta(days=1)

    return days_count


def count_days(start_date, end_date):
    return (end_date - start_date).days


def get_currency_data_from_nbp_api(start_date, end_date):
    currency_nbp_url = f"http://api.nbp.pl/api/exchangerates/tables/a/{start_date}/{end_date}/"

    with request.urlopen(currency_nbp_url) as response:
        data = json.loads(response.read().decode())

    currency_names = models.CurrencyName.objects.all()

    for day in data:
        if not models.CurrencyDate.objects.filter(date=datetime.strptime(day["effectiveDate"], "%Y-%m-%d")):
            currency_date = models.CurrencyDate.objects.create(data=datetime.strptime(day["effectiveDate"], "%Y-%m-%d"))

            currency_values = [
                models.CurrencyValue(
                    exchange_rate=rate["mid"],
                    currency_date=currency_date,
                    currency_name=currency_names.get(code=rate["code"]),
                )
                for rate in day["rates"]
            ]

            models.CurrencyValue.objects.bulk_create(currency_values)


class CurrencyView(FormView):
    form_class = forms.CurrencyForm
    template_name = "currency/currency_view.html"
    success_url = "/"

    def form_valid(self, form):
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        currencies = form.cleaned_data.get("currency")

        dates = models.CurrencyDate.objects.filter(date__range=(start_date, end_date)).count()

        if dates.count() < count_days(start_date, end_date) - count_holidays_during_weekdays(
            start_date, end_date
        ) - count_days_off(start_date, end_date):
            get_currency_data_from_nbp_api(start_date, end_date)

        context = self.get_context_data()
        context.update({"dates": dates})

        return super().form_valid(form)

    def get_form(self, form_class=None):
        currencies = models.CurrencyName.objects.all()
        form = super().get_form(form_class)

        form.fields["currency"].choices = [(currency.code, currency.name.title()) for currency in currencies]

        return form

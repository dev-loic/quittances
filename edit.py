from datetime import date
from calendar import monthrange

## INFORMATION
TODAY = date.today()
MONTHLY_TOTAL = 110.00
RENTAL_CHARGE = 7.12
MONTHLY_FEE = MONTHLY_TOTAL - RENTAL_CHARGE

def format_period():
    current_month_nb_of_days = monthrange(TODAY.year, TODAY.month)
    first_day = "1er {}".format(TODAY.strftime("%B %Y"))
    last_day = "{} {}".format(current_month_nb_of_days[1], TODAY.strftime("%B %Y"))
    return "{} au {}".format(first_day, last_day)

## FIELDS
# Here we have to match keys from GoogleDoc and replacing values
_edit_fields = [
    { 'key': '{{period}}', 'value': format_period() },
    { 'key': '{{monthly-fee}}', 'value': str(MONTHLY_FEE) },
    { 'key': '{{rental-charge}}', 'value': str(RENTAL_CHARGE) },
    { 'key': '{{monthly-total}}', 'value': str(MONTHLY_TOTAL) },
    { 'key': '{{today-date}}', 'value': TODAY.strftime('%d/%m/%y') }
]

def get_requests():
    requests = []
    for field in _edit_fields:
        request = {
            'replaceAllText': {
                'containsText': {
                    'text': field['key'],
                    'matchCase':  'true'
                },
                'replaceText': field['value']
            }
        }
        requests.append(request)
    return requests

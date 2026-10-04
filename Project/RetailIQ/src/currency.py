"""
RetailIQ - Currency Module

Maps a country to a display currency (symbol, code, and an approximate
fixed exchange rate from GBP). This is NOT live FX data - it is a fixed,
indicative rate meant for presentation only, so a dashboard filtered to
"Germany" shows amounts in EUR instead of always showing GBP.

Base currency: GBP (rate = 1.0), matching the original UCI Online Retail
dataset's currency. Numeric values in any loaded dataset are treated as
being in this base currency before conversion.
"""

# (currency_code, symbol, approx_rate_from_GBP) - indicative only.
COUNTRY_CURRENCY = {
    "United Kingdom": ("GBP", "£", 1.0),
    "United States": ("USD", "$", 1.27),
    "Germany": ("EUR", "€", 1.17),
    "France": ("EUR", "€", 1.17),
    "Spain": ("EUR", "€", 1.17),
    "Italy": ("EUR", "€", 1.17),
    "Netherlands": ("EUR", "€", 1.17),
    "Ireland": ("EUR", "€", 1.17),
    "Portugal": ("EUR", "€", 1.17),
    "Belgium": ("EUR", "€", 1.17),
    "Canada": ("CAD", "C$", 1.71),
    "Australia": ("AUD", "A$", 1.90),
    "India": ("INR", "₹", 105.0),
    "United Arab Emirates": ("AED", "AED ", 4.65),
    "Brazil": ("BRL", "R$", 6.30),
    "Japan": ("JPY", "¥", 190.0),
    "Sweden": ("SEK", "kr", 13.3),
    "Mexico": ("MXN", "$", 21.5),
    "Switzerland": ("CHF", "CHF ", 1.12),
    "Singapore": ("SGD", "S$", 1.68),
    "China": ("CNY", "¥", 9.10),
    "Saudi Arabia": ("SAR", "SAR ", 4.75),
}

BASE_CURRENCY = ("GBP", "£", 1.0)


def get_currency_for_countries(selected_countries):
    """
    Decide which currency to display given the current country filter.

    - Exactly one country selected and it's in the mapping -> that currency.
    - Zero or multiple countries selected (or an unmapped country) -> base (GBP).

    Returns (currency_code, symbol, rate_from_gbp).
    """
    if selected_countries and len(selected_countries) == 1:
        country = selected_countries[0]
        if country in COUNTRY_CURRENCY:
            return COUNTRY_CURRENCY[country]
    return BASE_CURRENCY

"""
Börsenplätze und Währungen.

Bei Yahoo Finance verrät die Endung des Kürzels den Handelsplatz:
SAP.DE = Xetra (Euro), 7203.T = Tokio (Yen), AAPL ohne Endung = USA (Dollar).
Daraus leiten wir Markt und Währung ab – nötig für Liquiditätsfilter,
Klumpenrisiko-Grenzen und später die Positionsgröße in Euro.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Market:
    code: str          # Kurzname für Berichte
    name: str
    currency: str      # ISO-Code der Notierungswährung
    price_divisor: float = 1.0   # London notiert in Pence (GBp) -> /100 für Pfund


US = Market("US", "USA", "USD")
CRYPTO = Market("CRYPTO", "Krypto", "USD")

SUFFIX_MARKETS: dict[str, Market] = {
    "DE": Market("DE", "Deutschland (Xetra)", "EUR"),
    "F": Market("DE", "Deutschland (Frankfurt)", "EUR"),
    "PA": Market("FR", "Frankreich", "EUR"),
    "AS": Market("NL", "Niederlande", "EUR"),
    "BR": Market("BE", "Belgien", "EUR"),
    "MI": Market("IT", "Italien", "EUR"),
    "MC": Market("ES", "Spanien", "EUR"),
    "HE": Market("FI", "Finnland", "EUR"),
    "LS": Market("PT", "Portugal", "EUR"),
    "IR": Market("IE", "Irland", "EUR"),
    "VI": Market("AT", "Österreich", "EUR"),
    "SW": Market("CH", "Schweiz", "CHF"),
    "L": Market("UK", "Großbritannien", "GBP", price_divisor=100.0),
    "ST": Market("SE", "Schweden", "SEK"),
    "CO": Market("DK", "Dänemark", "DKK"),
    "OL": Market("NO", "Norwegen", "NOK"),
    "T": Market("JP", "Japan", "JPY"),
    "HK": Market("HK", "Hongkong", "HKD"),
    "AX": Market("AU", "Australien", "AUD"),
    "TO": Market("CA", "Kanada", "CAD"),
    "NS": Market("IN", "Indien", "INR"),
    "KS": Market("KR", "Südkorea", "KRW"),
    "TW": Market("TW", "Taiwan", "TWD"),
    "SA": Market("BR", "Brasilien", "BRL"),
    "SI": Market("SG", "Singapur", "SGD"),
    "MX": Market("MX", "Mexiko", "MXN"),
}

CRYPTO_QUOTES = ("-USD", "-EUR", "-USDT", "-BTC")


def market_of(symbol: str) -> Market:
    s = symbol.upper()
    if s.endswith(CRYPTO_QUOTES):
        return CRYPTO
    if "." in s:
        suffix = s.rsplit(".", 1)[1]
        if suffix in SUFFIX_MARKETS:
            return SUFFIX_MARKETS[suffix]
    return US


def currency_of(symbol: str) -> str:
    return market_of(symbol).currency


def asset_class(symbol: str) -> str:
    """'crypto' oder 'stock' (Aktien und ETFs werden gleich behandelt)."""
    return "crypto" if market_of(symbol) is CRYPTO else "stock"


def fx_symbol(currency: str) -> str | None:
    """Yahoo-Kürzel für den Kurs '1 Einheit Währung in USD'."""
    return None if currency == "USD" else f"{currency}USD=X"

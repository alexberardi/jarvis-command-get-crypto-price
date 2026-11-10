from typing import Any

import requests

from jarvis_command_sdk import (
    CommandExample,
    CommandResponse,
    IJarvisCommand,
    JarvisPackage,
    JarvisParameter,
    RequestInformation,
)

try:
    from jarvis_log_client import JarvisLogger
except ImportError:
    import logging

    class JarvisLogger:
        def __init__(self, **kw):
            self._log = logging.getLogger(kw.get('service', __name__))

        def info(self, msg, **kw):
            self._log.info(msg)

        def warning(self, msg, **kw):
            self._log.warning(msg)

        def error(self, msg, **kw):
            self._log.error(msg)

        def debug(self, msg, **kw):
            self._log.debug(msg)


logger = JarvisLogger(service='get_crypto_price')

BASE_URL = 'https://api.coingecko.com/api/v3'
REQUEST_TIMEOUT = 8
HEADERS = {'Accept': 'application/json', 'User-Agent': 'jarvis-get-crypto-price/0.1'}

# Common names / tickers -> CoinGecko coin id
COIN_ALIASES = {
    'btc': 'bitcoin',
    'bitcoin': 'bitcoin',
    'eth': 'ethereum',
    'ethereum': 'ethereum',
    'ether': 'ethereum',
    'sol': 'solana',
    'solana': 'solana',
    'doge': 'dogecoin',
    'dogecoin': 'dogecoin',
    'xrp': 'ripple',
    'ripple': 'ripple',
    'ada': 'cardano',
    'cardano': 'cardano',
    'ltc': 'litecoin',
    'litecoin': 'litecoin',
    'bnb': 'binancecoin',
    'binance coin': 'binancecoin',
    'dot': 'polkadot',
    'polkadot': 'polkadot',
    'usdt': 'tether',
    'tether': 'tether',
    'shib': 'shiba-inu',
    'shiba inu': 'shiba-inu',
    'shiba': 'shiba-inu',
    'avax': 'avalanche-2',
    'avalanche': 'avalanche-2',
    'link': 'chainlink',
    'chainlink': 'chainlink',
    'xmr': 'monero',
    'monero': 'monero',
    'xlm': 'stellar',
    'stellar': 'stellar',
    'trx': 'tron',
    'tron': 'tron',
    'bch': 'bitcoin-cash',
    'bitcoin cash': 'bitcoin-cash',
}

COIN_DISPLAY_NAMES = {
    'bitcoin': 'Bitcoin',
    'ethereum': 'Ethereum',
    'solana': 'Solana',
    'dogecoin': 'Dogecoin',
    'ripple': 'XRP',
    'cardano': 'Cardano',
    'litecoin': 'Litecoin',
    'binancecoin': 'BNB',
    'polkadot': 'Polkadot',
    'tether': 'Tether',
    'shiba-inu': 'Shiba Inu',
    'avalanche-2': 'Avalanche',
    'chainlink': 'Chainlink',
    'monero': 'Monero',
    'stellar': 'Stellar',
    'tron': 'TRON',
    'bitcoin-cash': 'Bitcoin Cash',
}

# Spoken currency words -> ISO code
CURRENCY_ALIASES = {
    'dollar': 'usd',
    'dollars': 'usd',
    'us dollar': 'usd',
    'us dollars': 'usd',
    'bucks': 'usd',
    'euro': 'eur',
    'euros': 'eur',
    'pound': 'gbp',
    'pounds': 'gbp',
    'sterling': 'gbp',
    'british pounds': 'gbp',
    'yen': 'jpy',
    'japanese yen': 'jpy',
    'canadian dollars': 'cad',
    'canadian dollar': 'cad',
    'australian dollars': 'aud',
    'australian dollar': 'aud',
    'franc': 'chf',
    'francs': 'chf',
    'swiss francs': 'chf',
    'rupee': 'inr',
    'rupees': 'inr',
    'peso': 'mxn',
    'pesos': 'mxn',
    'yuan': 'cny',
    'renminbi': 'cny',
    'won': 'krw',
    'real': 'brl',
    'reais': 'brl',
}

CURRENCY_SPOKEN = {
    'usd': 'dollars',
    'eur': 'euros',
    'gbp': 'pounds',
    'jpy': 'yen',
    'cad': 'Canadian dollars',
    'aud': 'Australian dollars',
    'chf': 'Swiss francs',
    'inr': 'rupees',
    'mxn': 'pesos',
    'cny': 'yuan',
    'krw': 'won',
    'brl': 'reais',
}

FILLER_WORDS = {'the', 'coin', 'crypto', 'cryptocurrency', 'price', 'of', 'token', 'a'}


def _clean(text: str) -> str:
    lowered = str(text).lower().strip()
    return ''.join(ch for ch in lowered if ch.isalnum() or ch in ' -').strip()


def _normalize_coin(text: str) -> str:
    words = [w for w in _clean(text).split() if w not in FILLER_WORDS]
    return ' '.join(words)


def _normalize_currency(text: Any) -> str | None:
    if not text:
        return 'usd'
    cleaned = _clean(text)
    if not cleaned:
        return 'usd'
    if cleaned in CURRENCY_ALIASES:
        return CURRENCY_ALIASES[cleaned]
    compact = cleaned.replace(' ', '')
    if len(compact) == 3 and compact.isalpha():
        return compact
    return None


def _format_amount(value: float) -> str:
    if value >= 1000:
        return f'{value:,.0f}'
    if value >= 1:
        return f'{value:,.2f}'
    if value >= 0.01:
        return f'{value:.4f}'
    return f'{value:.6f}'


class GetCryptoPriceCommand(IJarvisCommand):
    '''Look up the current price of a cryptocurrency via CoinGecko.'''

    @property
    def command_name(self) -> str:
        return 'get_crypto_price'

    @property
    def description(self) -> str:
        return (
            'Get the current price of a cryptocurrency (Bitcoin, Ethereum, Solana, etc.) '
            'in USD or another currency, using CoinGecko.'
        )

    @property
    def keywords(self) -> list[str]:
        return [
            'crypto',
            'cryptocurrency',
            'bitcoin',
            'ethereum',
            'coin',
            'price',
            'btc',
            'eth',
            'coingecko',
        ]

    @property
    def parameters(self) -> list[JarvisParameter]:
        return [
            JarvisParameter(
                name='coin',
                param_type='string',
                required=True,
                description=(
                    'Name or ticker of the cryptocurrency, e.g. Bitcoin, Ethereum, BTC, Solana'
                ),
            ),
            JarvisParameter(
                name='currency',
                param_type='string',
                required=False,
                description=(
                    'Currency to quote the price in, e.g. USD, euros, pounds. '
                    'Defaults to USD if not mentioned.'
                ),
                default='usd',
            ),
        ]

    @property
    def required_secrets(self) -> list:
        return []

    @property
    def required_packages(self) -> list[JarvisPackage]:
        return [JarvisPackage('requests', '>=2.28.0')]

    def generate_prompt_examples(self) -> list[CommandExample]:
        return [
            CommandExample(
                voice_command="What's Bitcoin at?",
                expected_parameters={'coin': 'bitcoin', 'currency': 'usd'},
                is_primary=True,
            ),
            CommandExample(
                voice_command='Price of Ethereum in euros',
                expected_parameters={'coin': 'ethereum', 'currency': 'eur'},
            ),
            CommandExample(
                voice_command='How much is Solana right now?',
                expected_parameters={'coin': 'solana', 'currency': 'usd'},
            ),
            CommandExample(
                voice_command='Dogecoin price in pounds',
                expected_parameters={'coin': 'dogecoin', 'currency': 'gbp'},
            ),
        ]

    def generate_adapter_examples(self) -> list[CommandExample]:
        items = [
            ("What's Bitcoin at?", 'bitcoin', 'usd'),
            ('Price of Ethereum in euros', 'ethereum', 'eur'),
            ('How much is Solana right now?', 'solana', 'usd'),
            ('Dogecoin price in pounds', 'dogecoin', 'gbp'),
            ('What is BTC trading at?', 'BTC', 'usd'),
            ('Check the price of ETH', 'ETH', 'usd'),
            ('How much is one Bitcoin in yen?', 'bitcoin', 'jpy'),
            ("What's Litecoin worth?", 'litecoin', 'usd'),
            ('Cardano price in Canadian dollars', 'cardano', 'cad'),
            ('Tell me the XRP price', 'XRP', 'usd'),
            ('Bitcoin price in euros', 'bitcoin', 'eur'),
            ('How is Dogecoin doing?', 'dogecoin', 'usd'),
            ("What's the crypto price of Chainlink?", 'chainlink', 'usd'),
            ('Price of Monero in pounds', 'monero', 'gbp'),
            ("What's Shiba Inu at right now?", 'shiba inu', 'usd'),
            ('Avalanche price in Swiss francs', 'avalanche', 'chf'),
        ]
        examples = []
        for i, (voice, coin, currency) in enumerate(items):
            examples.append(
                CommandExample(
                    voice_command=voice,
                    expected_parameters={'coin': coin, 'currency': currency},
                    is_primary=(i == 0),
                )
            )
        return examples

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve_coin(self, query: str) -> tuple[str, str] | None:
        '''Return (coin_id, display_name) or None if the coin can't be found.'''
        if query in COIN_ALIASES:
            coin_id = COIN_ALIASES[query]
            return coin_id, COIN_DISPLAY_NAMES.get(coin_id, query.title())

        resp = requests.get(
            f'{BASE_URL}/search',
            params={'query': query},
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code == 429:
            raise RuntimeError('rate_limited')
        resp.raise_for_status()
        coins = resp.json().get('coins') or []
        if not coins:
            return None

        for coin in coins:
            if query in (
                str(coin.get('id', '')).lower(),
                str(coin.get('symbol', '')).lower(),
                str(coin.get('name', '')).lower(),
            ):
                return coin['id'], coin.get('name') or query.title()

        top = coins[0]
        return top['id'], top.get('name') or query.title()

    def _fetch_price(self, coin_id: str, currency: str) -> tuple[float | None, float | None, bool]:
        '''Return (price, change_24h, coin_found).'''
        resp = requests.get(
            f'{BASE_URL}/simple/price',
            params={
                'ids': coin_id,
                'vs_currencies': currency,
                'include_24hr_change': 'true',
            },
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code == 429:
            raise RuntimeError('rate_limited')
        resp.raise_for_status()
        data = resp.json() or {}
        coin_data = data.get(coin_id)
        if not coin_data:
            return None, None, False
        price = coin_data.get(currency)
        change = coin_data.get(f'{currency}_24h_change')
        return price, change, True

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self, request_info: RequestInformation, **kwargs: Any) -> CommandResponse:
        try:
            raw_coin = kwargs.get('coin')
            query = _normalize_coin(raw_coin) if raw_coin else ''
            if not query:
                return CommandResponse.success_response(
                    context_data={'message': 'Which cryptocurrency do you want the price of?'}
                )

            currency = _normalize_currency(kwargs.get('currency'))
            if currency is None:
                return CommandResponse.error_response(
                    error_details='unsupported currency',
                    context_data={
                        'message': "Sorry, I don't recognize that currency."
                    },
                )

            resolved = self._resolve_coin(query)
            if resolved is None:
                return CommandResponse.error_response(
                    error_details=f'coin not found: {query}',
                    context_data={
                        'message': f"Sorry, I couldn't find a coin called {query}."
                    },
                )
            coin_id, display_name = resolved

            price, change, found = self._fetch_price(coin_id, currency)
            if not found:
                return CommandResponse.error_response(
                    error_details=f'no price data for {coin_id}',
                    context_data={
                        'message': f"Sorry, I couldn't find a price for {display_name}."
                    },
                )
            if price is None:
                return CommandResponse.error_response(
                    error_details=f'currency {currency} not supported',
                    context_data={
                        'message': (
                            f"Sorry, I can't quote {display_name} in {currency.upper()}."
                        )
                    },
                )

            spoken_currency = CURRENCY_SPOKEN.get(currency, currency.upper())
            message = f'{display_name} is at {_format_amount(float(price))} {spoken_currency}'
            if isinstance(change, (int, float)):
                direction = 'up' if change >= 0 else 'down'
                message += f', {direction} {abs(change):.1f} percent today'
            message += '.'

            return CommandResponse.final_response(
                context_data={
                    'message': message,
                    'coin': display_name,
                    'coin_id': coin_id,
                    'currency': currency,
                    'price': price,
                    'change_24h_percent': change,
                }
            )

        except RuntimeError as e:
            if str(e) == 'rate_limited':
                logger.warning('CoinGecko rate limit hit')
                return CommandResponse.error_response(
                    error_details='rate limited',
                    context_data={
                        'message': 'The price service is busy right now. Try again in a minute.'
                    },
                )
            logger.error(f'Unexpected runtime error: {e}')
            return CommandResponse.error_response(
                error_details=str(e),
                context_data={'message': "Sorry, I couldn't get that price."},
            )
        except requests.exceptions.RequestException as e:
            logger.error(f'CoinGecko request failed: {e}')
            return CommandResponse.error_response(
                error_details=str(e),
                context_data={
                    'message': "Sorry, I couldn't reach the price service right now."
                },
            )
        except Exception as e:  # noqa: BLE001
            logger.error(f'Unexpected error in get_crypto_price: {e}')
            return CommandResponse.error_response(
                error_details=str(e),
                context_data={'message': "Sorry, I couldn't get that price."},
            )

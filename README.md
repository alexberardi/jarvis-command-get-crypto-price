# Crypto Price

A Jarvis voice command that tells you the current price of a cryptocurrency using [CoinGecko's](https://www.coingecko.com/) free public API. No API key or account is required.

## Setup

No setup is needed.

- **Secrets:** none
- **API keys:** none (uses CoinGecko's free public endpoints)
- **Dependencies:** `requests` (installed automatically)

The free CoinGecko API is rate limited. If you ask for prices very frequently, Jarvis will tell you the service is busy and to try again shortly.

## Usage

Example voice commands:

- "What's Bitcoin at?"
- "Price of Ethereum in euros"
- "How much is Solana right now?"
- "Dogecoin price in pounds"
- "What is BTC trading at?"
- "How much is one Bitcoin in yen?"

Example responses (kept short for speech):

- "Bitcoin is at 67,250 dollars, up 2.1 percent today."
- "Ethereum is at 3,100 euros, down 0.8 percent today."

## Parameters

| Parameter  | Type   | Required | Description                                                        |
|------------|--------|----------|--------------------------------------------------------------------|
| `coin`     | string | yes      | Coin name or ticker (Bitcoin, ETH, Solana, ...)                    |
| `currency` | string | no       | Currency name or code (euros, GBP, yen, ...). Defaults to USD.     |

## Supported Actions

- Look up the current price of a coin, with the 24-hour change.
- Quote prices in any currency supported by CoinGecko (USD, EUR, GBP, JPY, CAD, AUD, CHF, INR, and more). Spoken names like "euros" or "pounds" are understood.
- Resolve common coins and tickers instantly (BTC, ETH, SOL, DOGE, XRP, ADA, and others). Less common coins are found through CoinGecko search.

## Error Handling

- Unknown coin: "Sorry, I couldn't find a coin called ..."
- Unsupported currency: "Sorry, I can't quote Bitcoin in ..."
- Rate limit or network problems: a short spoken message, with no crash.

## License

MIT

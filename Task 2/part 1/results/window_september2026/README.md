# Trial: activity in September 2026

UTC window: inclusive 2026-09-01 00:00 to exclusive 2026-10-01 00:00.
Actual collection on 5 October 2026 using collect_window.py, max-pages=1 (at most 25 transactions per address). The manifest and input.csv fix the settings and sources. JSON files preserve observations and the provenance of each request.

Result: 11 addresses, 0 collection errors, 3 addresses with metrics based on histories with consistent counts, and 8 addresses whose coverage remains unverified.

| Entity | Address | Published label | Coverage | Observed September transactions | Complete count available |
| --- | --- | --- | --- | --- | --- |
| BTC-e.com | `16SbwNa22nBwhLtg6HzWVYFQiUxtNzAUpt` | unknown | unverified | 0 | unavailable |
| Bitfinex | `1Kr6QSydW9bFQG1mXiPNNu6WpJGmUa9i1g` | hot | unverified | 0 | unavailable |
| Binance | `34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo` | unknown | unverified | 6 | unavailable |
| Bitfinex | `3JZq4atUahhuA9rLhXLMhhTo133J9rF97j` | cold | unverified | 18 | unavailable |
| Binance | `3LYJfcfHPXYJreMsASk2jkn69LWEYKzexb` | unknown | unverified | 0 | unavailable |
| Binance | `3M219KR5vEneNb47ewrPfWyb5jQ2DjxRP6` | unknown | unverified | 10 | unavailable |
| Change | `bc1q43krjn8qvfydqs9lq8crg26er4c26hkpd2mpw7` | cold | count_consistent_full_history | 0 | 0 |
| Change | `bc1q9rqfux88j6az0wl957u2jdykgw5m5r72hcaclu` | cold | count_consistent_full_history | 0 | 0 |
| Bitfinex | `bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97` | cold | unverified | 0 | unavailable |
| Change | `bc1qhsuvec03zslh9qvauksh2wc9hy9za7csxem5ea` | cold | count_consistent_full_history | 0 | 0 |
| Binance | `bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h` | unknown | unverified | 0 | unavailable |

An observed value is not a complete count when coverage is unverified. In particular, zero observations in a truncated history do not establish inactivity. Provider count consistency does not guarantee an atomic snapshot or protection against reorgs.

Storage labels are not validated for September 2026. These results therefore do not constitute a validated hot/cold comparison, and no storage prediction was added. Change addresses are documented as cold only at 31 March 2025; a later result does not extend that evidence.

The next necessary improvement is targeted window collection with block-based coverage checks, rather than requiring the entire history. Simply increasing the cap does not guarantee coverage of highly active addresses. Missing complete statistics remain null in JSON files.

# AI Agent Kit for Shops 🤖🛍️

> A customer-support agent kit for a small shop. It answers customers on WhatsApp or a website: prices, stock, delivery, timings, payments — and it takes orders. It works fully offline with no API key, and it can use NVIDIA NIM for smarter replies when a key is available.

## Who is this for?

- A small shop owner (bakery, boutique, beauty salon, electronics shop, or home-based seller) who wants a support agent that answers customers even at night.
- A developer who wants to add a customer-support agent to a shop website or a WhatsApp flow, without paying for a chatbot platform.
- A student who wants to learn how a real support agent works — rules first, AI second.

You do not need to know how to code to run it. You only edit one file — `shop.json` — to make it your shop.

## How it works

```
Customer message
      |
      v
  ShopAgent (agent.py)
      |
      +-- AI backend (nim_backend.py) -- NVIDIA NIM, only when a key is set
      |       |
      |       +-- fails or no key --> falls back, and says so
      |
      +-- Rules engine (rules.py) -- keyword + intent matching, fully offline
      |
      v
  Reply from YOUR shop data (shop.json) — never invented
```

The agent has one strict rule: **it never invents an answer.** A question it cannot answer from your shop data gets a polite reply that connects the customer to the shop owner.

## Quick start

```bash
python3 chat.py
```

Type customer messages and watch the agent reply. Type `quit` to stop.

Replay a fixed demo conversation:

```bash
python3 chat.py --script
```

Run the tests:

```bash
python3 tests.py
```

## Make it your shop

Edit `shop.json` — nothing else:

- `shop_name`, `city`, `contact`, `timings`
- `products`: name, price (PKR), category, `in_stock` (true/false), description
- `delivery`: cities and charges, free-delivery limit, delivery time
- `payment_methods`: for example Cash on Delivery, JazzCash

The demo shop is a bakery in Lahore with 8 products. **All prices in `shop.json` are demo prices, made up for learning. Replace them with your real prices before using this for a real shop.** The contact in the file is a fake placeholder (`0300-XXXXXXX`) — put your real number in only when you deploy it yourself.

## What the agent can do

- **Prices** — "What is the price of chocolate cake?" → the real price from your data.
- **Stock** — "Is mango jam in stock?" → in stock, or politely out of stock.
- **Delivery** — "How much is delivery to Lahore?" → the charge for that city; unknown city → the full list.
- **Timings** — opening hours, Friday break included.
- **Payments** — COD, JazzCash, or whatever you list in `shop.json`.
- **Orders** — step by step: product → quantity → name → city → order summary with the total and delivery charges. Type `cancel` any time to stop.
- **Unknown questions** — "Do you sell cars?" → it says it will connect you to the shop owner. It never guesses.

## Optional: smarter replies with NVIDIA NIM

The kit works fully offline without any key. If you want free-text AI replies as well:

1. Create a free account at https://build.nvidia.com and generate a key at Settings → API Keys.
2. Set it as an environment variable (never put it in a file):
   ```bash
   export NVIDIA_API_KEY=nvapi-xxxx
   ```
3. Run the demo with the AI backend on:
   ```bash
   python3 chat.py --ai
   ```

The AI gets your shop data as context and is told to answer only from it. If the key is missing, or an AI call fails, the agent falls back to the offline rules engine and tells the customer so.

Notes on the free key: it is for prototyping, development and testing only, and it is rate-limited. Production use serving real customers needs an NVIDIA AI Enterprise licence. This kit never sends your key anywhere except NVIDIA's API, and it never stores it.

## Files

| File | What it does |
| --- | --- |
| `agent.py` | The core agent: loads the shop, runs the order flow, picks AI or rules, never invents answers |
| `rules.py` | The offline brain: intent and product matching with keywords |
| `nim_backend.py` | Optional NVIDIA NIM backend, key only from the `NVIDIA_API_KEY` environment variable |
| `chat.py` | CLI demo: live chat, or `--script` to replay `demo_conversation.txt` |
| `demo_conversation.txt` | A fixed demo conversation for `--script` mode |
| `shop.json` | Demo shop data (bakery, Lahore) — edit this to make it your shop |
| `tests.py` | 15 scripted tests, all offline, all must pass |

## Honest limits

- The offline brain matches keywords, it does not truly understand language. A strangely worded question falls back to the shop owner — that is by design, not a bug.
- Orders are only summaries in the chat. There is no payment, no database, and no WhatsApp connection built in. Connecting it to WhatsApp Business or a website chat widget is the next step, not part of this kit.
- The AI backend needs a working NVIDIA key and internet. Your NVIDIA account must be verified, or the API returns a 401 even with a valid-looking key.
- Prices, stock, and delivery details are only as correct as your `shop.json`. Keep that file up to date.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## About

Built by **M. Faisal Fiaz — Faisal Digital Hub**, Lahore, Pakistan. Faisal Digital Hub builds websites, online stores, and AI customer-support agents for small businesses — `BUILD . AUTOMATE . GROW`.

- Portfolio: https://faisal-digital-hub-portfolio.vercel.app
- Instagram: https://www.instagram.com/faisaldigitalhub7
- GitHub: https://github.com/faisaldigitalhub

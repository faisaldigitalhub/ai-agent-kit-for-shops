"""Tests for the AI Agent Kit for Shops.

Run:  python3 tests.py

Every case checks that the agent's reply contains an expected piece of
text. Each case prints PASS or FAIL, then a summary. The process exits
with code 0 only when every case passes. All tests run offline: they use
the rules engine, never the AI backend, so no API key is needed.
"""

from agent import ShopAgent


def check(name, agent, messages, expected):
    """Feed messages in order, check the last reply contains expected."""
    reply = ""
    for message in messages:
        reply = agent.respond(message)
    ok = expected.lower() in reply.lower()
    print(("PASS" if ok else "FAIL") + "  " + name)
    if not ok:
        print("       expected to contain: " + expected)
        print("       got: " + reply.replace("\n", " | ")[:200])
    return ok


def main():
    results = []

    # 1. Greeting
    results.append(check(
        "greeting",
        ShopAgent(), ["hello"], "Assalam-o-Alaikum"))

    # 2. Price question for a real product
    results.append(check(
        "price of chocolate cake",
        ShopAgent(), ["what is the price of chocolate cake?"], "1,200"))

    # 3. Price question for a product that does not exist -> menu, no invented price
    results.append(check(
        "price of unknown product shows menu",
        ShopAgent(), ["what is the price of a pizza?"], "menu"))

    # 4. Out-of-stock product
    results.append(check(
        "out-of-stock product",
        ShopAgent(), ["is mango jam in stock?"], "out of stock"))

    # 5. In-stock product
    results.append(check(
        "in-stock product",
        ShopAgent(), ["is chocolate cake available?"], "in stock"))

    # 6. Delivery question for a served city
    results.append(check(
        "delivery to Lahore",
        ShopAgent(), ["how much is delivery to Lahore?"], "150"))

    # 7. Delivery question with no city -> lists all cities
    results.append(check(
        "delivery list",
        ShopAgent(), ["do you deliver?"], "Karachi"))

    # 8. Shop timings
    results.append(check(
        "timings",
        ShopAgent(), ["what are your timings?"], "9:00 AM"))

    # 9. Payment options
    results.append(check(
        "payment options",
        ShopAgent(), ["how can I pay?"], "Cash on Delivery"))

    # 10. Full order flow: product -> quantity -> name -> city -> summary
    results.append(check(
        "full order flow",
        ShopAgent(),
        ["I want to order cupcakes", "2", "Ayesha", "Lahore"],
        "TOTAL: Rs. 1,950"))

    # 11. Order of an out-of-stock product is refused politely
    results.append(check(
        "order out-of-stock refused",
        ShopAgent(), ["I want to order mango jam"], "out of stock"))

    # 12. Order cancelled mid-flow
    results.append(check(
        "order cancel",
        ShopAgent(), ["I want to order cupcakes", "cancel"], "cancelled"))

    # 13. Unknown question -> escalation, never an invented answer
    results.append(check(
        "unknown question escalates",
        ShopAgent(), ["do you sell cars?"], "shop owner"))

    # 14. Nonsense input -> polite fallback, no crash
    results.append(check(
        "nonsense input",
        ShopAgent(), ["asdf qwer zxcv"], "shop owner"))

    # 15. Thanks
    results.append(check(
        "thanks",
        ShopAgent(), ["thanks"], "welcome"))

    passed = sum(results)
    total = len(results)
    print("\n" + str(passed) + "/" + str(total) + " tests passed.")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())

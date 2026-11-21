"""Offline brain of the AI Agent Kit for Shops.

Keyword and intent matching. No internet, no API key, no AI model needed.
This is what answers customers when there is no AI backend, or when the
AI backend fails. It only answers from the shop data it is given, and it
never invents a price, a stock level, or a delivery promise.
"""

import re

GREETING_WORDS = [
    "hello", "hi", "hey", "salam", "assalam", "aoa",
    "good morning", "good afternoon", "good evening",
]

THANKS_WORDS = ["thanks", "thank you", "shukriya", "shukran"]

GOODBYE_WORDS = ["bye", "allah hafiz", "khuda hafiz", "goodbye", "good night"]

PRICE_WORDS = [
    "price", "rate", "cost", "how much", "kitne", "kitna",
    "kya price", "charges", "paisa", "paise",
]

STOCK_WORDS = [
    "stock", "available", "availability", "hai kya", "hai ya nahi",
    "milay ga", "milega", "in stock", "left", "baki",
]

DELIVERY_WORDS = [
    "deliver", "delivery", "deliver karte", "pohnchana", "pohnchate",
    "shipping", "send karte", "home delivery",
]

TIMING_WORDS = [
    "timing", "hours", "open", "close", "khulta", "khula",
    "band", "kab tak", "working hours", "shop time",
]

PAYMENT_WORDS = [
    "payment", "pay", "cod", "cash on delivery", "jazzcash",
    "easypaisa", "bank", "transfer", "kaise pay",
]

ORDER_WORDS = [
    "order", "buy", "kharid", "kharidna", "book", "mujhe chahiye",
    "i want", "place order", "order karna", "order karna hai",
]

CANCEL_WORDS = ["cancel", "ruk jao", "stop", "nahi chahiye", "rehne do"]


def _contains(text, words):
    """True if any of the words appears in the text."""
    return any(word in text for word in words)


def find_product(text, products):
    """Find the shop product a customer is talking about.

    Matches words from the product name against whole words of the
    message, so "cake" does not match "cupcakes". The product with the
    most matching name words wins. Returns None when nothing matches,
    so the agent can ask which product instead of guessing.
    """
    tokens = re.findall(r"[a-z]+", text.lower())
    best = None
    best_score = 0
    for product in products:
        name_words = [w for w in product["name"].lower().split() if len(w) >= 3]
        score = 0
        for word in name_words:
            for token in tokens:
                if word == token:
                    score += 1
                    break
                if len(word) >= 4 and token.startswith(word):
                    score += 1
                    break
                if len(token) >= 4 and word.startswith(token):
                    score += 1
                    break
        if score > best_score:
            best_score = score
            best = product
    return best


def detect_intent(text, products):
    """Return (intent, product) for a customer message.

    Intents: greeting, thanks, goodbye, order, price, stock, delivery,
    timing, payment, cancel, unknown. Product is the matched shop product
    or None. Order is checked before price and stock, because "I want to
    order a chocolate cake" is an order, not a price question.
    """
    text = text.lower().strip()
    product = find_product(text, products)

    if _contains(text, CANCEL_WORDS):
        return "cancel", product
    if _contains(text, GREETING_WORDS) and len(text.split()) <= 4:
        return "greeting", product
    if _contains(text, THANKS_WORDS):
        return "thanks", product
    if _contains(text, GOODBYE_WORDS):
        return "goodbye", product
    if _contains(text, ORDER_WORDS):
        return "order", product
    if _contains(text, DELIVERY_WORDS):
        return "delivery", product
    if _contains(text, TIMING_WORDS):
        return "timing", product
    if _contains(text, PAYMENT_WORDS):
        return "payment", product
    if _contains(text, PRICE_WORDS):
        return "price", product
    if _contains(text, STOCK_WORDS):
        return "stock", product
    if product is not None:
        # A product name with no question word is usually a price question.
        return "price", product
    return "unknown", None

"""Core agent of the AI Agent Kit for Shops.

The agent answers customer questions from the shop data in shop.json:
product prices, stock, delivery, timings, and payments. It takes orders
step by step and builds an order summary.

Two brains, in this order:
    1. NVIDIA NIM (optional). When use_ai is on and an NVIDIA_API_KEY is
       set, the agent asks the AI first, with the shop data as context.
       If the AI call fails, it falls back to the rules engine and says so.
    2. Rules engine (rules.py). Keyword and intent matching, fully
       offline. This always works, with or without a key.

The agent NEVER invents an answer. A question it cannot answer from the
shop data gets a polite escalation to the shop owner.
"""

import json
import re

from rules import detect_intent, find_product

try:
    from nim_backend import ask_nim, has_key
except ImportError:  # Running without the optional backend file.
    ask_nim = None
    has_key = None


class ShopAgent:
    """A customer-support agent for one small shop."""

    def __init__(self, shop_path="shop.json", use_ai=True):
        with open(shop_path, "r", encoding="utf-8") as handle:
            self.shop = json.load(handle)
        self.products = self.shop["products"]
        self.use_ai = use_ai
        self.state = "idle"          # idle, product, quantity, name, city
        self.order = {}              # product, quantity, name, city
        self.history = []            # short chat history for the AI backend

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def respond(self, message):
        """Answer one customer message. Returns the reply text."""
        message = message.strip()
        if not message:
            return "Please write your question, and I will help you."

        # An order in progress always wins: the message is the next answer.
        if self.state != "idle":
            return self._handle_order_step(message)

        intent, product = detect_intent(message, self.products)

        if intent == "cancel":
            return self._cancel_order()

        # Try the AI backend first, when it is switched on and a key exists.
        if self.use_ai and has_key and has_key():
            reply = self._ask_ai(message)
            if reply:
                self._remember(message, reply)
                return reply
            # AI failed: say so, then answer with the rules engine below.
            fallback = self._answer_rules(intent, product, message)
            return ("(AI reply was not available, so here is the shop's "
                    "offline answer.)\n" + fallback)

        reply = self._answer_rules(intent, product, message)
        self._remember(message, reply)
        return reply

    # ------------------------------------------------------------------
    # Rules engine answers
    # ------------------------------------------------------------------
    def _answer_rules(self, intent, product, message):
        if intent == "greeting":
            return self._greeting()
        if intent == "thanks":
            return "You are most welcome! Anything else I can help you with?"
        if intent == "goodbye":
            return "Thank you for visiting " + self.shop["shop_name"] + ". Allah Hafiz!"
        if intent == "order":
            return self._start_order(product)
        if intent == "price":
            return self._price_answer(product)
        if intent == "stock":
            return self._stock_answer(product)
        if intent == "delivery":
            return self._delivery_answer(message)
        if intent == "timing":
            return self._timing_answer()
        if intent == "payment":
            return self._payment_answer()
        return self._escalate()

    def _greeting(self):
        lines = [
            "Assalam-o-Alaikum! Welcome to " + self.shop["shop_name"] + ".",
            "I can help you with prices, stock, delivery, timings, "
            "payments, or taking an order.",
            "What would you like to know?",
        ]
        return "\n".join(lines)

    def _price_answer(self, product):
        if product is None:
            return self._product_list("Which product's price would you like? Here is our menu:")
        return (product["name"] + " costs Rs. " + format(product["price"], ",")
                + ". " + product["description"])

    def _stock_answer(self, product):
        if product is None:
            return self._product_list("Which product do you want to check? Here is our menu:")
        if product["in_stock"]:
            return product["name"] + " is in stock. Would you like to order it?"
        return ("Sorry, " + product["name"] + " is out of stock right now. "
                "It will be back soon. Would you like to try another product?")

    def _delivery_answer(self, message):
        delivery = self.shop["delivery"]
        areas = delivery["areas"]
        for city, charge in areas.items():
            if city.lower() in message.lower():
                if delivery["free_above_pkr"] and self._last_total() and self._last_total() >= delivery["free_above_pkr"]:
                    return ("Delivery to " + city + " is FREE for this order "
                            "(orders above Rs. "
                            + format(delivery["free_above_pkr"], ",")
                            + " get free delivery). " + delivery["time"] + ".")
                return ("Delivery to " + city + " costs Rs. " + str(charge)
                        + ". " + delivery["time"] + ". Orders above Rs. "
                        + format(delivery["free_above_pkr"], ",")
                        + " get free delivery.")
        lines = ["We deliver to these cities:"]
        for city, charge in areas.items():
            lines.append("- " + city + ": Rs. " + str(charge))
        lines.append("Delivery time: " + delivery["time"] + ".")
        lines.append("Orders above Rs. "
                     + format(delivery["free_above_pkr"], ",")
                     + " get free delivery.")
        return "\n".join(lines)

    def _timing_answer(self):
        timing = self.shop["timings"]
        return ("We are open " + timing["days"] + ", "
                + timing["open"] + " to " + timing["close"] + ". "
                "Friday break: " + timing["friday_break"] + ".")

    def _payment_answer(self):
        methods = ", ".join(self.shop["payment_methods"])
        return "You can pay by: " + methods + "."

    def _product_list(self, intro):
        lines = [intro]
        for product in self.products:
            status = "in stock" if product["in_stock"] else "OUT OF STOCK"
            lines.append("- " + product["name"] + ": Rs. "
                         + format(product["price"], ",") + " (" + status + ")")
        return "\n".join(lines)

    def _escalate(self):
        return ("That is a good question, but I do not have that answer. "
                "I will connect you to the shop owner, who will reply soon. "
                "You can also ask me about prices, stock, delivery, "
                "timings, payments, or placing an order.")

    # ------------------------------------------------------------------
    # Order flow: product -> quantity -> name -> city -> summary
    # ------------------------------------------------------------------
    def _start_order(self, product):
        self.order = {}
        if product is not None:
            if not product["in_stock"]:
                return ("Sorry, " + product["name"] + " is out of stock "
                        "right now. Please pick another product from the menu.")
            self.order["product"] = product
            self.state = "quantity"
            return ("Great! You want to order " + product["name"]
                    + " (Rs. " + format(product["price"], ",") + "). "
                    "How many would you like?")
        self.state = "product"
        return self._product_list("Sure! Which product would you like to order?")

    def _handle_order_step(self, message):
        if message.lower().strip() in ("cancel", "ruk jao", "stop"):
            return self._cancel_order()

        if self.state == "product":
            product = find_product(message, self.products)
            if product is None:
                return self._product_list(
                    "I could not find that product. Please pick one from the menu:")
            if not product["in_stock"]:
                return ("Sorry, " + product["name"] + " is out of stock. "
                        "Please pick another product from the menu.")
            self.order["product"] = product
            self.state = "quantity"
            return ("Great! " + product["name"] + " (Rs. "
                    + format(product["price"], ",") + "). "
                    "How many would you like?")

        if self.state == "quantity":
            match = re.search(r"\d+", message)
            if not match:
                return "Please tell me the quantity as a number, for example 2."
            quantity = int(match.group(0))
            if quantity <= 0:
                return "Quantity must be at least 1. How many would you like?"
            self.order["quantity"] = quantity
            self.state = "name"
            return "Thank you. What is your name?"

        if self.state == "name":
            self.order["name"] = message.strip()
            self.state = "city"
            return "And which city should we deliver to?"

        if self.state == "city":
            self.order["city"] = message.strip()
            return self._order_summary()

        return self._escalate()

    def _order_summary(self):
        product = self.order["product"]
        quantity = self.order["quantity"]
        total = product["price"] * quantity
        delivery = self.shop["delivery"]
        city = self.order["city"]
        charge = delivery["areas"].get(city.title(), None)
        if charge is None:
            for known_city, known_charge in delivery["areas"].items():
                if known_city.lower() in city.lower():
                    charge = known_charge
                    city = known_city
                    break
        if charge is None:
            charge_note = "Delivery to your city will be confirmed by the shop owner."
            grand_total = total
        else:
            if total >= delivery["free_above_pkr"]:
                charge = 0
            charge_note = "Delivery charges: Rs. " + str(charge)
            grand_total = total + charge
        self.order["total"] = grand_total
        self.state = "idle"
        lines = [
            "Here is your order summary:",
            "- Product: " + product["name"] + " x " + str(quantity),
            "- Price: Rs. " + format(total, ","),
            "- Name: " + self.order["name"],
            "- City: " + city,
            "- " + charge_note,
            "- TOTAL: Rs. " + format(grand_total, ","),
            "Payment: " + ", ".join(self.shop["payment_methods"]) + ".",
            "Please confirm, and the shop owner will start your order. Thank you!",
        ]
        return "\n".join(lines)

    def _cancel_order(self):
        self.order = {}
        self.state = "idle"
        return "No problem, the order is cancelled. How else can I help you?"

    def _last_total(self):
        return self.order.get("total")

    # ------------------------------------------------------------------
    # Optional AI backend
    # ------------------------------------------------------------------
    def _system_prompt(self):
        lines = [
            "You are the customer-support agent of " + self.shop["shop_name"]
            + " in " + self.shop["city"] + ". Answer the customer in short, "
            "friendly, simple English.",
            "Only use the shop facts below. Never invent a price, a stock "
            "level, a delivery charge, or a delivery time. If the answer "
            "is not in the facts, say you will connect the customer to "
            "the shop owner.",
            "Products (prices are demo prices in PKR):",
        ]
        for product in self.products:
            status = "in stock" if product["in_stock"] else "OUT OF STOCK"
            lines.append("- " + product["name"] + ": Rs. "
                         + format(product["price"], ",") + " (" + status + ")")
        timing = self.shop["timings"]
        lines.append("Timings: " + timing["days"] + ", " + timing["open"]
                     + " to " + timing["close"] + ". Friday break: "
                     + timing["friday_break"] + ".")
        delivery = self.shop["delivery"]
        lines.append("Delivery: " + delivery["time"] + ". Charges: "
                     + ", ".join(city + " Rs. " + str(charge)
                                 for city, charge in delivery["areas"].items())
                     + ". Free above Rs. "
                     + format(delivery["free_above_pkr"], ",") + ".")
        lines.append("Payments: " + ", ".join(self.shop["payment_methods"]) + ".")
        return "\n".join(lines)

    def _ask_ai(self, message):
        if ask_nim is None:
            return None
        messages = [{"role": "system", "content": self._system_prompt()}]
        messages.extend(self.history[-6:])
        messages.append({"role": "user", "content": message})
        return ask_nim(messages)

    def _remember(self, message, reply):
        self.history.append({"role": "user", "content": message})
        self.history.append({"role": "assistant", "content": reply})
        self.history = self.history[-10:]

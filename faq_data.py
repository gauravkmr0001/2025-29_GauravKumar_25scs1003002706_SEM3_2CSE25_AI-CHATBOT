"""
faq_data.py
------------
This file contains the predefined FAQ dataset used by the chatbot.

Each entry represents one "intent" (a topic/category the user might ask about).
For every intent we provide:
  - "tag"       : a short internal name for the intent (used for logging/context)
  - "patterns"  : several different ways a user might phrase a question about
                   this topic. The more variety we give, the better the chatbot
                   gets at recognizing different phrasings of the same question.
  - "responses" : one or more possible answers. The bot picks one at random
                   so replies feel a little more natural.

Feel free to add more patterns or new intents — the chatbot automatically
adapts to whatever is in this list, no code changes required.
"""

FAQ_DATA = [
    {
        "tag": "greeting",
        "patterns": [
            "hi",
            "hello",
            "hey",
            "hey there",
            "good morning",
            "good afternoon",
            "good evening",
            "is anyone there",
            "howdy",
            "what's up",
            "greetings",
        ],
        "responses": [
            "Hello! Welcome to our support chat. How can I help you today?",
            "Hi there! I'm your virtual assistant. What can I do for you?",
            "Hey! Ask me anything about your account, orders, payments, or refunds.",
        ],
    },
    {
        "tag": "goodbye",
        "patterns": [
            "bye",
            "goodbye",
            "see you later",
            "talk to you later",
            "that's all thanks",
            "thanks bye",
            "close chat",
        ],
        "responses": [
            "Goodbye! Have a great day. Feel free to come back anytime.",
            "Thanks for chatting with us. Take care!",
        ],
    },
    {
        "tag": "thanks",
        "patterns": [
            "thanks",
            "thank you",
            "thanks a lot",
            "that helped",
            "appreciate it",
            "thank you so much",
        ],
        "responses": [
            "You're very welcome! Is there anything else I can help with?",
            "Happy to help! Let me know if you have more questions.",
        ],
    },
    {
        "tag": "account_create",
        "patterns": [
            "how do I create an account",
            "how to sign up",
            "how can I register",
            "I want to create a new account",
            "steps to open an account",
            "how do I make an account",
            "sign up process",
        ],
        "responses": [
            "To create an account, click 'Sign Up' on the top-right corner, "
            "enter your email and a password, then verify your email address.",
        ],
    },
    {
        "tag": "account_password",
        "patterns": [
            "I forgot my password",
            "how do I reset my password",
            "can't log in",
            "reset password",
            "change my password",
            "I lost access to my account",
            "unable to login",
        ],
        "responses": [
            "You can reset your password by clicking 'Forgot Password' on the "
            "login page. We'll send a reset link to your registered email.",
        ],
    },
    {
        "tag": "account_delete",
        "patterns": [
            "how do I delete my account",
            "close my account",
            "remove my account permanently",
            "deactivate my account",
            "cancel my account",
        ],
        "responses": [
            "To delete your account, go to Account Settings > Privacy > "
            "Delete Account. Note this action is permanent and cannot be undone.",
        ],
    },
    {
        "tag": "services_offered",
        "patterns": [
            "what services do you offer",
            "what do you sell",
            "tell me about your products",
            "what can I buy from you",
            "what does your company do",
            "list your services",
        ],
        "responses": [
            "We offer a range of services including subscription plans, "
            "one-time purchases, and premium support packages. "
            "Would you like details on a specific plan?",
        ],
    },
    {
        "tag": "services_pricing",
        "patterns": [
            "how much does it cost",
            "what is the price",
            "pricing plans",
            "how much do you charge",
            "what are your rates",
            "cost of subscription",
        ],
        "responses": [
            "Our pricing starts at $9.99/month for the Basic plan, "
            "$19.99/month for Pro, and $49.99/month for Enterprise. "
            "Would you like a comparison of features?",
        ],
    },
    {
        "tag": "payments_methods",
        "patterns": [
            "what payment methods do you accept",
            "can I pay with paypal",
            "do you accept credit cards",
            "how can I pay",
            "payment options",
            "can I pay with debit card",
        ],
        "responses": [
            "We accept Visa, Mastercard, American Express, PayPal, and "
            "bank transfers for most regions.",
        ],
    },
    {
        "tag": "payments_failed",
        "patterns": [
            "my payment failed",
            "payment is not going through",
            "card declined",
            "transaction failed",
            "payment error",
            "unable to complete payment",
        ],
        "responses": [
            "Sorry about that! Payment failures are usually caused by "
            "incorrect card details or insufficient funds. Please double-check "
            "your card information or try another payment method.",
        ],
    },
    {
        "tag": "refund_policy",
        "patterns": [
            "what is your refund policy",
            "can I get a refund",
            "how do refunds work",
            "refund policy",
            "money back guarantee",
        ],
        "responses": [
            "We offer a 30-day money-back guarantee on all plans. "
            "If you're not satisfied, contact support within 30 days of "
            "purchase for a full refund.",
        ],
    },
    {
        "tag": "refund_request",
        "patterns": [
            "how do I request a refund",
            "I want my money back",
            "start a refund",
            "process a refund",
            "cancel and refund my order",
        ],
        "responses": [
            "To request a refund, go to Order History, select the order, "
            "and click 'Request Refund'. Our team will process it within 5-7 "
            "business days.",
        ],
    },
    {
        "tag": "contact_info",
        "patterns": [
            "how can I contact support",
            "what is your phone number",
            "how do I reach customer service",
            "contact information",
            "customer support email",
            "how do I talk to a human",
        ],
        "responses": [
            "You can reach our support team at support@example.com or call "
            "us at +1-800-555-0199, Monday to Friday, 9 AM - 6 PM.",
        ],
    },
    {
        "tag": "business_hours",
        "patterns": [
            "what are your business hours",
            "when are you open",
            "what time do you close",
            "are you open on weekends",
            "working hours",
        ],
        "responses": [
            "Our support team is available Monday to Friday, 9 AM - 6 PM (EST). "
            "We're closed on weekends and public holidays.",
        ],
    },
    {
        "tag": "order_tracking",
        "patterns": [
            "how do I track my order",
            "where is my order",
            "order status",
            "track my package",
            "has my order shipped",
        ],
        "responses": [
            "You can track your order by going to 'My Orders' and clicking "
            "'Track Shipment'. You'll also receive tracking updates by email.",
        ],
    },
]

def ai_response(message):
    msg = message.lower()
    if any(word in msg for word in ["flour","unga","maize","ajab"]):
        return "We have Ajab Maize Flour 2kg at KES 175 at Naivas. The cheapest price is KES 172 at Carrefour. 50 packs in stock. Would you like me to add it to your cart?"
    if "milk" in msg:
        return "Brookside Milk 500ml is KES 65 at Naivas (100 in stock) and KES 62 at Chandarana - fresh daily. Would you like to add it to your cart?"
    if "bread" in msg:
        return "White Bread 400g is KES 60 at Naivas - soft and fresh. 70 loaves available. It goes well with milk!"
    if "soda" in msg or "coke" in msg or "drink" in msg:
        return "Coca Cola 1.25L is KES 100 at Quickmart and KES 99 at Magunas - chilled and ready. 80 bottles available."
    if "price" in msg or "compare" in msg or "cheap" in msg:
        return "I compare prices across 5 stores: Naivas, Quickmart, Carrefour, Chandarana, and Magunas. Tell me what you need - for example 'flour' or 'milk' - and I will find the cheapest price for you."
    if "rider" in msg or "delivery" in msg or "how long" in msg:
        return "Rider delivery takes 30 minutes within Kajiado, Kitengela, and Ongata Rongai. Delivery fee is KES 100. We have 3 riders available: John Mwangi (4.9 stars), Peter Ochieng (4.8 stars), and Samuel Kiprop (5.0 stars). Place your order now!"
    if "tomato" in msg:
        return "Fresh Tomatoes 1kg is KES 80 at Quickmart - directly from the farm. 60kg available today."
    if "omo" in msg or "detergent" in msg:
        return "Omo Detergent 1kg is KES 285 at Carrefour (cheapest) compared to KES 290 at Naivas. It removes tough stains. 40 packs left. We also have Geisha Soap at KES 55 at Magunas."
    if "hello" in msg or "hi" in msg:
        return "Hello! I am LONMA AI - your supermarket shopping assistant. I can help you find the cheapest prices, check stock availability, track your rider, and recommend products. What do you need today?"
    if "cart" in msg or "order" in msg:
        return "To place an order, add products by clicking the Add button, then click the cart icon at the top right to checkout. You can pay with M-Pesa or Cash on Delivery. Rider delivery is 30 minutes!"
    if "stock" in msg or "available" in msg:
        stock_list = ", ".join([f"{p['name']} ({p['stock']} left)" for p in PRODUCTS[:4]])
        return f"Current stock available: {stock_list}. Which item would you like?"
    if "help" in msg:
        return "I can help you with:\n• Finding products - say 'flour' or 'milk'\n• Comparing prices - say 'cheapest soda'\n• Checking delivery - say 'rider delivery time'\n• Tracking orders - say 'where is my order'\n• Recipe ideas - say 'what to cook with tomatoes'\nWhat would you like to know?"
    if "cook" in msg or "recipe" in msg:
        return "With Tomatoes, Flour, and Milk: You can make ugali with tomato stew and tea. Total cost: Flour KES 175 + Tomatoes KES 80 + Milk KES 65 = KES 320. Would you like the full recipe?"
    found = [p for p in PRODUCTS if any(w in p["name"].lower() for w in msg.split())]
    if found:
        p = found[0]
        return f"Found {p['name']} - KES {p['price']} at {p['store'].upper()} ({p['stock']} in stock). {p['desc']}. Would you like to add it to your cart?"
    return "I did not understand that. Please try: 'cheapest flour', 'milk price', 'rider delivery time', 'what is in stock', or 'help'."

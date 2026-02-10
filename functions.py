"""
functions.py
Each function handles ONE CASE
"""
import llm

def case_1_delivery_type(text, context):
    context["delivery_type"] = text
    delivery_confirmation_intent = llm.detect_intent_urdu(text)
    print(f"🤖 Intent detected: {delivery_confirmation_intent}")
    if delivery_confirmation_intent == "no":
        print("🤖 Aapka order cancel kar diya gaya hai. Shukriya!")
        return None  # END CONVERSATION (returns None to signal end)
    print("🤖 Aap kya order karna chahte hain?")
    return 2

def case_2_order_item(text, context):
    context["order_item"] = text
    print("🤖 Quantity bataein")
    return 3

def case_3_quantity(text, context):
    context["quantity"] = text
    print("🤖 Kya kuch aur chahiye?")
    return 4

def case_4_extra(text, context):
    context["extra"] = text
    print("🤖 Apna Adress bataen?")
    return 5

def case_5_address(text, context):
    context["address"] = text
    if "address" in context:
         reformatted_address = llm.reformat_address_to_english(context["address"])
         if reformatted_address:
             context["address"] = reformatted_address
             print(f"🤖 Reformatted Address: {reformatted_address}")
         else:
             print("🤖 Address ko samajhne mein problem hui. Address doobara bataen.")
             return 5  # Ask for address again

    print("\n✅ ORDER SUMMARY")
    for k, v in context.items():
        #display_rev = v[::-1]
        print(f"{k}: {v}")
    print("🤖 Shukriya! Aapka order confirm kar diya gaya hai.")
    return None  # END CONVERSATION (returns None to signal end)

# Dictionary mapping case numbers to functions
CASE_FUNCTIONS = {
    1: case_1_delivery_type,
    2: case_2_order_item,
    3: case_3_quantity,
    4: case_4_extra,
    5: case_5_address
}

#print(f"Intent detected: {llm.detect_intent_urdu('نہیں شکریہ')}")
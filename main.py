# main.py - Entry point for the voice agent

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator.greeting import GreetingOrchestrator
from orchestrator.order_item import OrderItemOrchestrator
from orchestrator.quantity import QuantityOrchestrator
from orchestrator.extras import ExtrasOrchestrator
from orchestrator.address import AddressOrchestrator
from integration.routeToAgent import RouteToAgent

from logger import setup_logger


async def voice_agent_controller():
    """
    Main controller for the voice agent.
    Orchestrates the entire order flow.
    """

    logger = setup_logger()
    
    print("=" * 50)
    print("🎙️  KFC Voice Agent Started")
    print("=" * 50)

    await asyncio.sleep(1)  # ✅ 1 second delay before flow starts
    
    # Single context dict for entire call
    context = {
        "msisdn": "923001234567",   # In real system: passed from incoming call
        "intent": None,
        "customer_profile": None,
        "order_item": None,
        "quantity": None,
        "extra": None,
        "address": None,
        "cost": None,
    }
    
    # Step 1: Greeting and intent detection
    print("\n📍 Step 1: Greeting")
    print("-" * 50)
    greeting_orchestrator = GreetingOrchestrator(logger=logger)
    should_proceed = await greeting_orchestrator.execute()
    
    if not should_proceed:
        print("\n❌ User chose not to order or unclear response. Ending call.")
        routeToAgent_orchestrator = RouteToAgent()
        await routeToAgent_orchestrator.routeCallToAgent()
        return

    print("\n✅ User wants to place an order. Proceeding...")
    context["intent"] = "order"    # ✅ save intent after greeting confirmed

    # Step 5: Collect address
    print("\n📍 Step 2: Address")
    print("-" * 50)
    address_orchestrator = AddressOrchestrator(logger=logger)
    success = await address_orchestrator.execute(context)
    
    if not success:
        print("\n❌ Failed to collect valid address. Ending call.")
        return
    
    # Step 2: Collect order item
    print("\n📍 Step 3: Order Item")
    print("-" * 50)
    order_item_orchestrator = OrderItemOrchestrator(logger=logger)
    success = await order_item_orchestrator.execute(context)
    
    if not success:
        print("\n❌ Failed to collect order item. Ending call.")
        return
    
    # Step 3: Collect quantity
    print("\n📍 Step 4: Quantity")
    print("-" * 50)
    quantity_orchestrator = QuantityOrchestrator(logger=logger)
    success = await quantity_orchestrator.execute(context)
    
    if not success:
        print("\n❌ Failed to collect quantity. Ending call.")
        return
    
    # Step 4: Collect extras
    print("\n📍 Step 5: Extras")
    print("-" * 50)
    extras_orchestrator = ExtrasOrchestrator(logger=logger)
    success = await extras_orchestrator.execute(context)
    
    if not success:
        print("\n❌ Failed to collect extras. Ending call.")
        return

    
    # Final: Display order summary
    print("\n" + "=" * 50)
    print("✅ ORDER SUMMARY")
    print("=" * 50)
    
    for key, value in context.items():
        # Reverse string values for better urdu readability in console, except for address and intent which are english
        if isinstance(value, str) and key.lower() in ["order_item", "quantity", "extra"]:
            print(f"  {key.upper()}: {value[::-1]}")
        else:
            print(f"  {key.upper()}: {value}")
    
    print("\n🎉 Order confirmed! Thank you for calling KFC.")
    print("=" * 50)


if __name__ == "__main__":
    try:
        asyncio.run(voice_agent_controller())
    except KeyboardInterrupt:
        print("\n\n⚠️  Voice agent stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
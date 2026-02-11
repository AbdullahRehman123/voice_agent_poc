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


async def voice_agent_controller():
    """
    Main controller for the voice agent.
    Orchestrates the entire order flow.
    """
    
    print("=" * 50)
    print("🎙️  KFC Voice Agent Started")
    print("=" * 50)
    
    # Shared context to store order details
    context = {}
    
    # Step 1: Greeting and intent detection
    print("\n📍 Step 1: Greeting")
    print("-" * 50)
    greeting_orchestrator = GreetingOrchestrator()
    should_proceed = await greeting_orchestrator.execute()
    
    if not should_proceed:
        print("\n❌ User chose not to order or unclear response. Ending call.")
        return
    
    print("\n✅ User wants to place an order. Proceeding...")
    
    # Step 2: Collect order item
    print("\n📍 Step 2: Order Item")
    print("-" * 50)
    order_item_orchestrator = OrderItemOrchestrator()
    success = await order_item_orchestrator.execute(context)
    
    if not success:
        print("\n❌ Failed to collect order item. Ending call.")
        return
    
    # Step 3: Collect quantity
    print("\n📍 Step 3: Quantity")
    print("-" * 50)
    quantity_orchestrator = QuantityOrchestrator()
    success = await quantity_orchestrator.execute(context)
    
    if not success:
        print("\n❌ Failed to collect quantity. Ending call.")
        return
    
    # Step 4: Collect extras
    print("\n📍 Step 4: Extras")
    print("-" * 50)
    extras_orchestrator = ExtrasOrchestrator()
    success = await extras_orchestrator.execute(context)
    
    if not success:
        print("\n❌ Failed to collect extras. Ending call.")
        return
    
    # Step 5: Collect address
    print("\n📍 Step 5: Address")
    print("-" * 50)
    address_orchestrator = AddressOrchestrator()
    success = await address_orchestrator.execute(context)
    
    if not success:
        print("\n❌ Failed to collect valid address. Ending call.")
        return
    
    # Final: Display order summary
    print("\n" + "=" * 50)
    print("✅ ORDER SUMMARY")
    print("=" * 50)
    
    for key, value in context.items():
        print(f"{key.upper()}: {value}")
    
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
import logging
from typing import Annotated, Optional, Union
from pydantic import Field

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    function_tool,
    metrics,
    tokenize,
    RunContext,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from commerce import (
    get_products, 
    create_order, 
    get_last_order, 
    get_all_orders,
    find_product_by_name,
    add_to_cart,
    get_cart,
    remove_from_cart,
    clear_cart,
    checkout_cart,
)

logger = logging.getLogger("agent")

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are an Amazon shopping assistant. Concise, helpful. You can browse products and place orders. Always summarize the order price before confirming.
            
            You have access to these function tools:
            - browse_products: Search, filter, and SORT products in the catalog. Use this when users ask about products, want to see items, browse the catalog, or request sorting. The browse_products function supports sorting with sort_by parameter: "price_asc" (cheapest first), "price_desc" (most expensive first), "rating_desc" (highest rated first), "name_asc" (A-Z), "name_desc" (Z-A). When users ask to sort, order by price, show cheapest/most expensive, or highest rated, ALWAYS use the sort_by parameter in browse_products.
            - place_order: Place an order for a product. Always confirm the total price in INR before finalizing.
            - get_last_order_info: Get information about the user's last order.
            - add_to_cart: Add products to shopping cart. Use this when users want to add items to their cart.
            - view_cart: View current cart contents. ALWAYS call this function when users ask "what's in my cart", "show my cart", "what did I add", or any question about their shopping cart.
            - remove_from_cart: Remove items from cart. ALWAYS call this function when users ask to remove, delete, or take out items from their cart. Use the product name the user mentions.
            - checkout_cart: Complete purchase from cart. Use this when users want to buy everything in their cart.
            - get_order_history: View all past orders.
            - get_product_details: Get detailed information about a specific product.
            
            When users ask about products, immediately call browse_products. When they want to buy something, use place_order or checkout_cart. 
            When users ask about their cart (e.g., "what's in my cart", "show my cart"), ALWAYS call view_cart first.
            When users want to remove items from cart, ALWAYS call remove_from_cart with the product name they mention.
            When users ask to sort products (e.g., "sort by price", "show cheapest", "most expensive", "highest rated"), ALWAYS call browse_products with the appropriate sort_by parameter. DO NOT say you can't sort - you can sort using browse_products with sort_by parameter.
            Always mention prices in Indian Rupees (₹).""",
        )
    

    @function_tool(description="Search and filter products from the catalog. All parameters are optional - provide only what you need.")
    async def browse_products(
        self,
        context: RunContext,
        search_term: Annotated[
            Optional[str],
            Field(description="Search by product name or keyword", default="")
        ] = "",
        category: Annotated[
            Optional[str],
            Field(description="Filter by category", default="")
        ] = "",
        max_price: Annotated[
            Optional[int],
            Field(description="Maximum price in INR", default=0)
        ] = 0,
        min_price: Annotated[
            Optional[int],
            Field(description="Minimum price in INR", default=0)
        ] = 0,
        sort_by: Annotated[
            Optional[str],
            Field(description="Sort option: price_asc, price_desc, rating_desc, name_asc", default="")
        ] = "",
    ) -> str:
        """
        Browse and filter products by search term, category, price range, or sorting preference.
        
        ALL PARAMETERS ARE OPTIONAL. You can provide any combination of:
        - search_term: Search by product name or keyword (e.g., "camera", "echo")
        - category: Filter by category (e.g., "electronics", "tablets", "smart-home")
        - max_price: Maximum price in INR (e.g., 10000, 50000)
        - min_price: Minimum price in INR
        - sort_by: Sort option - "price_asc" (low to high), "price_desc" (high to low), "rating_desc" (best rated), "name_asc" (alphabetical)
        
        Examples:
        - browse_products(search_term="camera") → finds all cameras
        - browse_products(max_price=30000) → products under ₹30,000
        - browse_products(search_term="sony", category="electronics") → Sony products in electronics
        - browse_products(sort_by="price_asc") → cheapest products first
        - browse_products(search_term="camera", max_price=10000) → cameras under ₹10,000
        """
        try:
            logger.info(
                f"browse_products called with: search_term={search_term}, "
                f"category={category}, max_price={max_price}, min_price={min_price}, "
                f"sort_by={sort_by}"
            )

            # Normalize empty strings and 0 to None for optional parameters
            # This allows the LLM to omit parameters without validation errors
            search_term = str(search_term).strip() if search_term else None
            category = str(category).strip().lower() if category else None
            max_price = int(max_price) if max_price and max_price > 0 else None
            min_price = int(min_price) if min_price and min_price > 0 else None
            sort_by = str(sort_by).strip() if sort_by else None
            
            # Call commerce layer with all parameters (handles None correctly)
            filtered_products = get_products(
                search_term=search_term,
                category=category,
                max_price=max_price,
                min_price=min_price,
                sort_by=sort_by
            )

            logger.info(f"Found {len(filtered_products)} products")

            if not filtered_products:
                return "Sorry, I couldn't find any products matching your criteria."

            # ✅ Send filter metadata to frontend via LiveKit data channel
            # This keeps the UI in sync with what the agent found
            # Only include non-empty parameters
            filter_params = []
            if search_term and search_term.strip():
                filter_params.append(f"search_term={search_term.strip()}")
            if category and category.strip():
                filter_params.append(f"category={category.strip()}")
            if max_price and max_price > 0:
                filter_params.append(f"max_price={max_price}")
            if min_price and min_price > 0:
                filter_params.append(f"min_price={min_price}")
            if sort_by and sort_by.strip() and sort_by.strip() != 'default':
                filter_params.append(f"sort_by={sort_by.strip()}")
            
            if filter_params:
                filter_message = f"[FILTER:{'&'.join(filter_params)}]"
                
                try:
                    import asyncio
                    async def send_metadata():
                        try:
                            await context.room.local_participant.publish_data(
                                filter_message.encode("utf-8"),
                                topic="chat",
                                reliable=True
                            )
                            logger.info(f"✅ Filter metadata sent to frontend: {filter_message}")
                        except Exception as e:
                            logger.warning(f"❌ Could not send metadata via data channel: {e}", exc_info=True)
                    
                    # Don't await - run in background
                    asyncio.create_task(send_metadata())
                except Exception as e:
                    logger.warning(f"❌ Could not create metadata send task: {e}", exc_info=True)
            else:
                logger.info("ℹ️ No filter parameters to send (all empty)")

            # Format response for agent to speak
            product_names = ", ".join([
                f"*{p['name']}* (₹{p['price']})"
                for p in filtered_products[:5]
            ])

            return (
                f"Found {len(filtered_products)} products. "
                f"Here are some options: {product_names}"
            )
        except Exception as e:
            logger.error("=" * 50)
            logger.error(f"❌ ERROR in browse_products: {e}", exc_info=True)
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details - search_term={search_term!r} (type: {type(search_term)}), category={category!r} (type: {type(category)}), max_price={max_price} (type: {type(max_price)}), min_price={min_price} (type: {type(min_price)}), sort_by={sort_by!r} (type: {type(sort_by)})")
            logger.error("=" * 50)
            # Return a user-friendly error message
            return f"I encountered an error while searching for products: {str(e)}. Please try again with simpler search terms."

    @function_tool(description="Place an order for a product")
    async def place_order(
        self,
        context: RunContext,
        product_name_or_id: str,
        quantity: Optional[int] = 1,
    ) -> str:
        """
        Place a new order for a product.
        
        Example: place_order(product_name_or_id="Echo Dot", quantity=2)
        """
        logger.info(f"Placing order: product_name_or_id={product_name_or_id}, quantity={quantity}")

        # Try to find product by name first
        product = find_product_by_name(product_name_or_id)
        
        if product:
            product_id = product["id"]
            logger.info(f"Found product by name: {product_name_or_id} -> {product_id}")
        else:
            # Assume it's already a product ID
            product_id = product_name_or_id
            logger.info(f"Using as product ID: {product_id}")

        try:
            order = create_order(product_id=product_id, quantity=quantity)
            logger.info(f"Order created successfully: {order['id']}")
            return f"Order confirmed! Order ID: {order['id']}. You ordered {quantity}x {order['items'][0]['product_name']} for a total of ₹{order['total']:,} {order['currency']}. Your order has been placed and will appear in the Live Order Status panel. Thank you for your purchase!"
        except ValueError as e:
            # If product ID lookup failed, try one more time with name search
            product = find_product_by_name(product_name_or_id)
            if product:
                try:
                    order = create_order(product_id=product["id"], quantity=quantity)
                    return f"Order confirmed! Order ID: {order['id']}. You ordered {quantity}x {order['items'][0]['product_name']} for a total of ₹{order['total']:,} {order['currency']}. Thank you for your purchase!"
                except ValueError as ve:
                    logger.error(f"Error creating order: {ve}")
                    return f"I found the product '{product['name']}' but couldn't create the order. Please try again."
            logger.error(f"Product not found: {product_name_or_id}, error: {e}")
            return f"I couldn't find a product matching '{product_name_or_id}'. Please try using the exact product name or browse products first to see available items."
        except Exception as e:
            logger.error(f"Unexpected error in place_order: {e}", exc_info=True)
            return f"I encountered an error while processing your order. Please try again or browse products first to see available items."

    @function_tool(description="View your most recent order")
    async def get_last_order_info(self, context: RunContext) -> str:
        """Get information about your most recent order."""
        logger.info("Getting last order info")

        try:
            order = get_last_order()
            if not order:
                return "You haven't placed any orders yet."

            items_summary = ", ".join([
                f"{item['quantity']}x {item['product_name']}"
                for item in order.get('items', [])
            ])

            return (
                f"📦 Your Last Order:\n"
                f"Order ID: {order['id']}\n"
                f"Items: {items_summary}\n"
                f"Total: ₹{order['total']:,}\n"
                f"Status: {order['status']}\n"
                f"Placed: {order['created_at']}"
            )
        except Exception as e:
            logger.error(f"Error getting last order: {str(e)}")
            return "Sorry, I couldn't retrieve your order."

    @function_tool(description="View your order history")
    async def get_order_history(
        self,
        context: RunContext,
        limit: Optional[int] = 5,
    ) -> str:
        """Get your recent orders."""
        logger.info("Getting order history")

        orders = get_all_orders()
        if not orders:
            return "You have no orders yet."

        recent = orders[-limit:] if limit else orders
        
        order_summary = "\n".join([
            f"  • Order #{i+1}: {order['id']} → ₹{order['total']:,} ({order['status']})"
            for i, order in enumerate(reversed(recent))
        ])
        
        return f"📜 Your Recent Orders:\n{order_summary}"

    @function_tool(description="Add a product to your shopping cart")
    async def add_to_cart(
        self,
        context: RunContext,
        product_name_or_id: str,
        quantity: Optional[int] = 1,
    ) -> str:
        """Add items to your cart."""
        logger.info(f"Adding to cart: product_name_or_id={product_name_or_id}, quantity={quantity}")

        # Find product by name
        product = find_product_by_name(product_name_or_id)
        if not product:
            return f"I couldn't find a product matching '{product_name_or_id}'. Please browse products first to see available items."

        try:
            result = add_to_cart(product["id"], quantity)
            cart = result["cart"]
            total = sum(item["unit_amount"] * item["quantity"] for item in cart)
            return f"{result['message']}. Your cart now has {len(cart)} item(s) with a total of ₹{total:,}."
        except Exception as e:
            logger.error(f"Error adding to cart: {e}", exc_info=True)
            return f"I encountered an error adding '{product_name_or_id}' to your cart. Please try again."

    @function_tool(description="View your shopping cart")
    async def view_cart(self, context: RunContext) -> str:
        """Get current cart contents and total."""
        logger.info("Viewing cart")

        cart = get_cart()
        if not cart or len(cart) == 0:
            return "Your cart is empty. Add some products to get started!"

        items_summary = "\n".join([
            f"  • {item['quantity']}x {item['product_name']} @ ₹{item['unit_amount']} each = ₹{item['quantity'] * item['unit_amount']:,}"
            for item in cart
        ])

        total = sum(item['quantity'] * item['unit_amount'] for item in cart)

        return f"🛒 Cart Contents:\n{items_summary}\n\nTotal: ₹{total:,}"

    @function_tool(description="Remove a product from your cart")
    async def remove_from_cart(
        self,
        context: RunContext,
        product_name_or_id: str,
    ) -> str:
        """Remove an item from your shopping cart."""
        logger.info(f"Removing from cart: product_name_or_id={product_name_or_id}")

        # Find product by name
        product = find_product_by_name(product_name_or_id)
        if not product:
            return f"I couldn't find a product matching '{product_name_or_id}' in your cart."

        try:
            result = remove_from_cart(product["id"])
            cart = result["cart"]
            if cart:
                total = sum(item["unit_amount"] * item["quantity"] for item in cart)
                return f"{result['message']}. Your cart now has {len(cart)} item(s) with a total of ₹{total:,}."
            else:
                return f"{result['message']}. Your cart is now empty."
        except Exception as e:
            logger.error(f"Error removing from cart: {e}", exc_info=True)
            return f"I encountered an error removing '{product_name_or_id}' from your cart. Please try again."

    @function_tool(description="Checkout and place order from your cart")
    async def checkout_cart(self, context: RunContext) -> str:
        """Convert cart to order and proceed with checkout."""
        logger.info("Checking out cart")

        try:
            cart = get_cart()
            if not cart or len(cart) == 0:
                return "Your cart is empty. Add products before checkout."

            order = checkout_cart()
            logger.info(f"Checkout completed: {order['id']}")

            items_count = sum(item['quantity'] for item in order['items'])
            return (
                f"✅ Checkout successful!\n"
                f"Order ID: {order['id']}\n"
                f"Items: {items_count}\n"
                f"Total: ₹{order['total']:,}\n"
                f"Status: {order['status']}"
            )
        except Exception as e:
            logger.error(f"Error during checkout: {str(e)}")
            return "Sorry, checkout failed. Please try again."

    @function_tool(description="Get detailed information about a product")
    async def get_product_details(
        self,
        context: RunContext,
        product_name_or_id: str,
    ) -> str:
        """Get complete details about a specific product."""
        logger.info(f"Getting product details: product_name_or_id={product_name_or_id}")

        try:
            product = find_product_by_name(product_name_or_id)
            if not product:
                return f"Product not found."

            return (
                f"📦 {product['name']}\n"
                f"💵 Price: ₹{product['price']:,}\n"
                f"📂 Category: {product['category']}\n"
                f"⭐ Rating: {product['rating']}/5 ({product['reviews']:,} reviews)\n"
                f"📝 Description: {product['description']}"
            )
        except Exception as e:
            logger.error(f"Error getting product details: {str(e)}")
            return "Sorry, I couldn't retrieve product details."


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
                model="gemini-2.5-flash",
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
            voice="en-US-matthew", 
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Create agent instance - keep it simple to ensure it works
    agent_instance = Assistant()
    logger.info("Agent initialized. Function tools should be automatically registered via @function_tool decorator.")


    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=agent_instance,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Note: Transcriptions should be automatically forwarded by the session
    # The frontend's useTranscriptions() hook will capture them
    # If transcriptions don't appear, ensure the session is properly configured

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
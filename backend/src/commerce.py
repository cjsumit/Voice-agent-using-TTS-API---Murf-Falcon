"""E-commerce merchant API for Day 9 - Amazon-style product catalog and order management."""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

# Amazon-style product catalog
CATALOG = [
    {
        "id": "echo-dot-5",
        "name": "Echo Dot (5th Gen)",
        "description": "Smart speaker with Alexa - Charcoal",
        "price": 4499,
        "currency": "INR",
        "category": "electronics",
        "image_url": "https://picsum.photos/300/300?random=1",
        "rating": 4.5,
        "reviews": 12500,
    },
    {
        "id": "kindle-paperwhite",
        "name": "Kindle Paperwhite",
        "description": "8 GB - Now with a 6.8\" display and adjustable warm light",
        "price": 13999,
        "currency": "INR",
        "category": "electronics",
        "image_url": "https://picsum.photos/300/300?random=2",
        "rating": 4.6,
        "reviews": 8900,
    },
    {
        "id": "fire-tv-stick",
        "name": "Fire TV Stick 4K",
        "description": "Streaming device with Alexa Voice Remote",
        "price": 4999,
        "currency": "INR",
        "category": "electronics",
        "image_url": "https://picsum.photos/300/300?random=3",
        "rating": 4.4,
        "reviews": 15200,
    },
    {
        "id": "echo-show-8",
        "name": "Echo Show 8",
        "description": "HD smart display with Alexa - Charcoal",
        "price": 8999,
        "currency": "INR",
        "category": "electronics",
        "image_url": "https://picsum.photos/300/300?random=4",
        "rating": 4.5,
        "reviews": 11200,
    },
    {
        "id": "ring-doorbell",
        "name": "Ring Video Doorbell",
        "description": "1080p HD video, motion detection, two-way talk",
        "price": 9999,
        "currency": "INR",
        "category": "home-security",
        "image_url": "https://picsum.photos/300/300?random=5",
        "rating": 4.3,
        "reviews": 7800,
    },
    {
        "id": "alexa-smart-plug",
        "name": "TP-Link Smart Plug",
        "description": "Works with Alexa - Control your home from anywhere",
        "price": 999,
        "currency": "INR",
        "category": "smart-home",
        "image_url": "https://picsum.photos/300/300?random=6",
        "rating": 4.2,
        "reviews": 5600,
    },
    {
        "id": "blink-outdoor",
        "name": "Blink Outdoor Camera",
        "description": "Wireless security camera with two-year battery life",
        "price": 7999,
        "currency": "INR",
        "category": "home-security",
        "image_url": "https://picsum.photos/300/300?random=7",
        "rating": 4.1,
        "reviews": 4200,
    },
    {
        "id": "roku-express",
        "name": "Roku Express 4K+",
        "description": "Streaming media player with voice remote",
        "price": 3999,
        "currency": "INR",
        "category": "electronics",
        "image_url": "https://picsum.photos/300/300?random=3",
        "rating": 4.3,
        "reviews": 9800,
    },
    {
        "id": "echo-show-10",
        "name": "Echo Show 10 (3rd Gen)",
        "description": "10.1\" HD smart display with motion - Charcoal",
        "price": 24999,
        "currency": "INR",
        "category": "electronics",
        "image_url": "https://picsum.photos/300/300?random=4",
        "rating": 4.6,
        "reviews": 6800,
    },
    {
        "id": "echo-studio",
        "name": "Echo Studio",
        "description": "High-fidelity smart speaker with 3D audio and Alexa",
        "price": 22999,
        "currency": "INR",
        "category": "electronics",
        "image_url": "https://picsum.photos/300/300?random=8",
        "rating": 4.7,
        "reviews": 5200,
    },
    {
        "id": "kindle-oasis",
        "name": "Kindle Oasis",
        "description": "32 GB - Premium e-reader with 7\" display and page turn buttons",
        "price": 27999,
        "currency": "INR",
        "category": "electronics",
        "image_url": "https://picsum.photos/300/300?random=2",
        "rating": 4.8,
        "reviews": 3400,
    },
    {
        "id": "fire-tv-cube",
        "name": "Fire TV Cube (3rd Gen)",
        "description": "4K streaming media player with built-in Alexa and hands-free TV control",
        "price": 12999,
        "currency": "INR",
        "category": "electronics",
        "image_url": "https://picsum.photos/300/300?random=3",
        "rating": 4.5,
        "reviews": 9100,
    },
    {
        "id": "ring-floodlight",
        "name": "Ring Floodlight Cam Wired Pro",
        "description": "1080p HD security camera with motion-activated LED floodlights",
        "price": 18999,
        "currency": "INR",
        "category": "home-security",
        "image_url": "https://picsum.photos/300/300?random=7",
        "rating": 4.4,
        "reviews": 2900,
    },
    {
        "id": "blink-mini",
        "name": "Blink Mini Camera",
        "description": "Compact indoor plug-in smart security camera with motion detection",
        "price": 2999,
        "currency": "INR",
        "category": "home-security",
        "image_url": "https://picsum.photos/300/300?random=7",
        "rating": 4.2,
        "reviews": 15600,
    },
    {
        "id": "philips-hue",
        "name": "Philips Hue White and Color Ambiance",
        "description": "Smart LED light bulb with 16 million colors, works with Alexa",
        "price": 5499,
        "currency": "INR",
        "category": "smart-home",
        "image_url": "https://picsum.photos/300/300?random=11",
        "rating": 4.6,
        "reviews": 12300,
    },
    {
        "id": "smart-lock",
        "name": "August Smart Lock Pro",
        "description": "Wi-Fi enabled smart lock with Alexa and Google Assistant support",
        "price": 19999,
        "currency": "INR",
        "category": "smart-home",
        "image_url": "https://picsum.photos/300/300?random=6",
        "rating": 4.3,
        "reviews": 2100,
    },
    {
        "id": "nest-thermostat",
        "name": "Google Nest Learning Thermostat",
        "description": "3rd Gen smart thermostat that learns your schedule and saves energy",
        "price": 15999,
        "currency": "INR",
        "category": "smart-home",
        "image_url": "https://picsum.photos/300/300?random=6",
        "rating": 4.5,
        "reviews": 4500,
    },
    {
        "id": "echo-buds",
        "name": "Echo Buds (2nd Gen)",
        "description": "True wireless earbuds with active noise cancellation and Alexa",
        "price": 8999,
        "currency": "INR",
        "category": "electronics",
        "image_url": "https://picsum.photos/300/300?random=9",
        "rating": 4.4,
        "reviews": 8700,
    },
    {
        "id": "fire-tablet",
        "name": "Fire HD 10 Tablet",
        "description": "10.1\" 1080p Full HD display, 32 GB, Black",
        "price": 12499,
        "currency": "INR",
        "category": "electronics",
        "image_url": "https://picsum.photos/300/300?random=10",
        "rating": 4.3,
        "reviews": 18900,
    },
    {
        "id": "ring-alarm",
        "name": "Ring Alarm 8-Piece Kit",
        "description": "Home security system with motion detector, contact sensor, and base station",
        "price": 24999,
        "currency": "INR",
        "category": "home-security",
        "image_url": "https://picsum.photos/300/300?random=7",
        "rating": 4.5,
        "reviews": 3200,
    },
    {
        "id": "wyze-cam",
        "name": "Wyze Cam v3",
        "description": "1080p HD indoor/outdoor security camera with night vision",
        "price": 3499,
        "currency": "INR",
        "category": "home-security",
        "image_url": "https://picsum.photos/300/300?random=7",
        "rating": 4.4,
        "reviews": 22100,
    },
    {
        "id": "smart-switch",
        "name": "TP-Link Kasa Smart Wi-Fi Light Switch",
        "description": "Works with Alexa and Google Assistant, no hub required",
        "price": 1999,
        "currency": "INR",
        "category": "smart-home",
        "image_url": "https://picsum.photos/300/300?random=6",
        "rating": 4.5,
        "reviews": 13400,
    },
]

# Store orders.json and cart.json in the backend directory (parent of src)
_BACKEND_DIR = Path(__file__).parent.parent
ORDERS_FILE = str(_BACKEND_DIR / "orders.json")
CART_FILE = str(_BACKEND_DIR / "cart.json")


def _load_orders() -> list[dict]:
    """Load orders from JSON file, creating it if it doesn't exist."""
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure it's a list
                if isinstance(data, list):
                    return data
                return []
        except (json.JSONDecodeError, IOError, OSError) as e:
            logger = logging.getLogger("commerce")
            logger.warning(f"Error loading orders file: {e}")
            return []
    return []


def _save_orders(orders: list[dict]) -> None:
    """Save orders to JSON file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(ORDERS_FILE) if os.path.dirname(ORDERS_FILE) else ".", exist_ok=True)
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(orders, f, indent=2, ensure_ascii=False)
    except (IOError, OSError) as e:
        logger = logging.getLogger("commerce")
        logger.error(f"Error saving orders file: {e}")
        raise


def _validate_product(product: dict) -> bool:
    """Validate that a product has all required fields."""
    required_fields = ["id", "name", "description", "price", "currency", "category", "image_url", "rating", "reviews"]
    for field in required_fields:
        if field not in product:
            logger = logging.getLogger("commerce")
            logger.warning(f"Product {product.get('id', 'unknown')} missing required field: {field}")
            return False
        # Validate field types
        if field == "price" and (not isinstance(product[field], (int, float)) or product[field] < 0):
            logger.warning(f"Product {product.get('id', 'unknown')} has invalid price: {product[field]}")
            return False
        if field == "rating" and (not isinstance(product[field], (int, float)) or product[field] < 0 or product[field] > 5):
            logger.warning(f"Product {product.get('id', 'unknown')} has invalid rating: {product[field]}")
            return False
        if field == "reviews" and (not isinstance(product[field], int) or product[field] < 0):
            logger.warning(f"Product {product.get('id', 'unknown')} has invalid reviews: {product[field]}")
            return False
    return True


def get_products(
    category: Optional[str] = None,
    max_price: Optional[int] = None,
    min_price: Optional[int] = None,
    search_term: Optional[str] = None,
    sort_by: Optional[str] = None,
) -> list[dict]:
    """
    Get products from the catalog with optional filtering.

    Args:
        category: Filter by product category
        max_price: Maximum price filter
        min_price: Minimum price filter
        search_term: Search in product name and description

    Returns:
        List of product dictionaries matching the filters
    """
    try:
        products = CATALOG.copy()
        
        # Ensure we have a valid list
        if not isinstance(products, list):
            logger = logging.getLogger("commerce")
            logger.error(f"CATALOG is not a list: {type(products)}")
            return []

        # Validate all products have required fields
        validated_products = []
        for product in products:
            if _validate_product(product):
                validated_products.append(product)
            else:
                logger = logging.getLogger("commerce")
                logger.warning(f"Skipping invalid product: {product.get('id', 'unknown')}")
        
        products = validated_products
        
        if category:
            category = str(category).strip().lower()
            products = [p for p in products if p.get("category", "").lower() == category]

        if max_price is not None:
            try:
                max_price = float(max_price)
                products = [p for p in products if p.get("price", 0) <= max_price]
            except (ValueError, TypeError):
                logger = logging.getLogger("commerce")
                logger.warning(f"Invalid max_price: {max_price}")

        if min_price is not None:
            try:
                min_price = float(min_price)
                products = [p for p in products if p.get("price", 0) >= min_price]
            except (ValueError, TypeError):
                logger = logging.getLogger("commerce")
                logger.warning(f"Invalid min_price: {min_price}")

        if search_term:
            try:
                term_lower = search_term.lower().strip()
                if not term_lower:
                    return products
                
                # Simple and robust matching
                def matches_product(product: dict) -> bool:
                    """Check if product matches search term."""
                    try:
                        name_lower = product.get("name", "").lower()
                        desc_lower = product.get("description", "").lower()
                        category_lower = product.get("category", "").lower()
                        
                        # Exact substring match
                        if term_lower in name_lower or term_lower in desc_lower:
                            return True
                        
                        # Word-based matching
                        search_words = term_lower.split()
                        for word in search_words:
                            if len(word) > 2:  # Only check significant words
                                if word in name_lower or word in desc_lower or word in category_lower:
                                    return True
                        
                        # Handle plural/singular variations
                        if term_lower.endswith('s') and len(term_lower) > 3:
                            singular = term_lower[:-1]
                            if singular in name_lower or singular in desc_lower:
                                return True
                        
                        # Handle common product variations (more flexible matching)
                        if 'camera' in term_lower or 'cam' in term_lower:
                            if 'camera' in name_lower or 'camera' in desc_lower or 'cam' in name_lower or 'cam' in desc_lower:
                                return True
                        if 'echo' in term_lower:
                            if 'echo' in name_lower or 'echo' in desc_lower:
                                return True
                        if 'dot' in term_lower:
                            if 'dot' in name_lower or 'dot' in desc_lower:
                                return True
                        if 'kindle' in term_lower:
                            if 'kindle' in name_lower or 'kindle' in desc_lower:
                                return True
                        if 'fire' in term_lower:
                            if 'fire' in name_lower or 'fire' in desc_lower:
                                return True
                        if 'doorbell' in term_lower:
                            if 'doorbell' in name_lower or 'doorbell' in desc_lower:
                                return True
                        if 'plug' in term_lower:
                            if 'plug' in name_lower or 'plug' in desc_lower:
                                return True
                        if 'blink' in term_lower:
                            if 'blink' in name_lower or 'blink' in desc_lower:
                                return True
                        if 'ring' in term_lower:
                            if 'ring' in name_lower or 'ring' in desc_lower:
                                return True
                        if 'wyze' in term_lower:
                            if 'wyze' in name_lower or 'wyze' in desc_lower:
                                return True
                        
                        return False
                    except Exception as e:
                        logger = logging.getLogger("commerce")
                        logger.warning(f"Error matching product: {e}")
                        return False
                
                products = [p for p in products if matches_product(p)]
            except Exception as e:
                logger = logging.getLogger("commerce")
                logger.error(f"Error in search_term filtering: {e}", exc_info=True)
                # Return all products if search fails
                return products

        # Apply sorting if specified
        if sort_by:
            sort_by = str(sort_by).strip().lower()
            if sort_by == "price_asc" or sort_by == "price_low_to_high":
                products.sort(key=lambda p: p.get("price", 0))
            elif sort_by == "price_desc" or sort_by == "price_high_to_low":
                products.sort(key=lambda p: p.get("price", 0), reverse=True)
            elif sort_by == "rating_desc" or sort_by == "rating_high_to_low":
                products.sort(key=lambda p: p.get("rating", 0), reverse=True)
            elif sort_by == "name_asc" or sort_by == "name_a_to_z":
                products.sort(key=lambda p: p.get("name", "").lower())
            elif sort_by == "name_desc" or sort_by == "name_z_to_a":
                products.sort(key=lambda p: p.get("name", "").lower(), reverse=True)

        # Final validation - ensure all returned products have all fields with proper types
        final_products = []
        for product in products:
            try:
                # Ensure all fields are present and valid
                validated_product = {
                    "id": str(product.get("id", "")),
                    "name": str(product.get("name", "Unknown Product")),
                    "description": str(product.get("description", "")),
                    "price": int(product.get("price", 0)),
                    "currency": str(product.get("currency", "INR")),
                    "category": str(product.get("category", "")),
                    "image_url": str(product.get("image_url", "https://picsum.photos/300/300?random=99")),
                    "rating": float(product.get("rating", 0.0)),
                    "reviews": int(product.get("reviews", 0)),
                }
                # Only add if all critical fields are valid
                if validated_product["id"] and validated_product["name"] != "Unknown Product" and validated_product["price"] > 0:
                    final_products.append(validated_product)
            except Exception as e:
                logger = logging.getLogger("commerce")
                logger.warning(f"Error validating product {product.get('id', 'unknown')}: {e}")
                continue
        
        return final_products
    except Exception as e:
        logger = logging.getLogger("commerce")
        logger.error(f"Error in get_products: {e}", exc_info=True)
        # Return empty list on error to prevent crashes
        return []


def create_order(product_id: str, quantity: int = 1) -> dict:
    """
    Create an order for a product.

    Args:
        product_id: The ID of the product to order
        quantity: The quantity to order (default: 1)

    Returns:
        Order dictionary with order details

    Raises:
        ValueError: If product_id is not found in catalog
    """
    # Find the product
    product = None
    for p in CATALOG:
        if p["id"] == product_id:
            product = p
            break

    if not product:
        raise ValueError(f"Product with ID '{product_id}' not found")

    # Calculate totals
    unit_amount = product["price"]
    total = unit_amount * quantity

    # Create order
    order = {
        "id": str(uuid4()),
        "items": [
            {
                "product_id": product_id,
                "product_name": product["name"],
                "quantity": quantity,
                "unit_amount": unit_amount,
                "currency": product["currency"],
            }
        ],
        "total": total,
        "currency": product["currency"],
        "status": "CONFIRMED",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    # Load existing orders and append
    orders = _load_orders()
    orders.append(order)
    _save_orders(orders)

    return order


def get_last_order() -> Optional[dict]:
    """Get the most recent order."""
    orders = _load_orders()
    if orders:
        return orders[-1]
    return None


def get_all_orders() -> list[dict]:
    """Get all orders."""
    return _load_orders()


def _load_cart() -> list[dict]:
    """Load cart from JSON file, creating it if it doesn't exist."""
    if os.path.exists(CART_FILE):
        try:
            with open(CART_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure it's a list
                if isinstance(data, list):
                    return data
                return []
        except (json.JSONDecodeError, IOError, OSError) as e:
            logger = logging.getLogger("commerce")
            logger.warning(f"Error loading cart file: {e}")
            return []
    return []


def _save_cart(cart: list[dict]) -> None:
    """Save cart to JSON file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(CART_FILE) if os.path.dirname(CART_FILE) else ".", exist_ok=True)
        with open(CART_FILE, "w", encoding="utf-8") as f:
            json.dump(cart, f, indent=2, ensure_ascii=False)
    except (IOError, OSError) as e:
        logger = logging.getLogger("commerce")
        logger.error(f"Error saving cart file: {e}")
        raise


def add_to_cart(product_id: str, quantity: int = 1) -> dict:
    """
    Add a product to the shopping cart.
    
    Args:
        product_id: The ID of the product to add
        quantity: The quantity to add (default: 1)
    
    Returns:
        Updated cart dictionary
    """
    # Find the product
    product = None
    for p in CATALOG:
        if p["id"] == product_id:
            product = p
            break
    
    if not product:
        raise ValueError(f"Product with ID '{product_id}' not found")
    
    # Load existing cart
    cart = _load_cart()
    
    # Check if product already in cart
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            _save_cart(cart)
            return {"cart": cart, "message": f"Updated quantity of {product['name']} in cart"}
    
    # Add new item to cart
    cart.append({
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_amount": product["price"],
        "currency": product["currency"],
    })
    _save_cart(cart)
    return {"cart": cart, "message": f"Added {quantity}x {product['name']} to cart"}


def get_cart() -> list[dict]:
    """Get the current shopping cart."""
    return _load_cart()


def update_cart_quantity(product_id: str, quantity: int) -> dict:
    """
    Update the quantity of a product in the shopping cart.
    
    Args:
        product_id: The ID of the product to update
        quantity: The new quantity (must be >= 1)
    
    Returns:
        Updated cart dictionary
    
    Raises:
        ValueError: If product_id is not found in cart or quantity is invalid
    """
    if quantity < 1:
        raise ValueError("Quantity must be at least 1")
    
    cart = _load_cart()
    
    # Find the item in cart
    item_found = False
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] = quantity
            item_found = True
            break
    
    if not item_found:
        raise ValueError(f"Product with ID '{product_id}' not found in cart")
    
    _save_cart(cart)
    return {"cart": cart, "message": f"Updated quantity to {quantity}"}


def remove_from_cart(product_id: str) -> dict:
    """
    Remove a product from the shopping cart.
    
    Args:
        product_id: The ID of the product to remove
    
    Returns:
        Updated cart dictionary
    """
    cart = _load_cart()
    cart = [item for item in cart if item["product_id"] != product_id]
    _save_cart(cart)
    return {"cart": cart, "message": "Item removed from cart"}


def clear_cart() -> dict:
    """Clear the entire shopping cart."""
    _save_cart([])
    return {"cart": [], "message": "Cart cleared"}


def checkout_cart() -> dict:
    """
    Checkout the cart - create an order from all cart items and clear the cart.
    
    Returns:
        Order dictionary
    """
    cart = _load_cart()
    if not cart:
        raise ValueError("Cart is empty")
    
    # Calculate total
    total = sum(item["unit_amount"] * item["quantity"] for item in cart)
    currency = cart[0]["currency"] if cart else "INR"
    
    # Create order
    order = {
        "id": str(uuid4()),
        "items": cart.copy(),
        "total": total,
        "currency": currency,
        "status": "CONFIRMED",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    
    # Save order
    orders = _load_orders()
    orders.append(order)
    _save_orders(orders)
    
    # Clear cart
    clear_cart()
    
    return order


def find_product_by_name(product_name: str) -> Optional[dict]:
    """
    Find a product by name (case-insensitive, partial match).

    Args:
        product_name: The product name or partial name to search for

    Returns:
        Product dictionary if found, None otherwise
    """
    if not product_name:
        return None
        
    name_lower = product_name.lower().strip()
    
    # Try exact match first
    for product in CATALOG:
        if product["name"].lower() == name_lower:
            return product
    
    # Try partial match - check if search term is contained in product name
    for product in CATALOG:
        product_name_lower = product["name"].lower()
        if name_lower in product_name_lower:
            return product
    
    # Try reverse partial match - check if product name key words are in search term
    for product in CATALOG:
        product_name_lower = product["name"].lower()
        # Extract main words (remove common words like "the", "a", numbers in parentheses)
        product_key_words = [
            word for word in product_name_lower.split() 
            if word not in ["the", "a", "an", "and", "or"] 
            and not (word.startswith("(") and word.endswith(")"))
        ]
        # Check if all key words from product are in the search term
        if all(word in name_lower for word in product_key_words if len(word) > 2):
            return product
    
    # Try matching key words - if at least 2 significant words match
    name_words = set(word for word in name_lower.split() if len(word) > 2)
    best_match = None
    best_score = 0
    
    for product in CATALOG:
        product_words = set(
            word for word in product["name"].lower().split() 
            if len(word) > 2 and word not in ["the", "a", "an", "and", "or"]
            and not (word.startswith("(") and word.endswith(")"))
        )
        # Calculate match score
        common_words = name_words & product_words
        if len(common_words) >= 2:
            score = len(common_words)
            if score > best_score:
                best_score = score
                best_match = product
    
    return best_match

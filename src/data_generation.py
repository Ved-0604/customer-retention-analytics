"""
Customer Retention & Churn Analytics Platform - Synthetic Data Generator
========================================================================
Generates a realistic, highly consistent relational e-commerce dataset exceeding:
- 10,000+ unique customers
- 100,000+ orders / transactions
- 10+ product categories
- 2-year longitudinal span (2024-01-01 through 2025-12-31)

Relational Tables Produced:
1. marketing_channels.csv
2. customers.csv
3. products.csv
4. orders.csv
5. order_items.csv
6. payments.csv

Behavioral & Statistical Mechanics:
- Pareto (80/20) repeat purchase distribution (one-time vs power buyers).
- Realistic seasonal surge during Q4 holidays (Black Friday / Cyber Monday).
- Realistic discount dependency and churn dynamics (90-day inactivity).
- Strict referential integrity, positive unit economics, and penny-exact financial reconciliation.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from faker import Faker

# Handle imports whether executed directly or as module
try:
    from src.config import RAW_DATA_DIR, analytics_config
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from src.config import RAW_DATA_DIR, analytics_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def generate_marketing_channels() -> pd.DataFrame:
    """Generate acquisition marketing channels."""
    channels_data = [
        {"channel_id": 1, "channel_name": "Organic Search", "channel_type": "Inbound", "avg_cpa": 12.50},
        {"channel_id": 2, "channel_name": "Paid Search (Google Ads)", "channel_type": "Paid", "avg_cpa": 48.00},
        {"channel_id": 3, "channel_name": "Paid Social (Meta / TikTok)", "channel_type": "Paid", "avg_cpa": 55.00},
        {"channel_id": 4, "channel_name": "Email Marketing", "channel_type": "Owned", "avg_cpa": 4.20},
        {"channel_id": 5, "channel_name": "Affiliate Partners", "channel_type": "Referral", "avg_cpa": 28.50},
        {"channel_id": 6, "channel_name": "Influencer Campaigns", "channel_type": "Paid", "avg_cpa": 62.00},
        {"channel_id": 7, "channel_name": "Direct / Word of Mouth", "channel_type": "Direct", "avg_cpa": 0.00},
    ]
    df = pd.DataFrame(channels_data)
    logger.info("Generated %d marketing channels.", len(df))
    return df


def generate_products() -> pd.DataFrame:
    """Generate 120 products across 12 distinct categories with realistic COGS and margins."""
    categories_catalog = {
        "Electronics": (45.0, 599.0, 0.65),           # (min_price, max_price, cogs_ratio)
        "Apparel & Fashion": (18.0, 160.0, 0.40),
        "Home & Kitchen": (22.0, 280.0, 0.48),
        "Beauty & Personal Care": (12.0, 85.0, 0.35),
        "Sports & Outdoors": (25.0, 320.0, 0.50),
        "Books & Media": (9.0, 45.0, 0.45),
        "Health & Wellness": (15.0, 95.0, 0.38),
        "Toys & Games": (14.0, 110.0, 0.42),
        "Office Products": (8.0, 150.0, 0.45),
        "Automotive": (20.0, 220.0, 0.55),
        "Pet Supplies": (11.0, 125.0, 0.45),
        "Jewelry & Watches": (35.0, 450.0, 0.30),
    }

    product_names = {
        "Electronics": ["Wireless Noise-Canceling Headphones", "Smart Fitness Watch", "Ultra-Slim 4K Monitor", "Bluetooth Portable Speaker", "USB-C Multiport Hub", "Mechanical Gaming Keyboard", "Ergonomic Wireless Mouse", "1080p HD Webcam", "Wireless Fast Charger Pad", "Smart Home Voice Assistant"],
        "Apparel & Fashion": ["Classic Oxford Cotton Shirt", "Slim-Fit Stretch Denim Jeans", "Merino Wool Crewneck Sweater", "Waterproof Trail Running Jacket", "Breathable Athletic Joggers", "Premium Leather Dress Belt", "Casual Canvas Sneakers", "UV-Protection Sunglasses", "Everyday Crew Socks (6-Pack)", "Thermal Fleece Half-Zip"],
        "Home & Kitchen": ["Stainless Steel Cookware Set (10-Pc)", "Cast Iron Dutch Oven 6-Qt", "Programmable Drip Coffee Maker", "High-Speed Countertop Blender", "Memory Foam Pillow Pair", "Egyptian Cotton Bed Sheets", "Aroma Essential Oil Diffuser", "LED Dimmable Desk Lamp", "Non-Stick Ceramic Frying Pan", "Bamboo Kitchen Cutting Board Set"],
        "Beauty & Personal Care": ["Hydrating Hyaluronic Acid Serum", "Vitamin C Brightening Moisturizer", "Gentle Foaming Daily Cleanser", "Repairing Keratin Hair Mask", "Organic Argan Facial Oil", "Mineral Broad-Spectrum Sunscreen SPF50", "Exfoliating AHA/BHA Toner", "Botanical Body Wash 16oz", "Sonic Vibrating Toothbrush", "Shea Butter Hand Cream"],
        "Sports & Outdoors": ["Adjustable Dumbbell Pair 50lb", "Anti-Tear Yoga Mat with Strap", "Insulated Stainless Steel Bottle 32oz", "Ultralight 2-Person Camping Tent", "Trekking Poles Carbon Fiber", "High-Density Foam Roller", "Resistance Exercise Bands Set", "Quick-Dry Microfiber Camp Towel", "Waterproof LED Headlamp", "Compact Bike Repair Multi-Tool"],
        "Books & Media": ["Modern Data Analytics in Practice", "Product Strategy for Digital Era", "The Behavioral Psychology of Habits", "Machine Learning Systems Design", "Financial Freedom Playbook", "World Architecture Illustrated", "Culinary Fundamentals & Recipes", "Mindfulness and Mental Resilience", "History of Scientific Revolutions", "Creative Thinking Workshop"],
        "Health & Wellness": ["Wild Alaskan Omega-3 Fish Oil", "Grass-Fed Whey Protein Powder 2lb", "Daily Multi-Vitamin & Mineral Complex", "Plant-Based Organic Supergreens", "Melatonin Sleep Aid Gummies", "Pure Magnesium Glycinate Tablets", "Turmeric Curcumin Anti-Inflammatory", "Probiotic 50 Billion CFU", "Collagen Peptides Powder 16oz", "Electrolyte Hydration Drink Mix"],
        "Toys & Games": ["Architectural Building Blocks Set", "Strategy Board Game: Empires", "Magnetic STEM Tiles (100 Pcs)", "Remote Control Racing Drone", "Wooden Montessori Puzzle Box", "Classic Family Trivia Night", "Interactive Robot Coding Kit", "Artisan Clay Craft Sculpting Kit", "Card Game: Tactical Blitz", "Children Illustrated Storybook Library"],
        "Office Products": ["Ergonomic Lumbar Support Cushion", "Dual-Arm Heavy Duty Monitor Mount", "Full-Desk Leatherette Mousepad", "Document Shredder Cross-Cut", "Gel Ink Retractable Pens (12-Pack)", "Adjustable Laptop Standing Riser", "Steel Mesh Desktop Organizer", "Dry Erase Magnetic Whiteboard", "Noise-Dampening Acoustic Desk Divider", "Thermal Label Maker Printer"],
        "Automotive": ["Digital Tire Pressure Gauge & Inflator", "OBD2 Bluetooth Diagnostic Scanner", "Emergency Roadside Assistance Kit", "Microfiber Car Detailing Towels (12-Pack)", "Heavy-Duty All-Weather Floor Mats", "Universal Magnetic Phone Mount", "12V Portable Car Vacuum Cleaner", "Ceramic Coating Paint Sealant", "Windshield Sunshade Reflective", "Jump Starter Power Bank 1500A"],
        "Pet Supplies": ["Orthopedic Memory Foam Dog Bed", "Grain-Free Salmon Dog Food 25lb", "Self-Cleaning Covered Cat Litter Box", "Multi-Level Sisal Cat Scratching Tree", "Interactive Laser Pet Toy", "Durable Rubber Chew Bone", "Natural Clumping Odor-Control Litter", "Stainless Steel Anti-Vomit Pet Bowls", "Retractable Dog Walking Leash 16ft", "Gentle De-Shedding Grooming Brush"],
        "Jewelry & Watches": ["Minimalist Solar Chronograph Watch", "Sterling Silver Herringbone Necklace", "14k Gold-Plated Huggie Earrings", "Classic Leather Strap Dress Watch", "Cubic Zirconia Tennis Bracelet", "Titanium Matte Finish Band Ring", "Natural Freshwater Pearl Pendant", "Diver 200M Automatic Stainless Watch", "Braided Italian Leather Cuff", "Personalized Initial Signet Ring"],
    }

    products = []
    prod_counter = 1
    np.random.seed(analytics_config.random_seed)

    for cat_name, (min_p, max_p, cogs_ratio) in categories_catalog.items():
        names = product_names[cat_name]
        for name in names:
            base_price = round(float(np.random.uniform(min_p, max_p)), 2)
            cogs = round(base_price * cogs_ratio * np.random.uniform(0.92, 1.05), 2)
            # Ensure positive margin
            if cogs >= base_price:
                cogs = round(base_price * 0.70, 2)
                
            products.append({
                "product_id": f"PROD-{prod_counter:04d}",
                "product_name": name,
                "category": cat_name,
                "base_price": base_price,
                "cogs": cogs,
                "is_active": True,
            })
            prod_counter += 1

    df = pd.DataFrame(products)
    logger.info("Generated %d products across %d categories.", len(df), df["category"].nunique())
    return df


def generate_customers(num_customers: int = 15000) -> pd.DataFrame:
    """Generate customer demographics with realistic age, channels, and cohort signup dates."""
    fake = Faker()
    Faker.seed(analytics_config.random_seed)
    np.random.seed(analytics_config.random_seed)

    logger.info("Generating %d synthetic customers...", num_customers)

    # US State and Major City distribution
    us_locations = [
        ("New York", "NY"), ("Los Angeles", "CA"), ("Chicago", "IL"), ("Houston", "TX"),
        ("Phoenix", "AZ"), ("Philadelphia", "PA"), ("San Antonio", "TX"), ("San Diego", "CA"),
        ("Dallas", "TX"), ("Austin", "TX"), ("San Jose", "CA"), ("Seattle", "WA"),
        ("Denver", "CO"), ("Boston", "MA"), ("Atlanta", "GA"), ("Miami", "FL"),
        ("Minneapolis", "MN"), ("Portland", "OR"), ("Charlotte", "NC"), ("Nashville", "TN")
    ]

    loc_indices = np.random.choice(len(us_locations), size=num_customers)
    cities = [us_locations[i][0] for i in loc_indices]
    states = [us_locations[i][1] for i in loc_indices]

    # Acquisition channel weights (Paid Search & Social largest, followed by Organic & Email)
    channel_ids = [1, 2, 3, 4, 5, 6, 7]
    channel_probs = [0.22, 0.26, 0.21, 0.13, 0.08, 0.05, 0.05]
    acq_channels = np.random.choice(channel_ids, size=num_customers, p=channel_probs)

    # Customer signup dates across 2024-01-01 to 2025-11-15
    start_dt = datetime.strptime("2024-01-01", "%Y-%m-%d")
    end_dt = datetime.strptime("2025-11-15", "%Y-%m-%d")
    days_range = (end_dt - start_dt).days

    # Slight growth trajectory over time (more customers acquire in later quarters)
    linear_bias = np.random.power(a=1.30, size=num_customers)
    signup_days = (linear_bias * days_range).astype(int)
    signup_dates = [start_dt + timedelta(days=int(d)) for d in signup_days]

    # Demographics
    genders = np.random.choice(["Female", "Male", "Non-Binary"], size=num_customers, p=[0.52, 0.45, 0.03])
    # Age: Normal distribution centered at 35, bounded between 18 and 75
    ages = np.clip(np.random.normal(loc=35, scale=11, size=num_customers).astype(int), 18, 75)

    customers = []
    for i in range(num_customers):
        cust_id = f"CUST-{i+1:05d}"
        first_name = fake.first_name_female() if genders[i] == "Female" else fake.first_name_male()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}.{i+1}@example.com".replace("'", "")
        
        customers.append({
            "customer_id": cust_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "gender": genders[i],
            "age": ages[i],
            "city": cities[i],
            "state": states[i],
            "country": "United States",
            "signup_date": signup_dates[i].strftime("%Y-%m-%d"),
            "acquisition_channel_id": acq_channels[i],
        })

    df = pd.DataFrame(customers)
    logger.info("Successfully generated %d customers.", len(df))
    return df


def generate_orders_and_items(
    customers_df: pd.DataFrame,
    products_df: pd.DataFrame,
    target_orders: int = 105000
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Simulates longitudinal transaction history with realistic e-commerce mechanics:
    - Power-law / Pareto repeat frequency distribution
    - Seasonality surge in Q4
    - Churn behavior and inactivity drop-off
    - Line-item generation and penny-exact financial reconciliation
    """
    np.random.seed(analytics_config.random_seed)
    logger.info("Simulating transactions targeting >= %d orders...", target_orders)

    num_customers = len(customers_df)
    cust_ids = customers_df["customer_id"].values
    signup_dates = pd.to_datetime(customers_df["signup_date"]).values
    acq_channel_map = dict(zip(customers_df["customer_id"], customers_df["acquisition_channel_id"]))

    # 1. Behavioral archetypes (Pareto distribution):
    # - One-time buyers: ~45% (Standard e-commerce benchmark)
    # - Low repeat (2-4 orders): ~28%
    # - Medium repeat (5-11 orders): ~17%
    # - High repeat / Champions (12-32 orders): ~10%
    archetypes = np.random.choice(
        ["one_time", "low_repeat", "medium_repeat", "vip"],
        size=num_customers,
        p=[0.45, 0.28, 0.17, 0.10]
    )

    # Assign order counts per customer based on archetype
    order_counts = np.zeros(num_customers, dtype=int)
    order_counts[archetypes == "one_time"] = 1
    order_counts[archetypes == "low_repeat"] = np.random.randint(2, 5, size=(archetypes == "low_repeat").sum())
    order_counts[archetypes == "medium_repeat"] = np.random.randint(5, 12, size=(archetypes == "medium_repeat").sum())
    order_counts[archetypes == "vip"] = np.random.randint(14, 35, size=(archetypes == "vip").sum())

    # Adjust counts to comfortably exceed target_orders (e.g. >= 105,000)
    total_assigned = order_counts.sum()
    if total_assigned < target_orders:
        extra_needed = target_orders - total_assigned
        repeat_mask = np.where(order_counts > 1)[0]
        extra_alloc = np.random.choice(repeat_mask, size=extra_needed)
        for idx in extra_alloc:
            order_counts[idx] += 1

    logger.info("Allocated %d total orders across %d customers.", order_counts.sum(), num_customers)

    study_end_dt = datetime.strptime("2025-12-31 23:59:59", "%Y-%m-%d %H:%M:%S")

    order_records = []
    order_item_records = []
    payment_records = []

    prod_ids = products_df["product_id"].values
    prod_prices = dict(zip(products_df["product_id"], products_df["base_price"]))
    prod_cogs = dict(zip(products_df["product_id"], products_df["cogs"]))
    prod_categories = dict(zip(products_df["product_id"], products_df["category"]))

    # Category popularity weights
    cat_weights = {
        "Apparel & Fashion": 0.16, "Beauty & Personal Care": 0.14, "Electronics": 0.12,
        "Home & Kitchen": 0.12, "Health & Wellness": 0.10, "Sports & Outdoors": 0.08,
        "Pet Supplies": 0.07, "Office Products": 0.06, "Toys & Games": 0.05,
        "Books & Media": 0.04, "Jewelry & Watches": 0.03, "Automotive": 0.03
    }
    prod_weights = np.array([cat_weights[prod_categories[p]] for p in prod_ids])
    prod_weights = prod_weights / prod_weights.sum()

    payment_methods_pool = ["Credit Card", "PayPal", "Apple Pay", "Debit Card", "Buy Now Pay Later"]
    payment_method_probs = [0.48, 0.24, 0.14, 0.09, 0.05]

    order_counter = 1
    item_counter = 1

    # Discount tiers: High discount propensity for specific users (bargain hunters)
    high_discount_propensity = np.random.binomial(1, 0.24, size=num_customers)

    # Churn probability for repeat customers (stops repeat buying prematurely)
    # Higher for discount hunters and paid social / affiliate channels
    churn_decisions = np.random.random(size=num_customers)

    for c_idx in range(num_customers):
        c_id = cust_ids[c_idx]
        c_signup = pd.Timestamp(signup_dates[c_idx]).to_pydatetime()
        n_orders = order_counts[c_idx]
        is_discount_hunter = bool(high_discount_propensity[c_idx])
        c_channel = acq_channel_map[c_id]

        # Calculate customer churn propensity:
        churn_threshold = 0.38 if is_discount_hunter else 0.25
        if c_channel in [3, 5]: # Paid Social, Affiliate
            churn_threshold += 0.08
        will_churn_early = (churn_decisions[c_idx] < churn_threshold) and (n_orders > 1)

        # If customer churns early, cap their effective orders to between 2 and max(2, n_orders // 2)
        if will_churn_early:
            effective_orders = int(np.random.randint(2, max(3, n_orders // 2 + 1)))
        else:
            effective_orders = n_orders

        # Calculate time span available between signup and end date
        days_avail = max(1, (study_end_dt - c_signup).days)
        
        # If churned early, restrict purchases to the first portion of their tenure so they are inactive > 90 days
        if will_churn_early:
            active_window_days = max(10, days_avail - int(np.random.randint(95, 260)))
        else:
            active_window_days = days_avail

        # Distribute orders across active window
        if effective_orders == 1:
            order_days_offset = [float(np.random.uniform(0, min(3, days_avail)))]
        else:
            # Generate sorted random offsets across the active window
            raw_offsets = np.sort(np.random.uniform(0, active_window_days, size=effective_orders))
            # First order is close to signup
            raw_offsets[0] = float(np.random.uniform(0, min(2, days_avail)))
            order_days_offset = raw_offsets

        for ord_seq in range(effective_orders):
            curr_time = c_signup + timedelta(days=float(order_days_offset[ord_seq]), hours=float(np.random.uniform(7, 23)))
            if curr_time > study_end_dt:
                continue

            # Order Status distribution:
            # 87% Delivered, 5% Completed, 4% Cancelled, 2.5% Returned, 1.5% Refunded
            status_rand = np.random.random()
            if status_rand < 0.87:
                status = "Delivered"
            elif status_rand < 0.92:
                status = "Completed"
            elif status_rand < 0.96:
                status = "Cancelled"
            elif status_rand < 0.985:
                status = "Returned"
            else:
                status = "Refunded"

            order_id = f"ORD-{order_counter:07d}"
            order_date_str = curr_time.strftime("%Y-%m-%d %H:%M:%S")

            # Determine number of line items (1 to 4 items)
            num_items = np.random.choice([1, 2, 3, 4], p=[0.58, 0.27, 0.11, 0.04])
            selected_prod_indices = np.random.choice(len(prod_ids), size=num_items, replace=False, p=prod_weights)

            gross_order_total = 0.0
            order_items_temp = []

            for p_idx in selected_prod_indices:
                p_id = prod_ids[p_idx]
                qty = int(np.random.choice([1, 2, 3], p=[0.82, 0.14, 0.04]))
                unit_price = prod_prices[p_id]
                unit_cost = prod_cogs[p_id]
                item_total = round(unit_price * qty, 2)
                gross_order_total += item_total

                order_items_temp.append({
                    "order_item_id": f"ITEM-{item_counter:08d}",
                    "order_id": order_id,
                    "product_id": p_id,
                    "quantity": qty,
                    "unit_price": unit_price,
                    "unit_cost": unit_cost,
                    "total_item_price": item_total,
                })
                item_counter += 1

            gross_order_total = round(gross_order_total, 2)

            # Discount calculation:
            if is_discount_hunter:
                disc_rate = float(np.random.choice([0.15, 0.20, 0.25, 0.30], p=[0.3, 0.35, 0.25, 0.10]))
            else:
                disc_rate = float(np.random.choice([0.0, 0.05, 0.10, 0.15], p=[0.60, 0.20, 0.15, 0.05]))

            discount_amount = round(gross_order_total * disc_rate, 2)
            
            # Shipping policy: Free shipping if gross > $75, else $5.99
            shipping_fee = 0.0 if gross_order_total >= 75.0 else 5.99
            
            # Net amount billed to customer
            net_amount = round(gross_order_total - discount_amount + shipping_fee, 2)

            # Order Record
            order_records.append({
                "order_id": order_id,
                "customer_id": c_id,
                "order_date": order_date_str,
                "order_status": status,
                "gross_amount": gross_order_total,
                "discount_amount": discount_amount,
                "shipping_fee": shipping_fee,
                "net_amount": net_amount,
                "acquisition_channel_id": c_channel,
            })
            order_item_records.extend(order_items_temp)

            # Payment Record
            pay_method = np.random.choice(payment_methods_pool, p=payment_method_probs)
            pay_status = "Failed" if status == "Cancelled" else ("Refunded" if status in ["Returned", "Refunded"] else "Success")
            
            payment_records.append({
                "payment_id": f"PAY-{order_counter:07d}",
                "order_id": order_id,
                "payment_method": pay_method,
                "payment_status": pay_status,
                "payment_date": order_date_str,
                "amount": net_amount,
            })

            order_counter += 1

    orders_df = pd.DataFrame(order_records)
    order_items_df = pd.DataFrame(order_item_records)
    payments_df = pd.DataFrame(payment_records)

    logger.info("Simulation complete: %d orders, %d order items, %d payments.",
                len(orders_df), len(order_items_df), len(payments_df))
    return orders_df, order_items_df, payments_df


def save_datasets(
    channels_df: pd.DataFrame,
    customers_df: pd.DataFrame,
    products_df: pd.DataFrame,
    orders_df: pd.DataFrame,
    order_items_df: pd.DataFrame,
    payments_df: pd.DataFrame,
    output_dir: Path = RAW_DATA_DIR
) -> None:
    """Save all generated relational datasets to CSV with standard quoting and encoding."""
    output_dir.mkdir(parents=True, exist_ok=True)

    datasets = {
        "marketing_channels.csv": channels_df,
        "customers.csv": customers_df,
        "products.csv": products_df,
        "orders.csv": orders_df,
        "order_items.csv": order_items_df,
        "payments.csv": payments_df,
    }

    for filename, df in datasets.items():
        file_path = output_dir / filename
        df.to_csv(file_path, index=False)
        logger.info("Saved %s: %d rows (%.2f MB)", filename, len(df), file_path.stat().st_size / (1024 * 1024))


def run_pipeline() -> None:
    """Execute complete data generation pipeline."""
    logger.info("=== Starting Synthetic Data Generation Pipeline ===")
    channels_df = generate_marketing_channels()
    products_df = generate_products()
    customers_df = generate_customers(num_customers=analytics_config.target_customers)
    orders_df, order_items_df, payments_df = generate_orders_and_items(
        customers_df=customers_df,
        products_df=products_df,
        target_orders=analytics_config.target_transactions
    )
    save_datasets(channels_df, customers_df, products_df, orders_df, order_items_df, payments_df)
    logger.info("=== Data Generation Pipeline Finished Successfully ===")


if __name__ == "__main__":
    run_pipeline()

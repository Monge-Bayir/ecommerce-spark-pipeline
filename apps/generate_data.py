import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

NUM_CUSTOMERS = 100_000
NUM_PRODUCTS = 5_000
NUM_ORDERS = 1_000_000
NUM_PAYMENTS = NUM_ORDERS


FIRST_NAMES = [
    "Alex", "John", "Anna", "Maria", "Michael",
    "Daniel", "David", "Emma", "Olivia", "James",
    "Robert", "Sophia", "William", "Emily", "Thomas"
]

LAST_NAMES = [
    "Smith", "Brown", "Johnson", "Ivanov", "Petrov",
    "Williams", "Jones", "Miller", "Davis", "Wilson",
    "Anderson", "Taylor", "Thomas", "Moore", "Martin"
]

COUNTRIES = [
    "Russia",
    "USA",
    "Germany",
    "France",
    "UK",
    "Canada",
    "Spain",
    "Italy",
    "Netherlands",
    "Poland",
]

CATEGORIES = [
    "Electronics",
    "Clothing",
    "Books",
    "Home",
    "Sports",
    "Beauty",
    "Toys",
    "Accessories",
]

PAYMENT_METHODS = [
    "card",
    "paypal",
    "apple_pay",
    "google_pay",
    "bank_transfer",
]

PAYMENT_STATUSES = [
    "paid",
    "pending",
    "failed",
    "refunded",
]


def random_date(start: datetime, end: datetime) -> str:
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return (start + timedelta(seconds=random_seconds)).strftime("%Y-%m-%d")


def random_name() -> str:
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


# ============================================================
# CUSTOMERS
# ============================================================

print("Generating customers...")

customers = []

with open(RAW_DIR / "customers.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "customer_id",
        "name",
        "email",
        "country",
        "registration_date",
    ])

    for customer_id in range(1, NUM_CUSTOMERS + 1):

        name = random_name()
        email = f"user{customer_id}@example.com"
        country = random.choice(COUNTRIES)
        registration_date = random_date(
            datetime(2024, 1, 1),
            datetime(2026, 6, 30),
        )

        # NULL email
        if random.random() < 0.01:
            email = ""

        # NULL country
        if random.random() < 0.005:
            country = ""

        writer.writerow([
            customer_id,
            name,
            email,
            country,
            registration_date,
        ])

        customers.append(customer_id)


# ============================================================
# PRODUCTS
# ============================================================

print("Generating products...")

product_names = [
    "Laptop",
    "Smartphone",
    "Headphones",
    "Keyboard",
    "Mouse",
    "Monitor",
    "T-Shirt",
    "Jeans",
    "Sneakers",
    "Backpack",
    "Book",
    "Desk",
    "Chair",
    "Football",
    "Basketball",
    "Camera",
    "Watch",
    "Tablet",
    "Game Console",
    "Coffee Machine",
]

with open(RAW_DIR / "products.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "product_id",
        "product_name",
        "category",
        "price",
    ])

    for product_id in range(1, NUM_PRODUCTS + 1):

        product_name = (
            f"{random.choice(product_names)} "
            f"Model-{product_id}"
        )

        category = random.choice(CATEGORIES)

        price = round(random.uniform(5, 2500), 2)

        # Иногда NULL цена
        if random.random() < 0.005:
            price = ""

        writer.writerow([
            product_id,
            product_name,
            category,
            price,
        ])


# ============================================================
# ORDERS
# ============================================================

print("Generating orders...")

order_start = datetime(2025, 1, 1)
order_end = datetime(2026, 9, 30)

with open(RAW_DIR / "orders.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "order_id",
        "customer_id",
        "product_id",
        "order_date",
        "quantity",
        "discount",
    ])

    for order_id in range(1, NUM_ORDERS + 1):

        customer_id = random.choice(customers)
        product_id = random.randint(1, NUM_PRODUCTS)

        order_date = random_date(order_start, order_end)

        quantity = random.randint(1, 5)

        discount = random.choice([
            0,
            0,
            0,
            5,
            10,
            15,
            20,
        ])

        # ==========================================
        # ГРЯЗНЫЕ ДАННЫЕ
        # ==========================================

        # 1. Неизвестный customer_id
        if random.random() < 0.003:
            customer_id = random.randint(
                NUM_CUSTOMERS + 1,
                NUM_CUSTOMERS + 1000,
            )

        # 2. Неизвестный product_id
        if random.random() < 0.003:
            product_id = random.randint(
                NUM_PRODUCTS + 1,
                NUM_PRODUCTS + 1000,
            )

        # 3. Отрицательное количество
        if random.random() < 0.002:
            quantity = -random.randint(1, 5)

        # 4. Нулевое количество
        if random.random() < 0.001:
            quantity = 0

        # 5. NULL quantity
        if random.random() < 0.001:
            quantity = ""

        # 6. NULL discount
        if random.random() < 0.003:
            discount = ""

        # 7. Битая дата
        if random.random() < 0.002:
            order_date = random.choice([
                "2026-99-99",
                "not-a-date",
                "2025-13-45",
                "",
            ])

        writer.writerow([
            order_id,
            customer_id,
            product_id,
            order_date,
            quantity,
            discount,
        ])

        # ==========================================
        # ДУБЛИКАТЫ
        # ==========================================

        if random.random() < 0.001:

            writer.writerow([
                order_id,
                customer_id,
                product_id,
                order_date,
                quantity,
                discount,
            ])


# ============================================================
# PAYMENTS
# ============================================================

print("Generating payments...")

with open(RAW_DIR / "payments.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "payment_id",
        "order_id",
        "payment_method",
        "payment_status",
        "payment_date",
    ])

    for payment_id in range(1, NUM_PAYMENTS + 1):

        order_id = payment_id

        payment_method = random.choice(PAYMENT_METHODS)
        payment_status = random.choice(PAYMENT_STATUSES)

        payment_date = random_date(
            datetime(2025, 1, 1),
            datetime(2026, 9, 30),
        )

        # NULL method
        if random.random() < 0.01:
            payment_method = ""

        # Некорректный статус
        if random.random() < 0.005:
            payment_status = "unknown"

        # Битая дата
        if random.random() < 0.002:
            payment_date = "invalid-date"

        writer.writerow([
            payment_id,
            order_id,
            payment_method,
            payment_status,
            payment_date,
        ])


print()
print("DONE!")
print(f"Files generated in: {RAW_DIR}")
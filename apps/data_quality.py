from pyspark.sql.functions import col, current_timestamp, current_date
from datetime import datetime
from pyspark.sql.functions import col, date_format, current_timestamp


def check_orders_quality(orders, customers, products):
    today_str = datetime.now().strftime("%Y-%m-%d")

    print('=== ORDERS DATA QUALITY ===')
    print(f'total_orders: {orders.count()}')

    # quantity
    null_quantity = orders.filter(col('quantity').isNull()).count()
    print(f'null_quantity: {null_quantity}')

    # невалидные: NULL ИЛИ <= 0
    invalid_quantity = orders.filter(
        col('quantity').isNull() | (col('quantity') <= 0)
    ).count()
    print(f'invalid_quantity: {invalid_quantity}')

    # order_date
    null_order_date = orders.filter(col('order_date').isNull()).count()
    print(f'null_order_date: {null_order_date}')

    # невалидные: в будущем (NULL уже посчитан отдельно)
    invalid_order_date = orders.filter(
        col("order_date") > today_str
    ).count()
    print(f'invalid_order_date: {invalid_order_date}')

    # заказы без клиента / продукта
    orders_without_customer = orders.join(
        customers, on='customer_id', how='left_anti'
    ).count()
    print(f'orders_without_customer: {orders_without_customer}')

    orders_without_product = orders.join(
        products, on='product_id', how='left_anti'
    ).count()
    print(f'orders_without_product: {orders_without_product}')


def cleanings_df_orders(orders, products, customers):
    today_str = datetime.now().strftime("%Y-%m-%d")

    orders_clean = (
        orders
        .join(customers, on='customer_id', how='inner')
        .join(products, on='product_id', how='inner')
        .filter(
            (col('quantity') > 0)
            & (col('order_date').isNotNull())
            & (col('order_date') <= today_str)
        )
    )
    return orders_clean
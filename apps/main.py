from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.functions import col, coalesce, lit, round
from data_quality import check_orders_quality, cleanings_df_orders


spark = (
    SparkSession
    .builder
    .appName('eccommerce-pipeline')
    .master('spark://spark-master:7077')
    .getOrCreate()
)
RAW_PATH = "file:///opt/spark/data/raw"
PROCESSED_PATH = "file:///opt/spark/data/processed"

print('=== SPARK STARTED ===')

customers = (
    spark.read
    .option('header', True)
    .option('inferSchema', True)
    .csv(f'{RAW_PATH}/customers.csv')
)

orders = (
    spark.read
    .option('header', True)
    .option('inferSchema', True)
    .csv(f'{RAW_PATH}/orders.csv')
)

payments = (
    spark.read
    .option('header', True)
    .option('inferSchema', True)
    .csv(f'{RAW_PATH}/payments.csv')
)

products = (
    spark.read
    .option('header', True)
    .option('inferSchema', True)
    .csv(f'{RAW_PATH}/products.csv')
)

orders.printSchema()
products.printSchema()
payments.printSchema()
customers.printSchema()

orders.createOrReplaceTempView('orders')
products.createOrReplaceTempView('products')
payments.createOrReplaceTempView('payments')
customers.createOrReplaceTempView('customers')


print('=== COUNTS ===')
print('customers:', customers.count())
print('orders:', orders.count())
print('payments:', payments.count())
print('products:', products.count())


print('=== CUSTOMERS ===')
print(customers.show(10, truncate=False))

print('=== PRODUCTS ===')
print(products.show(10, truncate=False))

print('=== ORDERS ===')
print(orders.show(10, truncate=False))

print('=== PAYMENTS ===')
print(orders.show(10, truncate=False))

check_orders_quality(orders, customers, products)

print('\n=== CLEAN ORDERS ===')
orders_clean = cleanings_df_orders(orders, products, customers)
orders_clean.show()
# orders_clean.explain('formatted')


print('\n=== ORDERS ENRICHED ===')
orders_enriched = orders_clean.withColumn(
    'revenue',
    round(col('quantity') * col('price') * (1 - coalesce(col('discount'), lit(0.0)) / 100), 2)
)
orders_enriched.show()


print('\n=== DAILY SALES ===')
daily_sales = orders_enriched.groupBy('order_date').agg(
    f.countDistinct('order_id').alias('orders_count'),
    f.countDistinct('customer_id').alias('unique_customers'),
    f.sum('revenue').alias('revenue'),
)
daily_sales = daily_sales.withColumn(
    'avg_order_value',
    f.round(f.col('revenue') / f.col('orders_count'), 2)
)
daily_sales.show()

print('\n=== CATEGORY SALES ===')
category_sales = orders_enriched.groupBy('category').agg(
    f.count('order_id').alias('orders_count'),
    f.countDistinct('customer_id').alias('unique_customers'),
    f.sum('quantity').alias('total_quantity'),
    f.sum('revenue').alias('revenue')
)
category_sales.show()

orders_enriched.printSchema()
print(orders_enriched.columns)

print('\n=== TOP PRODUCTS ===')
top_products = orders_enriched.groupBy('product_name').agg(
    f.round(f.sum('revenue'), 2).alias('revenue')
).orderBy(col('revenue').desc()).limit(20)
top_products.show()


print('\n=== WRITING FILES ===')
orders_clean.write.mode('overwrite').parquet(f'{PROCESSED_PATH}/orders_clean')
orders_enriched.write.mode('overwrite').parquet(f'{PROCESSED_PATH}/orders_enriched')
daily_sales.write.mode('overwrite').parquet(f'{PROCESSED_PATH}/daily_sales')
category_sales.write.mode('overwrite').parquet(f'{PROCESSED_PATH}/category_sales')
top_products.write.mode('overwrite').parquet(f'{PROCESSED_PATH}/top_products')


print('\n=== PARQUET FILES ===')
orders_clean_parquet = spark.read.parquet(f'{PROCESSED_PATH}/orders_clean')
orders_clean_parquet.show()
orders_clean_parquet.explain('formatted')


print('\n=== PARTITIONS ===')
print('orders:', orders_clean.rdd.getNumPartitions())

heavy_sales = (
    orders_enriched
    .groupBy("customer_id")
    .agg(
        f.sum("quantity").alias("total_quantity"),
        f.sum("revenue").alias("total_revenue"),
        f.countDistinct("product_id").alias("unique_products"),
        f.countDistinct("order_id").alias("orders_count")
    )
)

heavy_sales.explain("formatted")

heavy_sales.count()
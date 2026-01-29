-- BigQuery用スキーマ定義
-- データセット名: ecommerce (適宜変更してください)

-- 顧客テーブル
CREATE TABLE IF NOT EXISTS `ecommerce.customers` (
    customer_id INT64 NOT NULL,
    name STRING NOT NULL,
    email STRING NOT NULL,
    phone STRING,
    address STRING,
    city STRING,
    prefecture STRING,
    zip_code STRING,
    registration_date DATE NOT NULL
)
PARTITION BY registration_date
CLUSTER BY prefecture;

-- 商品テーブル
CREATE TABLE IF NOT EXISTS `ecommerce.products` (
    product_id INT64 NOT NULL,
    name STRING NOT NULL,
    category STRING NOT NULL,
    brand STRING,
    price NUMERIC(10, 2) NOT NULL,
    stock_quantity INT64 NOT NULL,
    description STRING,
    created_at DATE NOT NULL
)
PARTITION BY created_at
CLUSTER BY category;

-- 注文テーブル
CREATE TABLE IF NOT EXISTS `ecommerce.orders` (
    order_id INT64 NOT NULL,
    customer_id INT64 NOT NULL,
    order_date DATE NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL,
    status STRING NOT NULL,
    shipping_address STRING,
    payment_method STRING
)
PARTITION BY order_date
CLUSTER BY status, customer_id;

-- 注文明細テーブル
CREATE TABLE IF NOT EXISTS `ecommerce.order_items` (
    order_item_id INT64 NOT NULL,
    order_id INT64 NOT NULL,
    product_id INT64 NOT NULL,
    quantity INT64 NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL
)
PARTITION BY (SELECT order_date FROM `ecommerce.orders` WHERE orders.order_id = order_items.order_id)
CLUSTER BY order_id, product_id;


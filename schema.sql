-- Eコマース店舗データベーススキーマ

-- 顧客テーブル
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY, # 顧客ID
    name VARCHAR(100) NOT NULL, # 顧客名
    email VARCHAR(255) UNIQUE NOT NULL, # メールアドレス
    phone VARCHAR(20), # 電話番号
    address VARCHAR(255), # 住所
    city VARCHAR(50), # 市町村
    prefecture VARCHAR(20), # 都道府県
    zip_code VARCHAR(7), # 郵便番号（7桁、ハイフンなし）
    registration_date DATE NOT NULL # 登録日
);

-- 商品テーブル
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY, # 商品ID    
    name VARCHAR(200) NOT NULL, # 商品名
    category VARCHAR(50) NOT NULL,
    brand VARCHAR(100), # ブランド
    price DECIMAL(10, 2) NOT NULL, # 価格
    stock_quantity INTEGER NOT NULL DEFAULT 0, # 在庫数
    description TEXT, # 商品説明
    created_at DATE NOT NULL
);

-- 注文テーブル
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY, # 注文ID
    customer_id INTEGER NOT NULL, # 顧客ID
    order_date DATE NOT NULL, # 注文日
    total_amount DECIMAL(10, 2) NOT NULL, # 合計金額
    status VARCHAR(20) NOT NULL, -- 'pending', 'processing', 'shipped', 'delivered', 'cancelled'
    shipping_address VARCHAR(255), # 配送先住所
    payment_method VARCHAR(50), -- 'credit_card', 'bank_transfer', 'convenience_store', 'paypal'
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) # 顧客IDに外部キー制約
);

-- 注文明細テーブル
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY, # 注文明細ID
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);


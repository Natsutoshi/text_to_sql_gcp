# README

## Eコマース店舗 サンプルデータセット

text-to-SQLの学習用に作成したEコマース店舗のサンプルデータセットです。

### データセット概要

- **顧客（customers）**: 20件
- **商品（products）**: 20件
- **注文（orders）**: 20件
- **注文明細（order_items）**: 約40件

合計データサイズ: 約10-20KB（BigQuery無料枠の10GBストレージに十分収まります）

### テーブル構成

#### customers（顧客テーブル）
- `customer_id`: 顧客ID（主キー）
- `name`: 顧客名
- `email`: メールアドレス
- `phone`: 電話番号
- `address`: 住所
- `city`: 市区町村
- `prefecture`: 都道府県
- `zip_code`: 郵便番号（7桁、ハイフンなし）
- `registration_date`: 登録日

#### products（商品テーブル）
- `product_id`: 商品ID（主キー）
- `name`: 商品名
- `category`: カテゴリ（エレクトロニクス、ファッション、食品・飲料など）
- `brand`: ブランド名
- `price`: 価格
- `stock_quantity`: 在庫数
- `description`: 商品説明
- `created_at`: 登録日

### orders（注文テーブル）
- `order_id`: 注文ID（主キー）
- `customer_id`: 顧客ID（外部キー）
- `order_date`: 注文日
- `total_amount`: 合計金額
- `status`: ステータス（pending, processing, shipped, delivered, cancelled）
- `shipping_address`: 配送先住所
- `payment_method`: 支払い方法（credit_card, bank_transfer, convenience_store, paypal）

#### order_items（注文明細テーブル）
- `order_item_id`: 注文明細ID（主キー）
- `order_id`: 注文ID（外部キー）
- `product_id`: 商品ID（外部キー）
- `quantity`: 数量
- `unit_price`: 単価
- `subtotal`: 小計

### ファイル構成

```
.
├── schema.sql                    # データベーススキーマ定義
├── insert_customers.sql          # 顧客データのINSERT文
├── insert_products.sql           # 商品データのINSERT文
├── insert_orders.sql             # 注文データのINSERT文
├── insert_order_items.sql        # 注文明細データのINSERT文
├── customers.csv                 # 顧客データ（CSV形式）
├── products.csv                  # 商品データ（CSV形式）
├── orders.csv                    # 注文データ（CSV形式）
├── order_items.csv               # 注文明細データ（CSV形式）
├── generate_sample_data.py       # 小規模データ生成スクリプト（20件ずつ）
├── generate_large_dataset.py     # 大量データ生成スクリプト（カスタマイズ可能）
├── calculate_max_records.py      # BigQuery無料枠計算スクリプト
├── BIGQUERY_CAPACITY.md          # BigQuery無料枠の詳細計算結果
└── README.md                     # このファイル
```

## 使用方法

### 1. SQLiteでの使用

```bash
# データベース作成
sqlite3 ecommerce.db < schema.sql

# データ投入
sqlite3 ecommerce.db < insert_customers.sql
sqlite3 ecommerce.db < insert_products.sql
sqlite3 ecommerce.db < insert_orders.sql
sqlite3 ecommerce.db < insert_order_items.sql
```

### 2. PostgreSQLでの使用

```bash
# データベース作成
psql -U postgres -d ecommerce -f schema.sql

# データ投入
psql -U postgres -d ecommerce -f insert_customers.sql
psql -U postgres -d ecommerce -f insert_products.sql
psql -U postgres -d ecommerce -f insert_orders.sql
psql -U postgres -d ecommerce -f insert_order_items.sql
```

### 3. BigQueryでの使用

1. BigQueryコンソールでデータセットを作成
2. 各テーブルを作成（`schema.sql`を参考に）
3. CSVファイルをアップロードしてデータをインポート

または、SQL INSERT文をBigQueryで実行することも可能です。

### 4. データの再生成

データを再生成したい場合は、以下のコマンドを実行してください：

```bash
python3 generate_sample_data.py
```

## サンプルクエリ例

### 1. 顧客ごとの注文合計金額

```sql
SELECT 
    c.name,
    COUNT(o.order_id) AS order_count,
    SUM(o.total_amount) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC;
```

### 2. カテゴリ別の売上

```sql
SELECT 
    p.category,
    SUM(oi.subtotal) AS total_sales,
    COUNT(DISTINCT oi.order_id) AS order_count
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY total_sales DESC;
```

### 3. ステータス別の注文数

```sql
SELECT 
    status,
    COUNT(*) AS order_count,
    SUM(total_amount) AS total_amount
FROM orders
GROUP BY status
ORDER BY order_count DESC;
```

### 4. 最も売れている商品トップ5

```sql
SELECT 
    p.name,
    p.category,
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.subtotal) AS total_revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name, p.category
ORDER BY total_quantity DESC
LIMIT 5;
```

## BigQuery無料枠について

このデータセットは、GCP BigQueryの無料枠に十分収まります：

- **ストレージ**: 約10-20KB（無料枠: 10GB/月）
- **クエリ処理**: 非常に小規模なため、無料枠の1TB/月を大幅に下回ります

### BigQuery無料枠に収まる最大レコード数

詳細な計算結果は `BIGQUERY_CAPACITY.md` を参照してください。

**安全な推奨値（無料枠の80%使用）:**
- customers: **約3,800万レコード**
- products: **約3,200万レコード**
- orders: **約9,100万レコード**
- order_items: **約3億2,000万レコード**

**実用的な推奨値（学習・テスト用途）:**
- customers: **1,000万レコード**
- products: **100万レコード**
- orders: **5,000万レコード**
- order_items: **1億5,000万レコード**
- **推定ストレージ**: 約1.3GB（圧縮後）

### 大量データの生成

`generate_large_dataset.py`スクリプトを使用して、指定したレコード数のデータを生成できます：

```bash
# 中規模データセットを生成（10万顧客、1万商品、50万注文）
python3 generate_large_dataset.py --customers 100000 --products 10000 --orders 500000

# 大規模データセットを生成（100万顧客、10万商品、500万注文）
python3 generate_large_dataset.py --customers 1000000 --products 100000 --orders 5000000

# CSV形式のみで出力
python3 generate_large_dataset.py --customers 10000 --format csv

# SQL形式のみで出力
python3 generate_large_dataset.py --customers 10000 --format sql

# ヘルプを表示
python3 generate_large_dataset.py --help
```

**推奨設定例:**

| 用途 | customers | products | orders | 推定ストレージ |
|------|-----------|----------|--------|--------------|
| 小規模（テスト用） | 10,000 | 1,000 | 50,000 | 約1.3MB |
| 中規模（開発用） | 100,000 | 10,000 | 500,000 | 約13MB |
| 大規模（本番テスト用） | 1,000,000 | 100,000 | 5,000,000 | 約130MB |
| 最大規模（無料枠上限） | 10,000,000 | 1,000,000 | 50,000,000 | 約1.3GB |

## Text-to-SQL API（Gemini + FastAPI）

GeminiでSQLを生成し、FastAPI経由でBigQueryに投げる最小構成のAPIを用意しています。

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数

```bash
export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
export BQ_DATASET=ecommerce
export BQ_LOCATION=asia-northeast1
export GEMINI_API_KEY=YOUR_GEMINI_API_KEY
export GEMINI_MODEL=gemini-1.5-flash
```

### 3. 起動（ローカル）

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. 使い方

#### SQL生成

```bash
curl -s http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"カテゴリ別の売上トップ5を出して"}'
```

#### SQL実行

```bash
curl -s http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"sql":"SELECT * FROM `YOUR_PROJECT_ID.ecommerce.orders` LIMIT 10"}'
```

### 5. コスト対策（API側）

- SELECT以外は拒否
- LIMITが無い場合は自動で付与（デフォルト100）
- `maximum_bytes_billed`で上限を設定（デフォルト100MB）

## ライセンス

このデータセットは学習・研究目的で自由にご利用いただけます。


# BigQueryへのデータ投入方法

このドキュメントでは、生成したEコマースデータをBigQueryに格納する方法を説明します。

## 前提条件

1. Google Cloud Platform（GCP）アカウント
2. BigQuery APIが有効になっているプロジェクト
3. 必要な権限（BigQueryデータエディタ以上）

## 方法1: BigQueryコンソールからCSVファイルをアップロード（推奨・簡単）

### 手順

1. **データセットを作成**
   - BigQueryコンソール（https://console.cloud.google.com/bigquery）にアクセス
   - 左側のプロジェクト名をクリック → 「データセットを作成」
   - データセットID: `ecommerce`（任意）
   - ロケーション: `asia-northeast1`（東京）または `us`（米国）

2. **テーブルを作成**
   - 作成したデータセットをクリック → 「テーブルを作成」
   - テーブルIDを入力（例: `customers`）
   - 「スキーマ」タブを選択
   - 「テキストとして編集」をクリックして、以下のスキーマを貼り付け：

   ```json
   [
     {"name": "customer_id", "type": "INTEGER", "mode": "REQUIRED"},
     {"name": "name", "type": "STRING", "mode": "REQUIRED"},
     {"name": "email", "type": "STRING", "mode": "REQUIRED"},
     {"name": "phone", "type": "STRING"},
     {"name": "address", "type": "STRING"},
     {"name": "city", "type": "STRING"},
     {"name": "prefecture", "type": "STRING"},
     {"name": "zip_code", "type": "STRING"},
     {"name": "registration_date", "type": "DATE", "mode": "REQUIRED"}
   ]
   ```

3. **CSVファイルをアップロード**
   - 「データの作成」セクションで「ファイルをアップロード」を選択
   - `customers.csv`を選択
   - ファイル形式: CSV
   - ヘッダー行をスキップ: 1行
   - 「テーブルを作成」をクリック

4. **他のテーブルも同様に作成**
   - `products`, `orders`, `order_items`も同様の手順で作成

## 方法2: bqコマンドラインツールを使用

### セットアップ

```bash
# Google Cloud SDKをインストール（未インストールの場合）
# macOSの場合
brew install google-cloud-sdk

# 認証
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### データセットとテーブルを作成

```bash
# データセットを作成
bq mk --dataset --location=asia-northeast1 ecommerce

# テーブルを作成（スキーマファイルを使用）
bq mk --table ecommerce.customers schema_customers.json
bq mk --table ecommerce.products schema_products.json
bq mk --table ecommerce.orders schema_orders.json
bq mk --table ecommerce.order_items schema_order_items.json
```

### CSVファイルをアップロード

```bash
# 顧客データをアップロード
bq load --source_format=CSV --skip_leading_rows=1 \
  ecommerce.customers customers.csv \
  customer_id:INTEGER,name:STRING,email:STRING,phone:STRING,address:STRING,city:STRING,prefecture:STRING,zip_code:STRING,registration_date:DATE

# 商品データをアップロード
bq load --source_format=CSV --skip_leading_rows=1 \
  ecommerce.products products.csv \
  product_id:INTEGER,name:STRING,category:STRING,brand:STRING,price:NUMERIC,stock_quantity:INTEGER,description:STRING,created_at:DATE

# 注文データをアップロード
bq load --source_format=CSV --skip_leading_rows=1 \
  ecommerce.orders orders.csv \
  order_id:INTEGER,customer_id:INTEGER,order_date:DATE,total_amount:NUMERIC,status:STRING,shipping_address:STRING,payment_method:STRING

# 注文明細データをアップロード
bq load --source_format=CSV --skip_leading_rows=1 \
  ecommerce.order_items order_items.csv \
  order_item_id:INTEGER,order_id:INTEGER,product_id:INTEGER,quantity:INTEGER,unit_price:NUMERIC,subtotal:NUMERIC
```

## 方法3: PythonのBigQueryクライアントライブラリを使用（自動化・推奨）

### セットアップ

```bash
# 必要なライブラリをインストール
pip install -r requirements.txt

# 認証（初回のみ）
gcloud auth application-default login
```

### 使用方法

```bash
# プロジェクトIDを指定して実行
python3 upload_to_bigquery.py --project-id YOUR_PROJECT_ID

# データセットIDやロケーションを指定する場合
python3 upload_to_bigquery.py \
  --project-id YOUR_PROJECT_ID \
  --dataset-id ecommerce \
  --location asia-northeast1 \
  --data-dir .
```

このスクリプトは以下を自動的に実行します：
1. データセットが存在しない場合、作成
2. 各テーブルが存在しない場合、作成（スキーマも自動設定）
3. CSVファイルをアップロード

## 各テーブルのスキーマ（JSON形式）

### customers テーブル

```json
[
  {"name": "customer_id", "type": "INTEGER", "mode": "REQUIRED"},
  {"name": "name", "type": "STRING", "mode": "REQUIRED"},
  {"name": "email", "type": "STRING", "mode": "REQUIRED"},
  {"name": "phone", "type": "STRING"},
  {"name": "address", "type": "STRING"},
  {"name": "city", "type": "STRING"},
  {"name": "prefecture", "type": "STRING"},
  {"name": "zip_code", "type": "STRING"},
  {"name": "registration_date", "type": "DATE", "mode": "REQUIRED"}
]
```

### products テーブル

```json
[
  {"name": "product_id", "type": "INTEGER", "mode": "REQUIRED"},
  {"name": "name", "type": "STRING", "mode": "REQUIRED"},
  {"name": "category", "type": "STRING", "mode": "REQUIRED"},
  {"name": "brand", "type": "STRING"},
  {"name": "price", "type": "NUMERIC", "mode": "REQUIRED"},
  {"name": "stock_quantity", "type": "INTEGER", "mode": "REQUIRED"},
  {"name": "description", "type": "STRING"},
  {"name": "created_at", "type": "DATE", "mode": "REQUIRED"}
]
```

### orders テーブル

```json
[
  {"name": "order_id", "type": "INTEGER", "mode": "REQUIRED"},
  {"name": "customer_id", "type": "INTEGER", "mode": "REQUIRED"},
  {"name": "order_date", "type": "DATE", "mode": "REQUIRED"},
  {"name": "total_amount", "type": "NUMERIC", "mode": "REQUIRED"},
  {"name": "status", "type": "STRING", "mode": "REQUIRED"},
  {"name": "shipping_address", "type": "STRING"},
  {"name": "payment_method", "type": "STRING"}
]
```

### order_items テーブル

```json
[
  {"name": "order_item_id", "type": "INTEGER", "mode": "REQUIRED"},
  {"name": "order_id", "type": "INTEGER", "mode": "REQUIRED"},
  {"name": "product_id", "type": "INTEGER", "mode": "REQUIRED"},
  {"name": "quantity", "type": "INTEGER", "mode": "REQUIRED"},
  {"name": "unit_price", "type": "NUMERIC", "mode": "REQUIRED"},
  {"name": "subtotal", "type": "NUMERIC", "mode": "REQUIRED"}
]
```

## データ投入後の確認

BigQueryコンソールで以下のクエリを実行して、データが正しく投入されたか確認できます：

```sql
-- レコード数を確認
SELECT 
  'customers' AS table_name, COUNT(*) AS record_count FROM `YOUR_PROJECT_ID.ecommerce.customers`
UNION ALL
SELECT 'products', COUNT(*) FROM `YOUR_PROJECT_ID.ecommerce.products`
UNION ALL
SELECT 'orders', COUNT(*) FROM `YOUR_PROJECT_ID.ecommerce.orders`
UNION ALL
SELECT 'order_items', COUNT(*) FROM `YOUR_PROJECT_ID.ecommerce.order_items`;

-- サンプルデータを確認
SELECT * FROM `YOUR_PROJECT_ID.ecommerce.customers` LIMIT 10;
```

## トラブルシューティング

### エラー: "Permission denied"
- BigQuery APIが有効になっているか確認
- 必要な権限（BigQueryデータエディタ以上）があるか確認

### エラー: "Table already exists"
- 既存のテーブルを削除するか、`upload_to_bigquery.py`は自動的に上書きします

### エラー: "Invalid date format"
- CSVファイルの日付形式が `YYYY-MM-DD` になっているか確認

## コストについて

1万レコード×4テーブル = 約4万レコードのデータは、BigQuery無料枠（10GBストレージ）に十分収まります。

- **ストレージ**: 約5-10MB（圧縮後）
- **クエリ処理**: 小規模なクエリは無料枠（1TB/月）内

## 次のステップ

データ投入後、text-to-SQLエージェントの開発を開始できます：

1. BigQueryのクエリエディタでSQLクエリをテスト
2. LLM API（OpenAI、Claude等）を使用して自然言語からSQLを生成
3. 生成されたSQLをBigQueryで実行して結果を取得



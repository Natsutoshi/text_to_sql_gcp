# BigQueryへのデータアップロードガイド

このガイドでは、生成したEコマースデータをBigQueryにアップロードする方法を説明します。

## 前提条件

1. **GCPプロジェクトの作成**
   - [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
   - BigQuery APIを有効化

2. **認証情報の設定**
   - サービスアカウントキーの作成、または
   - `gcloud auth application-default login` で認証

## 方法1: BigQueryコンソールから手動アップロード（推奨：初回）

### ステップ1: データセットの作成

1. [BigQueryコンソール](https://console.cloud.google.com/bigquery)を開く
2. 左側のプロジェクト名をクリック → 「データセットを作成」
3. データセットID: `ecommerce`（任意）
4. リージョン: `asia-northeast1`（東京）を選択
5. 「データセットを作成」をクリック

### ステップ2: テーブルの作成とデータアップロード

各テーブルについて以下を繰り返します：

#### customersテーブル

1. データセット `ecommerce` を展開 → 「テーブルを作成」
2. **ソース**:
   - テーブルを作成元: 「ファイルをアップロード」を選択
   - ファイルを選択: `customers.csv` を選択
   - ファイル形式: CSV
3. **宛先**:
   - データセット: `ecommerce`
   - テーブル名: `customers`
4. **スキーマ**:
   - 「テーブルスキーマを自動検出」にチェック
   - または、以下のスキーマを手動で設定：
     ```
     customer_id: INTEGER (必須)
     name: STRING (必須)
     email: STRING (必須)
     phone: STRING
     address: STRING
     city: STRING
     prefecture: STRING
     zip_code: STRING
     registration_date: DATE (必須)
     ```
5. 「テーブルを作成」をクリック

#### productsテーブル

同様の手順で `products.csv` をアップロード：
- テーブル名: `products`
- スキーマ:
  ```
  product_id: INTEGER (必須)
  name: STRING (必須)
  category: STRING (必須)
  brand: STRING
  price: NUMERIC (必須)
  stock_quantity: INTEGER (必須)
  description: STRING
  created_at: DATE (必須)
  ```

#### ordersテーブル

同様の手順で `orders.csv` をアップロード：
- テーブル名: `orders`
- スキーマ:
  ```
  order_id: INTEGER (必須)
  customer_id: INTEGER (必須)
  order_date: DATE (必須)
  total_amount: NUMERIC (必須)
  status: STRING (必須)
  shipping_address: STRING
  payment_method: STRING
  ```

#### order_itemsテーブル

同様の手順で `order_items.csv` をアップロード：
- テーブル名: `order_items`
- スキーマ:
  ```
  order_item_id: INTEGER (必須)
  order_id: INTEGER (必須)
  product_id: INTEGER (必須)
  quantity: INTEGER (必須)
  unit_price: NUMERIC (必須)
  subtotal: NUMERIC (必須)
  ```

## 方法2: bqコマンドラインツールを使用

### インストール

```bash
# gcloud CLIがインストールされている場合
gcloud components install bq

# または、Cloud SDKをインストール
# https://cloud.google.com/sdk/docs/install
```

### 認証

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### データセットの作成

```bash
bq mk --dataset --location=asia-northeast1 ecommerce
```

### テーブルの作成とデータアップロード

```bash
# customersテーブル
bq load --source_format=CSV --skip_leading_rows=1 --autodetect \
  ecommerce.customers customers.csv

# productsテーブル
bq load --source_format=CSV --skip_leading_rows=1 --autodetect \
  ecommerce.products products.csv

# ordersテーブル
bq load --source_format=CSV --skip_leading_rows=1 --autodetect \
  ecommerce.orders orders.csv

# order_itemsテーブル
bq load --source_format=CSV --skip_leading_rows=1 --autodetect \
  ecommerce.order_items order_items.csv
```

### データ確認

```bash
# レコード数を確認
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) as count FROM \`ecommerce.customers\`"

bq query --use_legacy_sql=false \
  "SELECT COUNT(*) as count FROM \`ecommerce.products\`"

bq query --use_legacy_sql=false \
  "SELECT COUNT(*) as count FROM \`ecommerce.orders\`"

bq query --use_legacy_sql=false \
  "SELECT COUNT(*) as count FROM \`ecommerce.order_items\`"
```

## 方法3: Pythonスクリプトを使用（自動化）

### 必要なライブラリのインストール

```bash
pip install google-cloud-bigquery
```

### 認証の設定

```bash
# サービスアカウントキーを使用する場合
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"

# または、Application Default Credentialsを使用
gcloud auth application-default login
```

### スクリプトの実行

```bash
python3 upload_to_bigquery.py \
  --project-id YOUR_PROJECT_ID \
  --dataset-id ecommerce \
  --location asia-northeast1 \
  --create-tables \
  --truncate
```

### オプション

- `--create-tables`: テーブルを自動作成（既存の場合はスキップ）
- `--truncate`: 既存のデータを削除してからアップロード
- `--csv-dir`: CSVファイルのディレクトリを指定（デフォルト: カレントディレクトリ）

## 方法4: SQL INSERT文を使用

生成されたSQL INSERT文をBigQueryで実行することも可能です：

1. BigQueryコンソールでクエリエディタを開く
2. `insert_customers.sql` の内容をコピー＆ペースト
3. 実行

**注意**: 1万レコードのINSERT文は大きいため、バッチ処理やCSVアップロードの方が効率的です。

## データ確認クエリ

アップロード後、以下のクエリでデータを確認できます：

```sql
-- 各テーブルのレコード数
SELECT 'customers' as table_name, COUNT(*) as count FROM `ecommerce.customers`
UNION ALL
SELECT 'products', COUNT(*) FROM `ecommerce.products`
UNION ALL
SELECT 'orders', COUNT(*) FROM `ecommerce.orders`
UNION ALL
SELECT 'order_items', COUNT(*) FROM `ecommerce.order_items`;

-- サンプルデータの確認
SELECT * FROM `ecommerce.customers` LIMIT 5;
SELECT * FROM `ecommerce.products` LIMIT 5;
SELECT * FROM `ecommerce.orders` LIMIT 5;
SELECT * FROM `ecommerce.order_items` LIMIT 5;

-- 顧客ごとの注文数
SELECT 
    c.name,
    COUNT(o.order_id) as order_count,
    SUM(o.total_amount) as total_spent
FROM `ecommerce.customers` c
LEFT JOIN `ecommerce.orders` o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC
LIMIT 10;
```

## トラブルシューティング

### エラー: "Access Denied"

- プロジェクトの権限を確認
- BigQuery APIが有効化されているか確認
- サービスアカウントに適切な権限があるか確認

### エラー: "Invalid date format"

- CSVファイルの日付形式が `YYYY-MM-DD` であることを確認
- タイムゾーンの設定を確認

### エラー: "Table already exists"

- `--truncate` オプションを使用して既存データを削除
- または、別のテーブル名を使用

### パフォーマンスの最適化

- パーティション分割: 日付カラムでパーティション分割（`bigquery_schema.sql`を参照）
- クラスタリング: よく使用するカラムでクラスタリング
- ストリーミング挿入: リアルタイムデータの場合はストリーミング挿入を使用

## コスト見積もり

1万レコード × 4テーブルの場合：

- **ストレージ**: 約5-10MB（圧縮後）→ **無料枠内**
- **クエリ処理**: データ確認クエリは数MB程度 → **無料枠内**

BigQuery無料枠（10GBストレージ、1TBクエリ/月）に十分収まります。

## 次のステップ

データがアップロードできたら、text-to-SQLエージェントの開発を開始できます！


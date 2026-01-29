#!/usr/bin/env python3
"""
BigQueryにデータをアップロードするスクリプト
"""

import os
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import argparse

# テーブルスキーマ定義
SCHEMAS = {
    'customers': [
        bigquery.SchemaField("customer_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("phone", "STRING"),
        bigquery.SchemaField("address", "STRING"),
        bigquery.SchemaField("city", "STRING"),
        bigquery.SchemaField("prefecture", "STRING"),
        bigquery.SchemaField("zip_code", "STRING"),
        bigquery.SchemaField("registration_date", "DATE", mode="REQUIRED"),
    ],
    'products': [
        bigquery.SchemaField("product_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("category", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("brand", "STRING"),
        bigquery.SchemaField("price", "NUMERIC", mode="REQUIRED"),
        bigquery.SchemaField("stock_quantity", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("description", "STRING"),
        bigquery.SchemaField("created_at", "DATE", mode="REQUIRED"),
    ],
    'orders': [
        bigquery.SchemaField("order_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("customer_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("order_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("total_amount", "NUMERIC", mode="REQUIRED"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("shipping_address", "STRING"),
        bigquery.SchemaField("payment_method", "STRING"),
    ],
    'order_items': [
        bigquery.SchemaField("order_item_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("order_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("product_id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("quantity", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("unit_price", "NUMERIC", mode="REQUIRED"),
        bigquery.SchemaField("subtotal", "NUMERIC", mode="REQUIRED"),
    ],
}

def create_dataset_if_not_exists(client, project_id, dataset_id, location='asia-northeast1'):
    """データセットが存在しない場合、作成する"""
    dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset_ref.location = location
    
    try:
        client.get_dataset(dataset_ref)
        print(f"データセット '{dataset_id}' は既に存在します")
        return dataset_ref
    except NotFound:
        print(f"データセット '{dataset_id}' を作成中...")
        dataset = client.create_dataset(dataset_ref, timeout=30)
        print(f"データセット '{dataset_id}' を作成しました")
        return dataset_ref

def create_table_if_not_exists(client, dataset_ref, table_id, schema):
    """テーブルが存在しない場合、作成する"""
    table_ref = dataset_ref.table(table_id)
    
    try:
        client.get_table(table_ref)
        print(f"テーブル '{table_id}' は既に存在します")
        return table_ref
    except NotFound:
        print(f"テーブル '{table_id}' を作成中...")
        table = bigquery.Table(table_ref, schema=schema)
        table = client.create_table(table)
        print(f"テーブル '{table_id}' を作成しました")
        return table_ref

def upload_csv_to_bigquery(client, table_ref, csv_file, schema):
    """CSVファイルをBigQueryにアップロード"""
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=False,
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # 既存データを上書き
    )
    
    print(f"'{csv_file}' をアップロード中...")
    with open(csv_file, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_ref, job_config=job_config)
    
    job.result()  # ジョブの完了を待つ
    
    table = client.get_table(table_ref)
    print(f"✓ '{csv_file}' のアップロード完了: {table.num_rows:,} 行")

def main():
    parser = argparse.ArgumentParser(description='BigQueryにデータをアップロード')
    parser.add_argument('--project-id', type=str, required=True, help='GCPプロジェクトID')
    parser.add_argument('--dataset-id', type=str, default='ecommerce', help='データセットID（デフォルト: ecommerce）')
    parser.add_argument('--location', type=str, default='asia-northeast1', help='ロケーション（デフォルト: asia-northeast1）')
    parser.add_argument('--data-dir', type=str, default='.', help='CSVファイルがあるディレクトリ（デフォルト: カレントディレクトリ）')
    
    args = parser.parse_args()
    
    # BigQueryクライアントを初期化
    client = bigquery.Client(project=args.project_id)
    
    print("=" * 70)
    print("BigQueryへのデータアップロード")
    print("=" * 70)
    print(f"プロジェクトID: {args.project_id}")
    print(f"データセットID: {args.dataset_id}")
    print(f"ロケーション: {args.location}")
    print("=" * 70)
    print()
    
    # データセットを作成
    dataset_ref = create_dataset_if_not_exists(client, args.project_id, args.dataset_id, args.location)
    print()
    
    # 各テーブルを作成してデータをアップロード
    tables = ['customers', 'products', 'orders', 'order_items']
    
    for table_id in tables:
        csv_file = os.path.join(args.data_dir, f"{table_id}.csv")
        
        if not os.path.exists(csv_file):
            print(f"⚠ 警告: '{csv_file}' が見つかりません。スキップします。")
            continue
        
        # テーブルを作成
        table_ref = create_table_if_not_exists(client, dataset_ref, table_id, SCHEMAS[table_id])
        
        # CSVファイルをアップロード
        upload_csv_to_bigquery(client, table_ref, csv_file, SCHEMAS[table_id])
        print()
    
    print("=" * 70)
    print("アップロード完了！")
    print("=" * 70)
    print(f"BigQueryコンソール: https://console.cloud.google.com/bigquery?project={args.project_id}")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
BigQuery無料枠に収まる最大レコード数を計算するスクリプト
"""

import os

# BigQuery無料枠の制限
BIGQUERY_FREE_STORAGE_GB = 10
BIGQUERY_FREE_STORAGE_KB = BIGQUERY_FREE_STORAGE_GB * 1024 * 1024  # 10GB = 10,485,760 KB

# BigQueryの圧縮率（一般的に5-10倍圧縮されるが、安全のため3倍として計算）
COMPRESSION_RATIO = 3

# 実効ストレージ容量（圧縮を考慮）
EFFECTIVE_STORAGE_KB = BIGQUERY_FREE_STORAGE_KB * COMPRESSION_RATIO

# 現在のCSVファイルサイズとレコード数を確認
csv_files = {
    'customers': ('customers.csv', 20),
    'products': ('products.csv', 20),
    'orders': ('orders.csv', 20),
    'order_items': ('order_items.csv', 40),
}

def get_file_size_kb(filename):
    """ファイルサイズをKBで取得"""
    if os.path.exists(filename):
        size_bytes = os.path.getsize(filename)
        return size_bytes / 1024
    return 0

def calculate_max_records():
    """各テーブルの最大レコード数を計算"""
    print("=" * 70)
    print("BigQuery無料枠（10GB）に収まる最大レコード数の計算")
    print("=" * 70)
    print(f"\nBigQuery無料枠ストレージ: {BIGQUERY_FREE_STORAGE_GB}GB")
    print(f"圧縮率を考慮した実効容量: {EFFECTIVE_STORAGE_KB / (1024*1024):.2f}GB (圧縮率 {COMPRESSION_RATIO}倍想定)")
    print()
    
    results = {}
    total_size_kb = 0
    
    # 各テーブルのサイズとレコード数を確認
    print("現在のデータサイズ:")
    print("-" * 70)
    for table_name, (filename, record_count) in csv_files.items():
        file_size_kb = get_file_size_kb(filename)
        bytes_per_record = (file_size_kb * 1024) / record_count if record_count > 0 else 0
        total_size_kb += file_size_kb
        
        print(f"{table_name:15s}: {file_size_kb:8.2f}KB ({record_count:6d}レコード) - "
              f"1レコードあたり {bytes_per_record:6.1f}バイト")
        
        # 最大レコード数を計算（圧縮を考慮）
        max_records = int((EFFECTIVE_STORAGE_KB * 1024) / bytes_per_record) if bytes_per_record > 0 else 0
        results[table_name] = {
            'current_records': record_count,
            'file_size_kb': file_size_kb,
            'bytes_per_record': bytes_per_record,
            'max_records': max_records
        }
    
    print("-" * 70)
    print(f"合計: {total_size_kb:.2f}KB")
    print()
    
    # リレーションシップを考慮した推奨値
    print("=" * 70)
    print("各テーブルの最大レコード数（単独で計算）:")
    print("=" * 70)
    for table_name, data in results.items():
        print(f"{table_name:15s}: 最大 {data['max_records']:>15,} レコード")
    
    print()
    print("=" * 70)
    print("リレーションシップを考慮した推奨値:")
    print("=" * 70)
    
    # リレーションシップを考慮
    # customers: 基準
    # products: customersと同程度または少なめ
    # orders: customersの数倍（1顧客あたり複数注文）
    # order_items: ordersの数倍（1注文あたり複数商品）
    
    # ストレージを4テーブルで分配（リレーションシップを考慮）
    # customers: 20%, products: 20%, orders: 30%, order_items: 30%
    allocation = {
        'customers': 0.20,
        'products': 0.20,
        'orders': 0.30,
        'order_items': 0.30
    }
    
    recommended = {}
    for table_name, ratio in allocation.items():
        allocated_storage_kb = EFFECTIVE_STORAGE_KB * ratio
        data = results[table_name]
        max_records = int((allocated_storage_kb * 1024) / data['bytes_per_record']) if data['bytes_per_record'] > 0 else 0
        recommended[table_name] = max_records
        
        print(f"{table_name:15s}: 推奨 {max_records:>15,} レコード "
              f"(ストレージ配分: {ratio*100:.0f}%, 約 {allocated_storage_kb/(1024*1024):.2f}GB)")
    
    print()
    print("=" * 70)
    print("推奨構成の詳細:")
    print("=" * 70)
    
    # より現実的な数値に調整（丸め）
    realistic = {
        'customers': 10_000_000,      # 1,000万顧客
        'products': 1_000_000,         # 100万商品
        'orders': 50_000_000,          # 5,000万注文
        'order_items': 150_000_000,   # 1億5,000万注文明細
    }
    
    total_storage_estimate = 0
    for table_name, records in realistic.items():
        data = results[table_name]
        estimated_size_kb = (data['bytes_per_record'] * records) / 1024
        compressed_size_kb = estimated_size_kb / COMPRESSION_RATIO
        total_storage_estimate += compressed_size_kb
        
        print(f"\n{table_name}:")
        print(f"  レコード数: {records:,}")
        print(f"  推定サイズ（圧縮前）: {estimated_size_kb/(1024*1024):.2f}GB")
        print(f"  推定サイズ（圧縮後）: {compressed_size_kb/(1024*1024):.2f}GB")
    
    print()
    print(f"合計推定ストレージ（圧縮後）: {total_storage_estimate/(1024*1024):.2f}GB")
    print(f"BigQuery無料枠: {BIGQUERY_FREE_STORAGE_GB}GB")
    
    if total_storage_estimate / (1024*1024) <= BIGQUERY_FREE_STORAGE_GB:
        print("✓ 無料枠内に収まります！")
    else:
        print("⚠ 無料枠を超える可能性があります。レコード数を調整してください。")
    
    print()
    print("=" * 70)
    print("安全な推奨値（無料枠の80%使用を想定）:")
    print("=" * 70)
    
    safe_limit = BIGQUERY_FREE_STORAGE_GB * 0.8
    safe_storage_kb = safe_limit * 1024 * 1024 * COMPRESSION_RATIO
    
    safe_recommended = {}
    for table_name, ratio in allocation.items():
        allocated_storage_kb = safe_storage_kb * ratio
        data = results[table_name]
        max_records = int((allocated_storage_kb * 1024) / data['bytes_per_record']) if data['bytes_per_record'] > 0 else 0
        safe_recommended[table_name] = max_records
        
        print(f"{table_name:15s}: {max_records:>15,} レコード")
    
    return safe_recommended

if __name__ == '__main__':
    recommended = calculate_max_records()


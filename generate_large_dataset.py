#!/usr/bin/env python3
"""
Eコマース店舗の大量データ生成スクリプト
BigQuery無料枠に収まる量のデータを生成します
"""

import random
import argparse
from datetime import datetime, timedelta
import csv
import sys

# サンプルデータの定義
EMAIL_DOMAINS = [
    "gmail.com", "yahoo.co.jp", "outlook.com", "icloud.com", "example.com"
]

# 都道府県と市区町村、郵便番号の対応（実在する住所）
ADDRESS_DATA = [
    {
        "prefecture": "東京都",
        "city": "千代田区",
        "area": "丸の内",
        "zip_start": 1000001,
        "zip_end": 1000021
    },
    {
        "prefecture": "東京都",
        "city": "新宿区",
        "area": "新宿",
        "zip_start": 1600001,
        "zip_end": 1600021
    },
    {
        "prefecture": "東京都",
        "city": "渋谷区",
        "area": "渋谷",
        "zip_start": 1500001,
        "zip_end": 1500041
    },
    {
        "prefecture": "大阪府",
        "city": "大阪市北区",
        "area": "梅田",
        "zip_start": 5300001,
        "zip_end": 5300021
    },
    {
        "prefecture": "大阪府",
        "city": "大阪市中央区",
        "area": "本町",
        "zip_start": 5410001,
        "zip_end": 5410041
    },
    {
        "prefecture": "愛知県",
        "city": "名古屋市中区",
        "area": "錦",
        "zip_start": 4600001,
        "zip_end": 4600008
    },
    {
        "prefecture": "愛知県",
        "city": "名古屋市西区",
        "area": "名駅",
        "zip_start": 4510001,
        "zip_end": 4510041
    },
    {
        "prefecture": "福岡県",
        "city": "福岡市博多区",
        "area": "博多駅前",
        "zip_start": 8120001,
        "zip_end": 8120021
    },
    {
        "prefecture": "福岡県",
        "city": "福岡市中央区",
        "area": "天神",
        "zip_start": 8100001,
        "zip_end": 8100041
    },
    {
        "prefecture": "北海道",
        "city": "札幌市中央区",
        "area": "北1条西",
        "zip_start": 600001,
        "zip_end": 600041
    },
    {
        "prefecture": "北海道",
        "city": "札幌市北区",
        "area": "北6条西",
        "zip_start": 600001,
        "zip_end": 600041
    },
    {
        "prefecture": "神奈川県",
        "city": "横浜市中区",
        "area": "本町",
        "zip_start": 2310001,
        "zip_end": 2310041
    },
    {
        "prefecture": "神奈川県",
        "city": "横浜市西区",
        "area": "みなとみらい",
        "zip_start": 2200001,
        "zip_end": 2200041
    },
    {
        "prefecture": "埼玉県",
        "city": "さいたま市浦和区",
        "area": "高砂",
        "zip_start": 3300001,
        "zip_end": 3300041
    },
    {
        "prefecture": "埼玉県",
        "city": "さいたま市大宮区",
        "area": "大宮",
        "zip_start": 3300001,
        "zip_end": 3300041
    },
    {
        "prefecture": "千葉県",
        "city": "千葉市中央区",
        "area": "中央",
        "zip_start": 2600001,
        "zip_end": 2600041
    },
    {
        "prefecture": "千葉県",
        "city": "千葉市美浜区",
        "area": "美浜",
        "zip_start": 2610001,
        "zip_end": 2610041
    },
    {
        "prefecture": "兵庫県",
        "city": "神戸市中央区",
        "area": "三宮町",
        "zip_start": 6500001,
        "zip_end": 6500041
    },
    {
        "prefecture": "兵庫県",
        "city": "神戸市灘区",
        "area": "灘南通",
        "zip_start": 6570001,
        "zip_end": 6570041
    },
    {
        "prefecture": "京都府",
        "city": "京都市中京区",
        "area": "烏丸通",
        "zip_start": 6040001,
        "zip_end": 6040041
    },
    {
        "prefecture": "京都府",
        "city": "京都市下京区",
        "area": "四条通",
        "zip_start": 6000001,
        "zip_end": 6000041
    }
]

PRODUCT_CATEGORIES = [
    "エレクトロニクス", "ファッション", "食品・飲料", "ホーム・キッチン",
    "スポーツ・アウトドア", "本・雑誌", "美容・健康", "おもちゃ・ゲーム"
]

PRODUCT_NAMES = {
    "エレクトロニクス": [
        "ワイヤレスイヤホン", "スマートフォンケース", "モバイルバッテリー",
        "USBケーブル", "Bluetoothスピーカー", "タブレットスタンド",
        "ワイヤレスマウス", "キーボード", "モニタースタンド", "充電器"
    ],
    "ファッション": [
        "コットンTシャツ", "デニムジーンズ", "スニーカー", "レザージャケット",
        "ウールコート", "キャップ", "バッグ", "ベルト", "サングラス", "時計"
    ],
    "食品・飲料": [
        "有機コーヒー豆", "緑茶パック", "チョコレート詰め合わせ", "スナック菓子",
        "調味料セット", "ドライフルーツ", "ナッツミックス", "ハチミツ",
        "オリーブオイル", "パスタセット"
    ],
    "ホーム・キッチン": [
        "コーヒーメーカー", "調理器具セット", "食器セット", "バス用品セット",
        "収納ボックス", "ラグマット", "カーテン", "照明器具", "マットレス",
        "枕"
    ],
    "スポーツ・アウトドア": [
        "ヨガマット", "ランニングシューズ", "トレーニングウェア", "水筒",
        "キャンプ用品セット", "自転車ヘルメット", "テニスラケット",
        "バスケットボール", "サッカーボール", "フィットネスバンド"
    ],
    "本・雑誌": [
        "ビジネス書", "小説", "技術書", "料理本", "旅行ガイド",
        "写真集", "絵本", "雑誌バックナンバー", "辞書", "参考書"
    ],
    "美容・健康": [
        "スキンケアセット", "シャンプー", "ボディソープ", "化粧水",
        "日焼け止め", "マスク", "サプリメント", "歯ブラシ", "デンタルフロス",
        "ボディクリーム"
    ],
    "おもちゃ・ゲーム": [
        "パズル", "ボードゲーム", "カードゲーム", "プラモデル",
        "ぬいぐるみ", "レゴブロック", "アクションフィギュア", "パズルゲーム",
        "知育玩具", "ゲームソフト"
    ]
}

BRANDS = {
    "エレクトロニクス": ["TechPro", "SoundMax", "PowerUp", "Connect", "DigitalLife"],
    "ファッション": ["StyleCo", "UrbanWear", "Classic", "Modern", "Trendy"],
    "食品・飲料": ["Natural", "Organic", "Premium", "Fresh", "Healthy"],
    "ホーム・キッチン": ["HomeLife", "KitchenPro", "Comfort", "Design", "Quality"],
    "スポーツ・アウトドア": ["SportMax", "Outdoor", "Active", "Fit", "Energy"],
    "本・雑誌": ["出版社A", "出版社B", "出版社C", "出版社D", "出版社E"],
    "美容・健康": ["Beauty", "Care", "Pure", "Natural", "Wellness"],
    "おもちゃ・ゲーム": ["ToyFun", "GameZone", "PlayTime", "Kids", "Fun"]
}

ORDER_STATUSES = ["pending", "processing", "shipped", "delivered", "cancelled"]
PAYMENT_METHODS = ["credit_card", "bank_transfer", "convenience_store", "paypal"]

def generate_customer_name(seed):
    """シード値から顧客名を生成"""
    first_names = ["太郎", "花子", "一郎", "次郎", "三郎", "美咲", "健太", "さくら", 
                   "大輔", "麻衣", "優子", "和也", "真由美", "拓也", "直樹", "由美",
                   "健一", "智子", "翔太", "美穂", "雄一", "恵子", "誠", "愛", "亮",
                   "美香", "達也", "香織", "剛", "千佳", "慎一", "由美子", "正", "麻美"]
    last_names = ["山田", "佐藤", "鈴木", "田中", "渡辺", "伊藤", "中村", "小林",
                  "加藤", "吉田", "高橋", "松本", "井上", "木村", "林", "斎藤",
                  "山本", "森田", "池田", "前田", "橋本", "藤原", "石川", "後藤",
                  "岡田", "長谷川", "近藤", "村上", "遠藤", "青木", "坂本", "藤井"]
    
    random.seed(seed)
    return f"{random.choice(last_names)}{random.choice(first_names)}"

def generate_email(name, customer_id):
    """メールアドレスを生成"""
    name_lower = name.lower().replace(' ', '')
    domain = random.choice(EMAIL_DOMAINS)
    return f"{name_lower}{customer_id}@{domain}"

def generate_customers(num_customers):
    """顧客データを生成"""
    customers = []
    base_date = datetime(2023, 1, 1)
    
    print(f"顧客データを生成中: {num_customers:,}件...")
    
    for i in range(num_customers):
        if (i + 1) % 10000 == 0:
            print(f"  進行状況: {i + 1:,}/{num_customers:,}")
        
        customer_id = i + 1
        name = generate_customer_name(i)
        email = generate_email(name, customer_id)
        phone = f"090-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        
        # 実在する住所データから選択
        addr_data = random.choice(ADDRESS_DATA)
        prefecture = addr_data["prefecture"]
        city = addr_data["city"]
        area = addr_data["area"]
        
        # 郵便番号を範囲内から生成（7桁、ハイフンなし、先頭0埋め）
        zip_num = random.randint(addr_data["zip_start"], addr_data["zip_end"])
        zip_code = str(zip_num).zfill(7)
        
        # 実在する住所形式で生成
        chome = random.randint(1, 10)
        ban = random.randint(1, 30)
        go = random.randint(1, 10)
        address = f"{prefecture}{city}{area}{chome}丁目{ban}番{go}号"
        
        registration_date = base_date + timedelta(days=random.randint(0, 730))
        
        customers.append({
            'customer_id': customer_id,
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
            'city': city,
            'prefecture': prefecture,
            'zip_code': zip_code,
            'registration_date': registration_date.strftime('%Y-%m-%d')
        })
    
    return customers

def generate_products(num_products):
    """商品データを生成"""
    products = []
    base_date = datetime(2023, 1, 1)
    
    print(f"商品データを生成中: {num_products:,}件...")
    
    # 各カテゴリから均等に商品を生成
    products_per_category = num_products // len(PRODUCT_CATEGORIES)
    remaining = num_products % len(PRODUCT_CATEGORIES)
    
    product_id = 1
    for idx, category in enumerate(PRODUCT_CATEGORIES):
        category_products = PRODUCT_NAMES[category]
        brands = BRANDS[category]
        num_in_category = products_per_category + (1 if idx < remaining else 0)
        
        for j in range(num_in_category):
            if product_id > num_products:
                break
            
            if product_id % 10000 == 0:
                print(f"  進行状況: {product_id:,}/{num_products:,}")
            
            # 商品名を生成（既存の名前から選ぶか、番号を付ける）
            if j < len(category_products):
                product_name = category_products[j]
            else:
                product_name = f"{category_products[j % len(category_products)]} {j // len(category_products) + 1}"
            
            price = random.randint(500, 50000)
            stock_quantity = random.randint(0, 1000)
            description = f"{product_name}の詳細説明です。高品質でおすすめの商品です。"
            created_at = base_date + timedelta(days=random.randint(0, 365))
            
            products.append({
                'product_id': product_id,
                'name': product_name,
                'category': category,
                'brand': random.choice(brands),
                'price': price,
                'stock_quantity': stock_quantity,
                'description': description,
                'created_at': created_at.strftime('%Y-%m-%d')
            })
            product_id += 1
    
    return products

def generate_orders(num_orders, num_customers, products, customers):
    """注文データを生成（実在する住所を使用）"""
    orders = []
    base_date = datetime(2024, 1, 1)
    
    print(f"注文データを生成中: {num_orders:,}件...")
    
    for i in range(num_orders):
        if (i + 1) % 10000 == 0:
            print(f"  進行状況: {i + 1:,}/{num_orders:,}")
        
        order_id = i + 1
        customer_id = random.randint(1, num_customers)
        order_date = base_date + timedelta(days=random.randint(0, 180))
        
        # 注文ステータスの分布を調整
        status_weights = [0.1, 0.2, 0.2, 0.4, 0.1]
        status = random.choices(ORDER_STATUSES, weights=status_weights)[0]
        
        payment_method = random.choice(PAYMENT_METHODS)
        
        # 配送先住所は顧客の住所を使用（実在する住所と一致させる）
        # 顧客IDに対応する顧客データから住所を取得
        customer = customers[customer_id - 1]  # customer_idは1から始まるため-1
        shipping_address = customer['address']
        
        # 注文明細から合計金額を計算するため、一旦0に設定
        total_amount = 0
        
        orders.append({
            'order_id': order_id,
            'customer_id': customer_id,
            'order_date': order_date.strftime('%Y-%m-%d'),
            'total_amount': total_amount,
            'status': status,
            'shipping_address': shipping_address,
            'payment_method': payment_method
        })
    
    return orders

def generate_order_items(orders, products, items_per_order_avg=2.5, max_items=None):
    """注文明細データを生成"""
    order_items = []
    order_item_id = 1
    
    # max_itemsが指定されている場合、その数まで生成
    target_items = max_items if max_items else int(len(orders) * items_per_order_avg)
    print(f"注文明細データを生成中: 約{target_items:,}件...")
    
    for order_idx, order in enumerate(orders):
        if (order_idx + 1) % 10000 == 0:
            print(f"  進行状況: {order_idx + 1:,}/{len(orders):,}")
        
        # max_itemsが指定されている場合、上限に達したら終了
        if max_items and order_item_id > max_items:
            break
        
        order_id = order['order_id']
        # items_per_order_avgが1.0の場合、1商品のみ
        if items_per_order_avg <= 1.0:
            num_items_in_order = 1
        else:
            # 1注文あたり1-5商品（平均2.5）
            num_items_in_order = random.choices([1, 2, 3, 4, 5], weights=[10, 30, 40, 15, 5])[0]
        
        # max_itemsが指定されている場合、残り件数を考慮
        if max_items:
            remaining = max_items - (order_item_id - 1)
            num_items_in_order = min(num_items_in_order, remaining)
            if num_items_in_order <= 0:
                break
        
        selected_products = random.sample(products, min(num_items_in_order, len(products)))
        
        order_total = 0
        for product in selected_products:
            quantity = random.randint(1, 5)
            unit_price = product['price']
            subtotal = unit_price * quantity
            order_total += subtotal
            
            order_items.append({
                'order_item_id': order_item_id,
                'order_id': order_id,
                'product_id': product['product_id'],
                'quantity': quantity,
                'unit_price': unit_price,
                'subtotal': subtotal
            })
            order_item_id += 1
        
        # 注文の合計金額を更新
        order['total_amount'] = order_total
    
    return order_items

def write_csv(filename, data, fieldnames):
    """CSVファイルに書き込み"""
    print(f"CSVファイルに書き込み中: {filename}...")
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"  完了: {len(data):,}レコード")

def write_sql_insert(filename, table_name, data, fieldnames, batch_size=1000):
    """SQL INSERT文を生成（バッチ処理）"""
    print(f"SQL INSERT文を生成中: {filename}...")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"-- {table_name}テーブルのサンプルデータ\n")
        f.write(f"-- 総レコード数: {len(data):,}\n\n")
        
        # バッチごとにINSERT文を生成
        for batch_start in range(0, len(data), batch_size):
            batch_end = min(batch_start + batch_size, len(data))
            batch = data[batch_start:batch_end]
            
            f.write(f"INSERT INTO {table_name} ({', '.join(fieldnames)}) VALUES\n")
            
            for i, row in enumerate(batch):
                values = []
                for field in fieldnames:
                    value = row[field]
                    if isinstance(value, str):
                        value = value.replace("'", "''")
                        values.append(f"'{value}'")
                    elif value is None:
                        values.append("NULL")
                    else:
                        values.append(str(value))
                
                comma = "," if i < len(batch) - 1 else ";"
                f.write(f"  ({', '.join(values)}){comma}\n")
            
            f.write("\n")
    
    print(f"  完了: {len(data):,}レコード")

def main():
    parser = argparse.ArgumentParser(description='Eコマース店舗の大量データを生成')
    parser.add_argument('--customers', type=int, default=10000, help='顧客数（デフォルト: 10,000）')
    parser.add_argument('--products', type=int, default=1000, help='商品数（デフォルト: 1,000）')
    parser.add_argument('--orders', type=int, default=50000, help='注文数（デフォルト: 50,000）')
    parser.add_argument('--items-per-order', type=float, default=2.5, help='1注文あたりの平均商品数（デフォルト: 2.5）')
    parser.add_argument('--max-order-items', type=int, default=None, help='注文明細の最大件数（指定した場合、この数まで生成）')
    parser.add_argument('--format', choices=['csv', 'sql', 'both'], default='both', help='出力形式')
    parser.add_argument('--output-dir', type=str, default='.', help='出力ディレクトリ')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Eコマース店舗 大量データ生成")
    print("=" * 70)
    print(f"顧客数: {args.customers:,}")
    print(f"商品数: {args.products:,}")
    print(f"注文数: {args.orders:,}")
    print(f"1注文あたりの平均商品数: {args.items_per_order}")
    print(f"出力形式: {args.format}")
    print("=" * 70)
    print()
    
    # データ生成
    customers = generate_customers(args.customers)
    products = generate_products(args.products)
    orders = generate_orders(args.orders, args.customers, products, customers)
    order_items = generate_order_items(orders, products, args.items_per_order, args.max_order_items)
    
    print()
    print("=" * 70)
    print("データ生成完了")
    print("=" * 70)
    print(f"- 顧客: {len(customers):,}件")
    print(f"- 商品: {len(products):,}件")
    print(f"- 注文: {len(orders):,}件")
    print(f"- 注文明細: {len(order_items):,}件")
    print()
    
    # ファイル出力
    if args.format in ['csv', 'both']:
        print("CSVファイルを出力中...")
        write_csv(f'{args.output_dir}/customers.csv', customers,
                  ['customer_id', 'name', 'email', 'phone', 'address', 'city',
                   'prefecture', 'zip_code', 'registration_date'])
        write_csv(f'{args.output_dir}/products.csv', products,
                  ['product_id', 'name', 'category', 'brand', 'price',
                   'stock_quantity', 'description', 'created_at'])
        write_csv(f'{args.output_dir}/orders.csv', orders,
                  ['order_id', 'customer_id', 'order_date', 'total_amount',
                   'status', 'shipping_address', 'payment_method'])
        write_csv(f'{args.output_dir}/order_items.csv', order_items,
                  ['order_item_id', 'order_id', 'product_id', 'quantity',
                   'unit_price', 'subtotal'])
        print()
    
    if args.format in ['sql', 'both']:
        print("SQL INSERT文を出力中...")
        write_sql_insert(f'{args.output_dir}/insert_customers.sql', 'customers', customers,
                         ['customer_id', 'name', 'email', 'phone', 'address', 'city',
                          'prefecture', 'zip_code', 'registration_date'])
        write_sql_insert(f'{args.output_dir}/insert_products.sql', 'products', products,
                         ['product_id', 'name', 'category', 'brand', 'price',
                          'stock_quantity', 'description', 'created_at'])
        write_sql_insert(f'{args.output_dir}/insert_orders.sql', 'orders', orders,
                         ['order_id', 'customer_id', 'order_date', 'total_amount',
                          'status', 'shipping_address', 'payment_method'])
        write_sql_insert(f'{args.output_dir}/insert_order_items.sql', 'order_items', order_items,
                         ['order_item_id', 'order_id', 'product_id', 'quantity',
                          'unit_price', 'subtotal'])
        print()
    
    print("=" * 70)
    print("完了しました！")
    print("=" * 70)

if __name__ == '__main__':
    main()


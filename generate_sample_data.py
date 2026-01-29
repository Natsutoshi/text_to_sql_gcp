#!/usr/bin/env python3
"""
Eコマース店舗のサンプルデータ生成スクリプト
各テーブルに20レコードずつのサンプルデータを生成します
"""

import random
from datetime import datetime, timedelta
import csv

# サンプルデータの定義
CUSTOMER_NAMES = [
    "山田太郎", "佐藤花子", "鈴木一郎", "田中次郎", "渡辺三郎",
    "伊藤美咲", "中村健太", "小林さくら", "加藤大輔", "吉田麻衣",
    "高橋優子", "松本和也", "井上真由美", "木村拓也", "林直樹",
    "斎藤由美", "山本健一", "森田智子", "池田翔太", "前田美穂"
]

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

def generate_customers():
    """顧客データを生成（実在する日本の住所と郵便番号を使用）"""
    customers = []
    base_date = datetime(2023, 1, 1)
    
    for i in range(20):
        customer_id = i + 1
        name = CUSTOMER_NAMES[i]
        email = f"{name.lower().replace(' ', '')}{i+1}@{random.choice(EMAIL_DOMAINS)}"
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
        
        registration_date = base_date + timedelta(days=random.randint(0, 365))
        
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

def generate_products():
    """商品データを生成"""
    products = []
    base_date = datetime(2023, 1, 1)
    product_id = 1
    
    # 全カテゴリから商品を均等に選ぶ
    products_per_category = 20 // len(PRODUCT_CATEGORIES)  # カテゴリあたり2-3商品
    remaining = 20 % len(PRODUCT_CATEGORIES)  # 余り
    
    for idx, category in enumerate(PRODUCT_CATEGORIES):
        category_products = PRODUCT_NAMES[category]
        brands = BRANDS[category]
        
        # 余りは最初のカテゴリに分配
        num_products = products_per_category + (1 if idx < remaining else 0)
        num_products = min(num_products, len(category_products))
        
        selected_products = random.sample(category_products, num_products)
        
        for product_name in selected_products:
            if product_id > 20:
                break
                
            price = random.randint(500, 50000)
            stock_quantity = random.randint(0, 100)
            description = f"{product_name}の詳細説明です。高品質でおすすめの商品です。"
            created_at = base_date + timedelta(days=random.randint(0, 200))
            
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

def generate_orders(customers, products):
    """注文データを生成"""
    orders = []
    base_date = datetime(2024, 1, 1)
    
    for i in range(20):
        order_id = i + 1
        customer_id = random.randint(1, 20)
        order_date = base_date + timedelta(days=random.randint(0, 180))
        
        # 注文ステータスの分布を調整（deliveredが多い）
        status_weights = [0.1, 0.2, 0.2, 0.4, 0.1]
        status = random.choices(ORDER_STATUSES, weights=status_weights)[0]
        
        payment_method = random.choice(PAYMENT_METHODS)
        # 顧客の住所を取得
        customer = next(c for c in customers if c['customer_id'] == customer_id)
        shipping_address = customer['address']
        
        # 注文明細から合計金額を計算するため、一旦0に設定
        # 後でorder_items生成後に更新
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

def generate_order_items(orders, products):
    """注文明細データを生成"""
    order_items = []
    order_item_id = 1
    
    for order in orders:
        order_id = order['order_id']
        # 1注文あたり1-3商品
        num_items = random.randint(1, 3)
        selected_products = random.sample(products, min(num_items, len(products)))
        
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
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def write_sql_insert(filename, table_name, data, fieldnames):
    """SQL INSERT文を生成"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"-- {table_name}テーブルのサンプルデータ\n")
        f.write(f"INSERT INTO {table_name} ({', '.join(fieldnames)}) VALUES\n")
        
        for i, row in enumerate(data):
            values = []
            for field in fieldnames:
                value = row[field]
                if isinstance(value, str):
                    # SQLインジェクション対策
                    value = value.replace("'", "''")
                    values.append(f"'{value}'")
                elif value is None:
                    values.append("NULL")
                else:
                    values.append(str(value))
            
            comma = "," if i < len(data) - 1 else ";"
            f.write(f"  ({', '.join(values)}){comma}\n")

def main():
    print("サンプルデータを生成しています...")
    
    # データ生成
    customers = generate_customers()
    products = generate_products()
    orders = generate_orders(customers, products)
    order_items = generate_order_items(orders, products)
    
    # CSVファイル出力
    print("CSVファイルを生成しています...")
    write_csv('customers.csv', customers, 
              ['customer_id', 'name', 'email', 'phone', 'address', 'city', 
               'prefecture', 'zip_code', 'registration_date'])
    write_csv('products.csv', products,
              ['product_id', 'name', 'category', 'brand', 'price', 
               'stock_quantity', 'description', 'created_at'])
    write_csv('orders.csv', orders,
              ['order_id', 'customer_id', 'order_date', 'total_amount', 
               'status', 'shipping_address', 'payment_method'])
    write_csv('order_items.csv', order_items,
              ['order_item_id', 'order_id', 'product_id', 'quantity', 
               'unit_price', 'subtotal'])
    
    # SQL INSERT文出力
    print("SQL INSERT文を生成しています...")
    write_sql_insert('insert_customers.sql', 'customers', customers,
                     ['customer_id', 'name', 'email', 'phone', 'address', 'city', 
                      'prefecture', 'zip_code', 'registration_date'])
    write_sql_insert('insert_products.sql', 'products', products,
                     ['product_id', 'name', 'category', 'brand', 'price', 
                      'stock_quantity', 'description', 'created_at'])
    write_sql_insert('insert_orders.sql', 'orders', orders,
                     ['order_id', 'customer_id', 'order_date', 'total_amount', 
                      'status', 'shipping_address', 'payment_method'])
    write_sql_insert('insert_order_items.sql', 'order_items', order_items,
                     ['order_item_id', 'order_id', 'product_id', 'quantity', 
                      'unit_price', 'subtotal'])
    
    print("完了しました！")
    print(f"- 顧客: {len(customers)}件")
    print(f"- 商品: {len(products)}件")
    print(f"- 注文: {len(orders)}件")
    print(f"- 注文明細: {len(order_items)}件")

if __name__ == '__main__':
    main()


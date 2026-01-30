-- 顧客データを更新するSQL: BigqueryのGUIでScheduled Queryに設定の上実行してください

MERGE `text-to-sql-agent-485209.raw_data.customers` AS T
USING `text-to-sql-agent-485209.raw_data.temp_customers` AS S
ON T.customer_id = S.customer_id
-- 一致する行があるが、中身がどれか一つでも異なる場合のみ更新
WHEN MATCHED AND (
    T.name != S.name OR
    T.email != S.email OR
    T.phone != S.phone OR
    T.address != S.address OR
    T.city != S.city OR
    T.prefecture != S.prefecture OR
    T.zip_code != S.zip_code OR
    T.registration_date != S.registration_date
) THEN
  UPDATE SET 
    name = S.name,
    email = S.email,
    phone = S.phone,
    address = S.address,
    city = S.city,
    prefecture = S.prefecture,
    zip_code = S.zip_code,
    registration_date = S.registration_date
-- そもそも customer_id が存在しない場合は新規追加
WHEN NOT MATCHED THEN
  INSERT (customer_id, name, email, phone, address, city, prefecture, zip_code, registration_date)
  VALUES (S.customer_id, S.name, S.email, S.phone, S.address, S.city, S.prefecture, S.zip_code, S.registration_date)
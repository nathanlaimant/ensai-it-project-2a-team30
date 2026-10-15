INSERT INTO user(user_id, username, password_hash, email, role, is_active, created_at, updated_at, access_token) VALUES
(1, 'md', 'hash1', 'md@email.fr', 'ADMIN', TRUE, DATE_FORMAT("2026-09-28", "%D, %b %Y"), DATE_FORMAT("2026-09-28", "%D, %b %Y"), 'accesstoken1'),
(2, 'qk', 'hash2', 'qk@email.fr', 'ADMIN', TRUE, DATE_FORMAT("2026-09-28", "%D, %b %Y"), DATE_FORMAT("2026-09-28", "%D, %b %Y"), 'accesstoken2'),
(3, 'nl', 'hash3', 'nl@email.fr', 'ADMIN', TRUE, DATE_FORMAT("2026-09-28", "%D, %b %Y"), DATE_FORMAT("2026-09-28", "%D, %b %Y"), 'accesstoken3'),
(4, 'vn', 'hash4', 'vn@email.fr', 'ADMIN', TRUE, DATE_FORMAT("2026-09-28", "%D, %b %Y"), DATE_FORMAT("2026-09-28", "%D, %b %Y"), 'accesstoken4'),
(5, 'ap', 'hash5', 'ap@email.fr', 'ADMIN', TRUE, DATE_FORMAT("2026-09-28", "%D, %b %Y"), DATE_FORMAT("2026-09-28", "%D, %b %Y"), 'accesstoken5');

INSERT INTO vehicle_type (
    vehicle_type_id, form_factor, rider_capacity, cargo_volume_capacity,
    cargo_load_capacity, propulsion_type, max_range_meters, name, return_constraint
) VALUES
('dott_bicycle', 'bicycle', 1, NULL, NULL, 'electric_assist', 100000, 'Dott Bicycle', 'free_floating');

INSERT INTO station_information (
    station_id, name, short_name, lat, lon, adress,
    is_virtual_station, station_area, contact_phone, capacity, is_charging_station
) VALUES
('16bbf68d-685a-4799-9bba-8915f10700e0', 'id_38206', NULL, 48.87272566626918, 2.3543781376503787, NULL,
 TRUE, '{"region_id": "59668473-9a3b-47cc-99cb-a361e4ca72d4"}', NULL, 3, FALSE),
('b42cb6d7-0558-4589-ad71-63e374fdb784', 'id_34235', NULL, 48.82660892524964, 2.334670585820952, NULL,
 TRUE, '{"region_id": "59668473-9a3b-47cc-99cb-a361e4ca72d4"}', NULL, 3, FALSE),
('5770705c-cbb1-4baa-a1ca-eb40540b2f40', '17 RUE DU VIEUX COLOMBIER', NULL, 48.851759, 2.3306, NULL,
 TRUE, '{"region_id": "59668473-9a3b-47cc-99cb-a361e4ca72d4"}', NULL, 3, FALSE),
('74a3f9a1-70b0-4d9a-a1d1-bbb5c6948840', 'id_old844604G20081106092237', NULL, 48.83228438273518, 2.3210551613779056, NULL,
 TRUE, '{"region_id": "59668473-9a3b-47cc-99cb-a361e4ca72d4"}', NULL, 3, FALSE),
('cfc59b52-ba26-4b99-9925-4786e037800c', 'id_16615', NULL, 48.86736605114877, 2.3377172234556336, NULL,
 TRUE, '{"region_id": "59668473-9a3b-47cc-99cb-a361e4ca72d4"}', NULL, 3, FALSE);

 INSERT INTO station_virtual_capacity (station_id, vehicle_type_id, capacity) VALUES
('16bbf68d-685a-4799-9bba-8915f10700e0', 'dott_bicycle', 3),
('b42cb6d7-0558-4589-ad71-63e374fdb784', 'dott_bicycle', 3),
('5770705c-cbb1-4baa-a1ca-eb40540b2f40', 'dott_bicycle', 3),
('74a3f9a1-70b0-4d9a-a1d1-bbb5c6948840', 'dott_bicycle', 3),
('cfc59b52-ba26-4b99-9925-4786e037800c', 'dott_bicycle', 3);
-- ===============================================
-- 1. SYSTEM INFORMATION (from system_information.json)
-- ===============================================
INSERT INTO veloscope.system_information (system_id, language, name, timezone) VALUES
('Paris', 'en', 'Paris', 'Europe/Paris');

-- ===============================================
-- 2. STATION INFORMATION (from station_information.json)
-- ===============================================
INSERT INTO veloscope.station_information (station_id, name, short_name, lat, lon, capacity) VALUES
('213688169', 'Benjamin Godard - Victor Hugo', '16107', 48.865983, 2.275725, 35),
('19179944124', 'Hôpital Mondor', '40001', 48.798922410229, 2.4537451531298, 28),
('18795078746', 'Charcot - Benfleet', '32304', 48.878370277021, 2.440523876268, 28),
('36255', 'Toudouze - Clauzel', '9020', 48.87929591733507, 2.3373600840568547, 21),
('251039991', 'Cassini - Denfert-Rochereau', '14111', 48.837525839067, 2.3360354080796, 25);

-- ===============================================
-- 3. STATION STATUS (from station_status.json)
-- ===============================================
INSERT INTO veloscope.station_status (
    station_id,
    num_bikes_available,
    num_docks_available,
    operational_capacity,
    last_reported,
    vehicle_types_available,
    station_state
) VALUES
('213688169', 23, 11, 34, TO_TIMESTAMP(1792526423), '[{"mechanical": 16}, {"ebike": 7}]'::jsonb, 'FUNCTIONAL'),
('19179944124', 21, 7, 28, TO_TIMESTAMP(1792526596), '[{"mechanical": 12}, {"ebike": 9}]'::jsonb, 'FUNCTIONAL'),
('18795078746', 4, 25, 29, TO_TIMESTAMP(1792526599), '[{"mechanical": 1}, {"ebike": 3}]'::jsonb, 'FUNCTIONAL'),
('36255', 6, 15, 21, TO_TIMESTAMP(1792526434), '[{"mechanical": 4}, {"ebike": 2}]'::jsonb, 'FUNCTIONAL'),
('251039991', 2, 23, 25, TO_TIMESTAMP(1792526346), '[{"mechanical": 2}, {"ebike": 0}]'::jsonb, 'FUNCTIONAL');

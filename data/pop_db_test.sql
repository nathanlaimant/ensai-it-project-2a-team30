INSERT INTO veloscope."user" (username, password_hashed, email, role, is_active, access_token) VALUES
('md', 'hash1', 'md@email.fr', 'ADMIN', TRUE, 'accesstoken1'),
('qk', 'hash2', 'qk@email.fr', 'ADMIN', TRUE, 'accesstoken2'),
('nl', 'hash3', 'nl@email.fr', 'ADMIN', TRUE, 'accesstoken3'),
('vn', 'hash4', 'vn@email.fr', 'ADMIN', TRUE, 'accesstoken4'),
('ap', 'hash5', 'ap@email.fr', 'ADMIN', TRUE, 'accesstoken5');

INSERT INTO veloscope.station_information (
    station_id, name, short_name, lat, lon, capacity
) VALUES
('213688169', 'Benjamin Godard - Victor Hugo', '16107', 48.865983, 2.275725, 35),
('19179944124', 'Hôpital Mondor', '40001', 48.798922410229, 2.4537451531298, 28),
('18795078746', 'Charcot - Benfleet', '32304', 48.878370277021, 2.440523876268, 28),
('36255', 'Toudouze - Clauzel', '9020', 48.87929591733507, 2.3373600840568547, 21),
('251039991', 'Cassini - Denfert-Rochereau', '14111', 48.837525839067, 2.3360354080796, 25);

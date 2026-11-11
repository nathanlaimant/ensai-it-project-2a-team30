INSERT INTO veloscope."user" (username, password_hashed, email, role, is_active, access_token) VALUES
('md', 'af316ecb91a8ee7ae99210702b2d4758f30cdde3bf61e3d8e787d74681f90a6e', 'md@email.fr', 'ADMIN', TRUE, 'accesstoken1'),
('qk', 'e7bf382f6e5915b3f88619b866223ebf1d51c4c5321cccde2e9ff700a3259086', 'qk@email.fr', 'ADMIN', TRUE, 'accesstoken2'),
('nl', '42caa4abb7b60f8f914e5bfb8e6511d7d9bd9817de719b74251755d97fe97bf1', 'nl@email.fr', 'ADMIN', TRUE, 'accesstoken3'),
('vn', '1c27099b3b84b13d0e3fbd299ba93ae7853ec1d0d3a4e5daa89e68b7ad59d7cb', 'vn@email.fr', 'ADMIN', TRUE, 'accesstoken4'),
('ap', '7da450ab64a26820e56dd73cd346950d656e60a20dba00bd4be9ced75ba7cdef', 'ap@email.fr', 'ADMIN', TRUE, 'accesstoken5');

-- Password used (non-hashed) : 'hash1', 'hash2', 'hash3', 'hash4', 'hash5' respectively

INSERT INTO veloscope_test.station_information (
    station_id, name, short_name, lat, lon, capacity
) VALUES
('213688169', 'Benjamin Godard - Victor Hugo', '16107', 48.865983, 2.275725, 35),
('19179944124', 'Hôpital Mondor', '40001', 48.798922410229, 2.4537451531298, 28),
('18795078746', 'Charcot - Benfleet', '32304', 48.878370277021, 2.440523876268, 28),
('36255', 'Toudouze - Clauzel', '9020', 48.87929591733507, 2.3373600840568547, 21),
('251039991', 'Cassini - Denfert-Rochereau', '14111', 48.837525839067, 2.3360354080796, 25);

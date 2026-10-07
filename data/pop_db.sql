INSERT INTO user(user_id, username, password_hash, email, role, is_active, created_at, updated_at, access_token) VALUES
(1, 'md', 'hash1', 'md@email.fr', 'ADMIN', TRUE, DATE_FORMAT("2026-09-28", "%D, %b %Y"), DATE_FORMAT("2026-09-28", "%D, %b %Y"), 'accesstoken1'),
(2, 'qk', 'hash2', 'qk@email.fr', 'ADMIN', TRUE, DATE_FORMAT("2026-09-28", "%D, %b %Y"), DATE_FORMAT("2026-09-28", "%D, %b %Y"), 'accesstoken2'),
(3, 'nl', 'hash3', 'nl@email.fr', 'ADMIN', TRUE, DATE_FORMAT("2026-09-28", "%D, %b %Y"), DATE_FORMAT("2026-09-28", "%D, %b %Y"), 'accesstoken3'),
(4, 'vn', 'hash4', 'vn@email.fr', 'ADMIN', TRUE, DATE_FORMAT("2026-09-28", "%D, %b %Y"), DATE_FORMAT("2026-09-28", "%D, %b %Y"), 'accesstoken4'),
(5, 'ap', 'hash5', 'ap@email.fr', 'ADMIN', TRUE, DATE_FORMAT("2026-09-28", "%D, %b %Y"), DATE_FORMAT("2026-09-28", "%D, %b %Y"), 'accesstoken5');

--  USER ACCOUNTS
-- Creates the test environment. Emma is the target; others provide ranking competition[cite: 5].
INSERT INTO users (username, hash, cash) VALUES 
('emma', 'pbkdf2:sha256:250000$examplehash1', 100000.00),
('high_roller', 'pbkdf2:sha256:250000$examplehash2', 500000.00),
('new_user', 'pbkdf2:sha256:250000$examplehash3', 10000.00),
('stale_user', 'pbkdf2:sha256:250000$examplehash4', 50000.00);

-- EMMA'S DATA
-- Tests that the query selects the latest snap_id (100k total) rather than adding snapshots together[cite: 4].
INSERT INTO balance_snapshots (user_id, snap_datetime, portfolio_value, cash_balance) VALUES 
(1, '2026-04-30 10:00:00', 5000.00, 95000.00),
(1, '2026-05-02 12:00:00', 7500.00, 92500.00);

-- STALE SNAPSHOTS
-- Verifies the ranker ignores older history for a user if newer data exists.
INSERT INTO balance_snapshots (user_id, snap_datetime, portfolio_value, cash_balance) VALUES 
(4, '2026-04-20 09:00:00', 20000.00, 40000.00),
(4, '2026-04-25 09:00:00', 30000.00, 30000.00);

-- COMPETITION DATA
-- Sets up ranking. High Roller takes Rank 1. New User tests 0.00 portfolio values[cite: 3, 4].
INSERT INTO balance_snapshots (user_id, snap_datetime, portfolio_value, cash_balance) VALUES 
(2, '2026-05-02 12:00:00', 250000.00, 500000.00), 
(3, '2026-05-02 12:00:00', 0.00, 10000.00),
(4, '2026-05-02 09:00:00', 31000.00, 30000.00);
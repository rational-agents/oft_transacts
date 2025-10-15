/*
decription: idempotent script to create the OFT schema
*/

-- 1. Drop all tables in order 
-- to avoid foreign key constraints
DROP VIEW IF EXISTS account_balances;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS transacts;
DROP TABLE IF EXISTS accounts; 
DROP TABLE IF EXISTS users; 

-- 2. Create all tables in order

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,  -- Store as lowercase for case-insensitive matching
    username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accounts (
    account_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    account_name TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    checkpoint_balance INTEGER NOT NULL,
    checkpoint_timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE transacts (
    trans_id INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL,
    occurred_at TIMESTAMP NOT NULL,
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0),
    direction TEXT NOT NULL CHECK (direction IN ('credit','debit')),
    trans_status TEXT NOT NULL DEFAULT 'posted' CHECK (trans_status IN ('posted','deleted')),
    notes TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

-- 3. Create views

-- View: balance = checkpoint + net(posted credits - debits) since checkpoint
CREATE VIEW account_balances AS
SELECT
    a.account_id,
    a.account_name,
    a.currency,
    a.checkpoint_balance
        + COALESCE(
            SUM(
                CASE t.direction
                    WHEN 'credit' THEN t.amount_cents
                    ELSE -t.amount_cents
                END
            ), 0
        ) AS balance
FROM 
    accounts AS a
    LEFT JOIN transacts AS t ON t.account_id = a.account_id
        AND t.trans_status = 'posted'
        AND t.occurred_at >= a.checkpoint_timestamp
GROUP BY
    a.account_id,
    a.account_name,
    a.currency,
    a.checkpoint_balance,
    a.checkpoint_timestamp;
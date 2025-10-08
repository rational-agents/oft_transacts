/*
description: seed data for the OFT schema
    start without transactions in order to ensure 
    resilience of the implementation.
*/
PRAGMA foreign_keys = ON;

-- seed the user table with a single user
INSERT INTO users (email, username) VALUES
('john.kelly@rational-agents.ai', 'john kelly');

-- seed the account table with a checking account for jk in USD pennies equivalent to $500
INSERT INTO accounts (
    user_id,
    account_name, 
    currency, 
    checkpoint_balance, 
    checkpoint_timestamp
    )
SELECT
    user_id,
    'chase checking',
    'USD',
    50000,
    CURRENT_TIMESTAMP
FROM
    users
WHERE 
    email = 'john.kelly@rational-agents.ai';

-- seed the account table with crypto account for jk in SATs equivalent to 1 bitcoin
INSERT INTO accounts (
    user_id,
    account_name, 
    currency, 
    checkpoint_balance, 
    checkpoint_timestamp
    )
SELECT
    user_id,
    'crypto',
    'BTC',
    100000000,
    CURRENT_TIMESTAMP
FROM
    users
WHERE 
    email = 'john.kelly@rational-agents.ai';

-- no transactions to seed
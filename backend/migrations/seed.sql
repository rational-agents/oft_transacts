/*
description: seed data for the OFT schema
    start without transactions in order to ensure 
    resilience of the implementation.
*/
PRAGMA foreign_keys = ON;

-- seed the user table with a single user
INSERT INTO users (email, username) VALUES
('jkelly.admin@gmail.com', 'john kelly');

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
    'checking',
    'USD',
    50000,
    CURRENT_TIMESTAMP
FROM
    users
WHERE 
    email = 'jkelly.admin@gmail.com';

-- no transactions to seed
-- First, let's see all payments
SELECT 
    payment_id,
    invoice_number,
    amount,
    status,
    TO_CHAR(due_date, 'Mon DD, YYYY') as due_date,
    TO_CHAR(paid_at, 'Mon DD, YYYY') as paid_at,
    TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') as created_at
FROM subscription_payments
ORDER BY created_at;

-- Delete duplicate payments, keeping only the oldest one
DELETE FROM subscription_payments
WHERE payment_id NOT IN (
    SELECT MIN(payment_id)
    FROM subscription_payments
    GROUP BY subscription_id, invoice_number
);

-- Verify only one payment remains
SELECT 
    payment_id,
    invoice_number,
    amount,
    status,
    TO_CHAR(due_date, 'Mon DD, YYYY') as due_date,
    TO_CHAR(paid_at, 'Mon DD, YYYY') as paid_at
FROM subscription_payments
ORDER BY created_at;

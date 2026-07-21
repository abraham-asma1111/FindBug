-- Update all pending subscription payments to paid status
UPDATE subscription_payments
SET 
    status = 'paid',
    paid_at = period_start + INTERVAL '5 days',
    payment_method = 'bank_transfer',
    gateway_transaction_id = 'TXN-' || UPPER(SUBSTRING(payment_id::text, 1, 12))
WHERE status = 'pending';

-- Verify the update
SELECT 
    invoice_number,
    amount,
    currency,
    status,
    TO_CHAR(period_start, 'Mon DD, YYYY') as period_start,
    TO_CHAR(period_end, 'Mon DD, YYYY') as period_end,
    TO_CHAR(due_date, 'Mon DD, YYYY') as due_date,
    TO_CHAR(paid_at, 'Mon DD, YYYY') as paid_at,
    payment_method
FROM subscription_payments
ORDER BY created_at;

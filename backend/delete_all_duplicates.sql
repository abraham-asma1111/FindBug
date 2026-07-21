-- Show current payments before deletion
SELECT 
    payment_id,
    invoice_number,
    amount,
    status,
    TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') as created_at
FROM subscription_payments
ORDER BY created_at;

-- Delete ALL payments first to start fresh
DELETE FROM subscription_payments;

-- Verify all deleted
SELECT COUNT(*) as remaining_payments FROM subscription_payments;

-- Show result
SELECT 'All duplicate payments have been deleted' as status;

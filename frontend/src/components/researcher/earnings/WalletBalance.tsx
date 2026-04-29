'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import Spinner from '@/components/ui/Spinner';
import Modal from '@/components/ui/Modal';

interface WalletBalanceData {
  balance: number;
  reserved_balance: number;
  available_balance: number;
  currency: string;
}

export default function WalletBalance() {
  const [isWithdrawModalOpen, setIsWithdrawModalOpen] = useState(false);
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [withdrawError, setWithdrawError] = useState('');

  const { data: balanceData, isLoading, refetch } = useApiQuery<WalletBalanceData>(
    '/wallet/balance',
    { 
      enabled: true,
      retry: 0, // Don't retry on errors
    }
  );

  const { mutate: requestWithdrawal, isLoading: isWithdrawing } = useApiMutation(
    '/wallet/withdraw',
    'POST',
    {
      onSuccess: () => {
        setIsWithdrawModalOpen(false);
        setWithdrawAmount('');
        setWithdrawError('');
        refetch();
      },
      onError: (error: any) => {
        if (error.message?.includes('KYC verification required')) {
          setWithdrawError('KYC verification is required to withdraw funds. Please complete your KYC verification first.');
        } else {
          setWithdrawError(error.message || 'Failed to process withdrawal');
        }
      },
    }
  );

  const handleWithdraw = () => {
    setWithdrawError('');
    
    const amount = parseFloat(withdrawAmount);
    
    if (isNaN(amount) || amount <= 0) {
      setWithdrawError('Please enter a valid amount');
      return;
    }
    
    if (amount < 100) {
      setWithdrawError('Minimum withdrawal amount is 100 ETB');
      return;
    }
    
    if (amount > (balanceData?.available_balance || 0)) {
      setWithdrawError('Insufficient balance');
      return;
    }

    requestWithdrawal({
      amount,
      payment_method: 'bank_transfer',
      account_details: {},
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-ET', {
      style: 'currency',
      currency: 'ETB',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  if (isLoading) {
    return (
      <div className="rounded-2xl bg-[#faf6f1] p-8 flex justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <>
      <div className="rounded-2xl bg-gradient-to-br from-[#ef2330] to-[#d41f2c] p-8 text-white">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Total Balance */}
          <div>
            <p className="text-sm font-medium text-white/80 mb-2">Total Balance</p>
            <p className="text-3xl font-bold">
              {formatCurrency(balanceData?.balance || 0)}
            </p>
          </div>

          {/* Reserved */}
          <div>
            <p className="text-sm font-medium text-white/80 mb-2">Reserved</p>
            <p className="text-2xl font-semibold">
              {formatCurrency(balanceData?.reserved_balance || 0)}
            </p>
            <p className="text-xs text-white/60 mt-1">Pending payouts</p>
          </div>

          {/* Available */}
          <div>
            <p className="text-sm font-medium text-white/80 mb-2">Available for Withdrawal</p>
            <p className="text-2xl font-semibold">
              {formatCurrency(balanceData?.available_balance || 0)}
            </p>
            <button
              onClick={() => setIsWithdrawModalOpen(true)}
              disabled={(balanceData?.available_balance || 0) < 100}
              className="mt-3 inline-flex rounded-full bg-white dark:bg-[#111111] px-6 py-2 text-sm font-semibold text-[#ef2330] transition hover:bg-white/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Request Withdrawal
            </button>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="mt-8 pt-6 border-t border-white/20 grid grid-cols-3 gap-4">
          <div>
            <p className="text-xs text-white/60 mb-1">This Month</p>
            <p className="text-lg font-semibold">ETB 0.00</p>
          </div>
          <div>
            <p className="text-xs text-white/60 mb-1">Last Payout</p>
            <p className="text-lg font-semibold">-</p>
          </div>
          <div>
            <p className="text-xs text-white/60 mb-1">Total Earned</p>
            <p className="text-lg font-semibold">{formatCurrency(balanceData?.balance || 0)}</p>
          </div>
        </div>
      </div>

      {/* Withdrawal Modal */}
      <Modal
        isOpen={isWithdrawModalOpen}
        onClose={() => {
          setIsWithdrawModalOpen(false);
          setWithdrawAmount('');
          setWithdrawError('');
        }}
        size="md"
      >
        <div className="space-y-5">
          <div>
            <h2 className="text-xl font-bold text-[#2d2a26]">Request Withdrawal</h2>
            <p className="text-sm text-[#6d6760] mt-1">
              Withdraw funds from your wallet to your bank account
            </p>
          </div>

          {withdrawError && (
            <div className="rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
              <p className="font-semibold">Error</p>
              <p className="mt-1">{withdrawError}</p>
            </div>
          )}

          <div className="rounded-2xl bg-[#faf6f1] p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-2">
              Available Balance
            </p>
            <p className="text-2xl font-bold text-[#2d2a26]">
              {formatCurrency(balanceData?.available_balance || 0)}
            </p>
          </div>

          <div className="rounded-2xl bg-[#faf6f1] p-5">
            <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
              Withdrawal Amount (ETB) *
            </label>
            <input
              type="number"
              placeholder="Enter amount (min. 100 ETB)"
              value={withdrawAmount}
              onChange={(e) => setWithdrawAmount(e.target.value)}
              min="100"
              step="0.01"
              className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] placeholder:text-[#8b8177] focus:border-[#c8bfb6] focus:outline-none"
            />
            <p className="mt-2 text-xs text-[#6d6760]">
              Minimum withdrawal: 100 ETB
            </p>
          </div>

          <div className="rounded-2xl bg-[#eef5fb] border border-[#b8d4f1] p-4 text-sm text-[#2d78a8]">
            <p className="font-semibold mb-1">ℹ️ Important Information</p>
            <ul className="list-disc list-inside space-y-1 text-xs">
              <li>Withdrawals are processed within 3-5 business days</li>
              <li>You must have a verified KYC status to withdraw</li>
              <li>A default payout method must be set</li>
            </ul>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-[#e6ddd4]">
            <button
              onClick={() => {
                setIsWithdrawModalOpen(false);
                setWithdrawAmount('');
                setWithdrawError('');
              }}
              className="inline-flex rounded-full border border-[#d8d0c8] px-6 py-2.5 text-sm font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
            >
              Cancel
            </button>
            <button
              onClick={handleWithdraw}
              disabled={isWithdrawing || !withdrawAmount}
              className="inline-flex items-center gap-2 rounded-full bg-[#ef2330] px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-[#d41f2c] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isWithdrawing ? (
                <>
                  <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </>
              ) : (
                'Submit Request'
              )}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}

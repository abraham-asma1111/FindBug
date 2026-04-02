'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import Spinner from '@/components/ui/Spinner';
import Badge from '@/components/ui/Badge';

interface Transaction {
  id: string;
  transaction_type: string;
  amount: number;
  balance_after: number;
  created_at: string;
  reference_type?: string;
  reference_id?: string;
  description?: string;
  status?: string;
}

interface TransactionListProps {
  limit?: number;
  showFilters?: boolean;
}

export default function TransactionList({ limit = 50, showFilters = true }: TransactionListProps) {
  const [filters, setFilters] = useState({
    type: '',
    search: '',
  });

  const { data: transactionsData, isLoading, isError } = useApiQuery<{ transactions: Transaction[]; total: number }>(
    `/wallet/transactions?limit=${limit}&offset=0`,
    { enabled: true }
  );

  const transactions = transactionsData?.transactions || [];

  const filteredTransactions = transactions.filter(transaction => {
    if (filters.type && transaction.transaction_type !== filters.type) return false;
    if (filters.search && !transaction.description?.toLowerCase().includes(filters.search.toLowerCase())) return false;
    return true;
  });

  const getTransactionIcon = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'credit':
      case 'bounty':
      case 'bonus':
        return (
          <svg className="w-5 h-5 text-[#10b981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        );
      case 'debit':
      case 'withdrawal':
        return (
          <svg className="w-5 h-5 text-[#ef4444]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5 text-[#6b7280]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
        );
    }
  };

  const getTransactionColor = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'credit':
      case 'bounty':
      case 'bonus':
        return 'text-[#10b981]';
      case 'debit':
      case 'withdrawal':
        return 'text-[#ef4444]';
      default:
        return 'text-[#6b7280]';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-ET', {
      style: 'currency',
      currency: 'ETB',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
        Failed to load transactions. Please try again.
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* Filters */}
      {showFilters && (
        <div className="rounded-2xl bg-[#faf6f1] p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input
              type="text"
              placeholder="Search transactions..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="rounded-xl border border-[#d8d0c8] bg-white px-4 py-2 text-sm text-[#2d2a26] placeholder:text-[#8b8177] focus:border-[#c8bfb6] focus:outline-none"
            />
            <select
              value={filters.type}
              onChange={(e) => setFilters({ ...filters, type: e.target.value })}
              className="rounded-xl border border-[#d8d0c8] bg-white px-4 py-2 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
            >
              <option value="">All Types</option>
              <option value="credit">Credits</option>
              <option value="debit">Debits</option>
              <option value="bounty">Bounties</option>
              <option value="bonus">Bonuses</option>
              <option value="withdrawal">Withdrawals</option>
            </select>
          </div>
        </div>
      )}

      {/* Transactions List */}
      {filteredTransactions.length === 0 ? (
        <div className="rounded-2xl bg-[#faf6f1] p-8 text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#8b8177]">
            No transactions found
          </p>
          <p className="mt-2 text-sm text-[#6d6760]">
            {transactions.length === 0
              ? "You don't have any transactions yet. Start earning by submitting vulnerability reports."
              : 'No transactions match your current filters.'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredTransactions.map((transaction) => (
            <div
              key={transaction.id}
              className="rounded-2xl bg-[#faf6f1] p-5 flex items-center justify-between"
            >
              <div className="flex items-center gap-4">
                {/* Icon */}
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-white flex items-center justify-center border border-[#e6ddd4]">
                  {getTransactionIcon(transaction.transaction_type)}
                </div>

                {/* Details */}
                <div>
                  <p className="text-sm font-semibold text-[#2d2a26] capitalize">
                    {transaction.transaction_type.replace('_', ' ')}
                  </p>
                  <p className="text-xs text-[#6d6760] mt-1">
                    {formatDate(transaction.created_at)}
                  </p>
                  {transaction.description && (
                    <p className="text-xs text-[#8b8177] mt-1">
                      {transaction.description}
                    </p>
                  )}
                </div>
              </div>

              {/* Amount */}
              <div className="text-right">
                <p className={`text-lg font-bold ${getTransactionColor(transaction.transaction_type)}`}>
                  {transaction.transaction_type.toLowerCase() === 'debit' || 
                   transaction.transaction_type.toLowerCase() === 'withdrawal' ? '-' : '+'}
                  {formatCurrency(transaction.amount)}
                </p>
                <p className="text-xs text-[#6d6760] mt-1">
                  Balance: {formatCurrency(transaction.balance_after)}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination Info */}
      {filteredTransactions.length > 0 && (
        <div className="text-center text-sm text-[#6d6760]">
          Showing {filteredTransactions.length} of {transactionsData?.total || 0} transactions
        </div>
      )}
    </div>
  );
}

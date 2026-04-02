'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import SectionCard from '@/components/dashboard/SectionCard';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import WalletBalance from '@/components/researcher/earnings/WalletBalance';
import TransactionList from '@/components/researcher/earnings/TransactionList';
import PayoutMethods from '@/components/researcher/earnings/PayoutMethods';
import KYCStatus from '@/components/researcher/earnings/KYCStatus';

export default function EarningsPage() {
  const user = useAuthStore((state) => state.user);
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Earnings"
          subtitle="Manage your wallet, transactions, and payouts"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Researcher Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          {/* Tabs */}
          <div className="mb-6 flex justify-center">
            <div className="flex gap-6">
              <button
                onClick={() => setActiveTab('overview')}
                className={`inline-flex items-center gap-2 rounded-full px-6 py-2.5 text-sm font-semibold transition ${
                  activeTab === 'overview'
                    ? 'bg-[#ef2330] text-white'
                    : 'bg-[#f3ede6] text-[#5f5851] hover:bg-[#eadfd3]'
                }`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('transactions')}
                className={`inline-flex items-center gap-2 rounded-full px-6 py-2.5 text-sm font-semibold transition ${
                  activeTab === 'transactions'
                    ? 'bg-[#ef2330] text-white'
                    : 'bg-[#f3ede6] text-[#5f5851] hover:bg-[#eadfd3]'
                }`}
              >
                Transactions
              </button>
              <button
                onClick={() => setActiveTab('payout-methods')}
                className={`inline-flex items-center gap-2 rounded-full px-6 py-2.5 text-sm font-semibold transition ${
                  activeTab === 'payout-methods'
                    ? 'bg-[#ef2330] text-white'
                    : 'bg-[#f3ede6] text-[#5f5851] hover:bg-[#eadfd3]'
                }`}
              >
                Payout Methods
              </button>
              <button
                onClick={() => setActiveTab('kyc')}
                className={`inline-flex items-center gap-2 rounded-full px-6 py-2.5 text-sm font-semibold transition ${
                  activeTab === 'kyc'
                    ? 'bg-[#ef2330] text-white'
                    : 'bg-[#f3ede6] text-[#5f5851] hover:bg-[#eadfd3]'
                }`}
              >
                KYC Status
              </button>
            </div>
          </div>

          {/* Content */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <WalletBalance />
              
              <SectionCard
                title="Recent Transactions"
                description="Your latest earnings and withdrawals"
                headerAlign="center"
              >
                <TransactionList limit={5} showFilters={false} />
              </SectionCard>
            </div>
          )}

          {activeTab === 'transactions' && (
            <SectionCard
              title="Transaction History"
              description="All your earnings, bonuses, and withdrawals"
              headerAlign="center"
            >
              <TransactionList limit={50} showFilters={true} />
            </SectionCard>
          )}

          {activeTab === 'payout-methods' && (
            <SectionCard
              title="Payout Methods"
              description="Manage your bank accounts and payment methods"
              headerAlign="center"
            >
              <PayoutMethods />
            </SectionCard>
          )}

          {activeTab === 'kyc' && (
            <SectionCard
              title="KYC Verification"
              description="Complete your identity verification to enable withdrawals"
              headerAlign="center"
            >
              <KYCStatus />
            </SectionCard>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}

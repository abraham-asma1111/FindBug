'use client';

import { useState } from 'react';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import Modal from '@/components/ui/Modal';
import Input from '@/components/ui/Input';
import Alert from '@/components/ui/Alert';

export default function OrganizationWalletPage() {
  const user = useAuthStore((state) => state.user);
  const [isRechargeModalOpen, setIsRechargeModalOpen] = useState(false);
  const [rechargeAmount, setRechargeAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('bank_transfer');
  const [error, setError] = useState('');

  // Fetch wallet balance
  const { data: walletData, isLoading: isLoadingWallet, refetch } = useApiQuery(
    '/wallet/balance'
  );

  // Fetch transactions
  const { data: transactionsData, isLoading: isLoadingTransactions } = useApiQuery(
    '/wallet/transactions?limit=20'
  );

  // Recharge mutation
  const { mutate: rechargeWallet, isLoading: isRecharging } = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      setIsRechargeModalOpen(false);
      setRechargeAmount('');
      setError('');
      refetch();
    },
    onError: (error: any) => {
      setError(error.message || 'Failed to recharge wallet');
    },
  });

  const handleRecharge = () => {
    const amount = parseFloat(rechargeAmount);
    
    if (!amount || amount < 1000) {
      setError('Minimum recharge amount is 1000 ETB');
      return;
    }

    rechargeWallet({
      endpoint: `/wallet/recharge?amount=${amount}&payment_method=${paymentMethod}`
    });
  };

  const balance = walletData?.balance || 0;
  const availableBalance = walletData?.available_balance || 0;
  const reservedBalance = walletData?.reserved_balance || 0;
  const transactions = transactionsData?.transactions || [];

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user ? (
        <PortalShell
          user={user}
          title="Wallet"
          subtitle="Manage your organization's wallet and fund bounty programs"
          navItems={getPortalNavItems(user.role)}
          headerAlign="center"
          eyebrowText="Organization Portal"
          eyebrowClassName="text-xl tracking-[0.18em]"
        >
          <div className="space-y-6">
            {/* Wallet Balance Card */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">Wallet Balance</h2>
                <Button
                  onClick={() => setIsRechargeModalOpen(true)}
                  variant="primary"
                >
                  Recharge Wallet
                </Button>
              </div>

              {isLoadingWallet ? (
                <div className="text-gray-400">Loading wallet balance...</div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <div className="text-sm text-gray-400 mb-1">Total Balance</div>
                    <div className="text-3xl font-bold text-white">
                      {balance.toLocaleString()} ETB
                    </div>
                  </div>

                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <div className="text-sm text-gray-400 mb-1">Available Balance</div>
                    <div className="text-3xl font-bold text-green-400">
                      {availableBalance.toLocaleString()} ETB
                    </div>
                  </div>

                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <div className="text-sm text-gray-400 mb-1">Reserved Balance</div>
                    <div className="text-3xl font-bold text-yellow-400">
                      {reservedBalance.toLocaleString()} ETB
                    </div>
                  </div>
                </div>
              )}

              <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                <div className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-blue-400 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="text-sm text-gray-300">
                    <p className="font-semibold mb-1">About Wallet Balance</p>
                    <p>You need sufficient wallet balance to publish bounty programs. The minimum required balance is equal to your program's critical tier reward amount.</p>
                  </div>
                </div>
              </div>
            </Card>

            {/* Transaction History */}
            <Card className="p-6">
              <h2 className="text-2xl font-bold text-white mb-6">Transaction History</h2>

              {isLoadingTransactions ? (
                <div className="text-gray-400">Loading transactions...</div>
              ) : transactions.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  <svg className="w-16 h-16 mx-auto mb-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p>No transactions yet</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-700">
                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Date</th>
                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Type</th>
                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Reference</th>
                        <th className="text-right py-3 px-4 text-sm font-semibold text-gray-400">Amount</th>
                        <th className="text-right py-3 px-4 text-sm font-semibold text-gray-400">Balance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {transactions.map((tx: any) => (
                        <tr key={tx.id} className="border-b border-gray-800 hover:bg-gray-800/30">
                          <td className="py-3 px-4 text-sm text-gray-300">
                            {new Date(tx.created_at).toLocaleDateString()}
                          </td>
                          <td className="py-3 px-4">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              tx.transaction_type === 'credit' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
                            }`}>
                              {tx.transaction_type === 'credit' ? 'Credit' : 'Debit'}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-sm text-gray-400">
                            {tx.reference_type || 'N/A'}
                          </td>
                          <td className={`py-3 px-4 text-sm text-right font-semibold ${
                            tx.transaction_type === 'credit' ? 'text-green-400' : 'text-red-400'
                          }`}>
                            {tx.transaction_type === 'credit' ? '+' : '-'}{tx.amount.toLocaleString()} ETB
                          </td>
                          <td className="py-3 px-4 text-sm text-right text-gray-300">
                            {tx.balance_after.toLocaleString()} ETB
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          </div>

          {/* Recharge Modal */}
          <Modal
            isOpen={isRechargeModalOpen}
            onClose={() => {
              setIsRechargeModalOpen(false);
              setError('');
              setRechargeAmount('');
            }}
            title="Recharge Wallet"
          >
            <div className="space-y-4">
              {error && (
                <Alert variant="error" onClose={() => setError('')}>
                  {error}
                </Alert>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Amount (ETB)
                </label>
                <Input
                  type="number"
                  value={rechargeAmount}
                  onChange={(e) => setRechargeAmount(e.target.value)}
                  placeholder="Enter amount (minimum 1000 ETB)"
                  min="1000"
                  step="100"
                />
                <p className="mt-1 text-xs text-gray-400">Minimum recharge: 1,000 ETB</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Payment Method
                </label>
                <select
                  value={paymentMethod}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="bank_transfer">Bank Transfer</option>
                  <option value="telebirr">Telebirr</option>
                  <option value="cbe_birr">CBE Birr</option>
                </select>
              </div>

              <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                <div className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-yellow-400 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <div className="text-sm text-gray-300">
                    <p className="font-semibold mb-1">Payment Instructions</p>
                    <p>After clicking "Recharge", you'll receive payment instructions. Please complete the payment within 24 hours.</p>
                  </div>
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  onClick={() => {
                    setIsRechargeModalOpen(false);
                    setError('');
                    setRechargeAmount('');
                  }}
                  variant="secondary"
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleRecharge}
                  variant="primary"
                  className="flex-1"
                  disabled={isRecharging || !rechargeAmount}
                >
                  {isRecharging ? 'Processing...' : 'Recharge'}
                </Button>
              </div>
            </div>
          </Modal>
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}

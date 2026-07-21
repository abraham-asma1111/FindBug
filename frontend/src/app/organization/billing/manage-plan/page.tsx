'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import { api } from '@/lib/api';

interface Subscription {
  subscription_id: string;
  tier: string;
  status: string;
  subscription_fee: number;
  currency: string;
}

interface PricingTier {
  id: string;
  name: string;
  tier: string;
  price: number;
  billingCycle: string;
  description: string;
  features: string[];
  popular?: boolean;
  current?: boolean;
}

export default function ManagePlanPage() {
  const user = useAuthStore((state) => state.user);
  const router = useRouter();
  const [isMounted, setIsMounted] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelReason, setCancelReason] = useState('');
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedTier, setSelectedTier] = useState<string>('');
  const [paymentMethod, setPaymentMethod] = useState<'wallet' | 'manual'>('wallet');

  useEffect(() => {
    document.documentElement.classList.add('dark');
    setIsMounted(true);
  }, []);

  // Fetch current subscription
  const { data: subscriptionData, refetch: refetchSubscription, isError: subscriptionError, isLoading: subscriptionLoading } = useApiQuery<Subscription>({
    endpoint: isMounted ? '/subscriptions/current' : undefined,
    enabled: isMounted,
    retry: 0, // Don't retry on 404
    onError: (error) => {
      console.log('[ManagePlan] Subscription query error:', error.message);
    },
  });

  // Fetch wallet balance
  const { data: walletData } = useApiQuery<{ balance: number; available_balance: number; currency: string }>({
    endpoint: isMounted ? '/wallet/balance' : undefined,
    enabled: isMounted,
  });

  // Debug logging
  useEffect(() => {
    console.log('[ManagePlan] State:', {
      isMounted,
      subscriptionLoading,
      subscriptionError,
      hasData: !!subscriptionData,
    });
  }, [isMounted, subscriptionLoading, subscriptionError, subscriptionData]);

  // Change plan mutation
  const changePlanMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      alert(subscriptionData ? 'Plan changed successfully! Your new plan is now active.' : 'Subscription created successfully! Welcome to your new plan.');
      refetchSubscription();
    },
    onError: (error) => {
      alert(`Failed to ${subscriptionData ? 'change plan' : 'create subscription'}: ${error.message}`);
    },
  });

  // Cancel subscription mutation
  const cancelSubscriptionMutation = useApiMutation({
    method: 'POST',
    onSuccess: () => {
      alert('Subscription cancelled successfully. You can now choose a new plan.');
      setShowCancelModal(false);
      setCancelReason('');
      // Refetch to update UI
      refetchSubscription();
    },
    onError: (error) => {
      alert(`Failed to cancel subscription: ${error.message}`);
    },
  });

  // Pricing tiers (hardcoded for now - can be fetched from API later)
  const pricingTiers: PricingTier[] = [
    {
      id: 'basic',
      name: 'Basic',
      tier: 'basic',
      price: 15000,
      billingCycle: 'per 4 months',
      description: 'Perfect for small teams getting started with bug bounty programs',
      features: [
        'Up to 3 active programs',
        'Up to 50 researchers',
        'Basic analytics',
        'Email support',
        'Standard response time',
        'Community access',
      ],
      current: subscriptionData?.tier?.toLowerCase() === 'basic',
    },
    {
      id: 'professional',
      name: 'Professional',
      tier: 'professional',
      price: 25000,
      billingCycle: 'per 4 months',
      description: 'For growing organizations with multiple security programs',
      features: [
        'Up to 10 active programs',
        'Up to 200 researchers',
        'Advanced analytics & reporting',
        'Priority email & chat support',
        'PTaaS integration',
        'API access',
        'Custom branding',
        'Dedicated account manager',
      ],
      popular: true,
      current: subscriptionData?.tier?.toLowerCase() === 'professional',
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      tier: 'enterprise',
      price: 50000,
      billingCycle: 'per 4 months',
      description: 'For large enterprises with complex security needs',
      features: [
        'Unlimited active programs',
        'Unlimited researchers',
        'Enterprise analytics & insights',
        '24/7 priority support',
        'PTaaS + Code Review + AI Red Teaming',
        'Full API access',
        'White-label solution',
        'SSO & advanced security',
        'Custom integrations',
        'Dedicated security team',
      ],
      current: subscriptionData?.tier?.toLowerCase() === 'enterprise',
    },
  ];

  const handleSelectPlan = async (tier: string) => {
    console.log('[handleSelectPlan] Called with tier:', tier);
    const newTier = tier.toLowerCase();

    // Case 1: No subscription exists - Show payment modal
    if (!subscriptionData) {
      console.log('[handleSelectPlan] No subscription exists, showing payment modal');
      setSelectedTier(newTier);
      setShowPaymentModal(true);
      return;
    }

    // Case 2: Subscription exists - Change plan
    const currentTier = subscriptionData.tier.toLowerCase();

    if (currentTier === newTier) {
      alert('You are already on this plan');
      return;
    }

    // Determine if upgrade or downgrade
    const tierOrder = { basic: 1, professional: 2, enterprise: 3 };
    const isUpgrade = tierOrder[newTier as keyof typeof tierOrder] > tierOrder[currentTier as keyof typeof tierOrder];
    const action = isUpgrade ? 'upgrade' : 'downgrade';

    if (!confirm(`Are you sure you want to ${action} to the ${tier} plan?`)) {
      return;
    }

    await changePlanMutation.mutate({
      endpoint: `/subscriptions/${subscriptionData.subscription_id}/change-plan`,
      new_tier: newTier,
    });
  };

  const handleConfirmPayment = async () => {
    if (!user?.id) {
      alert('User information not available');
      return;
    }

    try {
      // Get the organization ID from the user profile
      const profileResponse = await api.get<any>('/profile');
      
      if (!profileResponse.data.organization?.id) {
        throw new Error('Organization information not found in profile');
      }

      const organizationId = profileResponse.data.organization.id;
      const tierPrice = pricingTiers.find(t => t.tier === selectedTier)?.price || 0;

      // Check if paying from wallet and validate balance
      if (paymentMethod === 'wallet') {
        if (!walletData || walletData.available_balance < tierPrice) {
          alert(`Insufficient wallet balance. Required: ${tierPrice.toLocaleString()} ETB, Available: ${walletData?.available_balance.toLocaleString() || 0} ETB`);
          return;
        }
      }

      // Create subscription
      await changePlanMutation.mutate({
        endpoint: '/subscriptions',
        organization_id: organizationId,
        tier: selectedTier.toUpperCase(), // Backend expects UPPERCASE
        trial_days: 0,
        pay_from_wallet: paymentMethod === 'wallet',
      });

      // Refetch subscription data to update UI
      refetchSubscription();
      
      setShowPaymentModal(false);
      setSelectedTier('');
      setPaymentMethod('wallet');
      
      // Show success message
      alert(paymentMethod === 'wallet' 
        ? 'Subscription activated! Payment deducted from wallet.' 
        : 'Subscription created! Awaiting payment verification by Finance Officer.');
    } catch (error) {
      console.error('[handleConfirmPayment] Error:', error);
      alert(`Failed to create subscription: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const handleCancelSubscription = () => {
    setShowCancelModal(true);
  };

  const handleConfirmCancel = async () => {
    if (!subscriptionData) {
      alert('No active subscription found');
      return;
    }

    await cancelSubscriptionMutation.mutate({
      endpoint: `/subscriptions/${subscriptionData.subscription_id}/cancel`,
      reason: cancelReason || undefined,
    });
  };

  const handleContactSales = () => {
    // TODO: Implement contact sales functionality
    alert('Contact Sales: This will open a contact form or redirect to sales page.');
  };

  return (
    <ProtectedRoute allowedRoles={['organization']}>
      {user ? (
        <PortalShell
          user={user}
          title="Manage Subscription Plan"
          subtitle="Choose the perfect plan for your organization"
          navItems={getPortalNavItems(user.role)}
          hideThemeToggle={true}
        >
          {/* Back Button */}
          <div className="mb-6">
            <button
              onClick={() => router.push('/organization/billing')}
              className="flex items-center gap-2 text-[#94A3B8] hover:text-[#F8FAFC] transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Billing
            </button>
          </div>

          {/* Loading State */}
          {subscriptionLoading && (
            <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-12 mb-8 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-[#334155] border-t-[#3B82F6] mb-4"></div>
              <p className="text-[#94A3B8]">Loading subscription...</p>
            </div>
          )}

          {/* Current Plan Banner - Only show if subscription exists */}
          {subscriptionData && (
            <div className="bg-gradient-to-r from-[#3B82F6]/20 to-[#8B5CF6]/20 rounded-xl border border-[#3B82F6]/30 p-6 mb-8">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-[#F8FAFC] mb-1">
                    Current Plan: <span className="text-[#3B82F6] capitalize">{subscriptionData.tier}</span>
                  </h3>
                  <p className="text-[#94A3B8]">
                    {subscriptionData.subscription_fee.toLocaleString()} {subscriptionData.currency} per 4 months
                  </p>
                </div>
                <button
                  onClick={handleCancelSubscription}
                  className="px-4 py-2 bg-[#EF4444]/10 hover:bg-[#EF4444]/20 text-[#EF4444] rounded-lg font-medium transition-colors border border-[#EF4444]/30"
                >
                  Cancel Subscription
                </button>
              </div>
            </div>
          )}

          {/* No Subscription Message - Show when no subscription exists */}
          {!subscriptionLoading && (subscriptionError || !subscriptionData) && (
            <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-8 mb-8 text-center">
              <div className="bg-[#334155]/30 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-[#3B82F6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-[#F8FAFC] mb-2">Choose Your Plan</h3>
              <p className="text-[#94A3B8]">Select a subscription plan below to get started</p>
            </div>
          )}

          {/* Pricing Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {pricingTiers.map((tier) => (
              <div
                key={tier.id}
                className={`relative bg-[#1E293B] rounded-xl p-8 transition-all ${
                  tier.popular
                    ? 'border-2 border-[#3B82F6] shadow-lg shadow-[#3B82F6]/20'
                    : 'border border-[#334155]'
                } ${tier.current ? 'ring-2 ring-[#10B981]' : ''}`}
              >
                {/* Popular Badge */}
                {tier.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] text-white px-4 py-1 rounded-full text-sm font-bold">
                      MOST POPULAR
                    </span>
                  </div>
                )}

                {/* Current Plan Badge */}
                {tier.current && (
                  <div className="absolute -top-4 right-4">
                    <span className="bg-[#10B981] text-white px-3 py-1 rounded-full text-xs font-bold">
                      CURRENT PLAN
                    </span>
                  </div>
                )}

                {/* Tier Header */}
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-[#F8FAFC] mb-2">{tier.name}</h3>
                  <div className="mb-4">
                    <span className="text-4xl font-bold text-[#F8FAFC]">
                      {tier.price.toLocaleString()}
                    </span>
                    <span className="text-[#94A3B8] ml-2">ETB</span>
                  </div>
                  <p className="text-[#64748B] text-sm">{tier.billingCycle}</p>
                  <p className="text-[#94A3B8] text-sm mt-2">{tier.description}</p>
                </div>

                {/* Features List */}
                <div className="space-y-3 mb-8">
                  {tier.features.map((feature, index) => (
                    <div key={index} className="flex items-start gap-3">
                      <svg
                        className="w-5 h-5 text-[#10B981] flex-shrink-0 mt-0.5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                      <span className="text-[#F8FAFC] text-sm">{feature}</span>
                    </div>
                  ))}
                </div>

                {/* Action Button */}
                <button
                  onClick={() => handleSelectPlan(tier.tier)}
                  disabled={tier.current || changePlanMutation.isLoading}
                  className={`w-full py-3 rounded-lg font-semibold transition-all ${
                    tier.current
                      ? 'bg-[#334155] text-[#64748B] cursor-not-allowed'
                      : tier.popular
                      ? 'bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] hover:from-[#2563EB] hover:to-[#7C3AED] text-white disabled:opacity-50'
                      : 'bg-[#3B82F6] hover:bg-[#2563EB] text-white disabled:opacity-50'
                  }`}
                >
                  {tier.current 
                    ? 'Current Plan' 
                    : changePlanMutation.isLoading 
                    ? 'Processing...' 
                    : subscriptionData 
                    ? 'Select Plan' 
                    : 'Subscribe Now'}
                </button>
              </div>
            ))}
          </div>

          {/* Additional Information */}
          <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-6">
            <h3 className="text-lg font-bold text-[#F8FAFC] mb-4">Need Help Choosing?</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-[#F8FAFC] mb-2">All Plans Include:</h4>
                <ul className="space-y-2 text-[#94A3B8] text-sm">
                  <li>• Secure bug bounty platform</li>
                  <li>• Researcher community access</li>
                  <li>• Payment processing</li>
                  <li>• Report management</li>
                  <li>• Vulnerability tracking</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-[#F8FAFC] mb-2">Questions?</h4>
                <p className="text-[#94A3B8] text-sm mb-3">
                  Our team is here to help you choose the right plan for your organization.
                </p>
                <button 
                  onClick={handleContactSales}
                  className="px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg font-medium transition-colors text-sm"
                >
                  Contact Sales
                </button>
              </div>
            </div>
          </div>

          {/* Payment Method Modal */}
          {showPaymentModal && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-8 max-w-md w-full mx-4">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-[#F8FAFC]">Choose Payment Method</h2>
                  <button
                    onClick={() => {
                      setShowPaymentModal(false);
                      setSelectedTier('');
                    }}
                    className="text-[#94A3B8] hover:text-[#F8FAFC] transition-colors"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="space-y-6">
                  {/* Selected Plan Info */}
                  <div className="bg-[#334155]/30 rounded-lg p-4">
                    <p className="text-[#94A3B8] text-sm mb-1">Selected Plan</p>
                    <p className="text-[#F8FAFC] font-semibold capitalize text-lg">{selectedTier}</p>
                    <p className="text-[#3B82F6] font-bold text-2xl mt-2">
                      {pricingTiers.find(t => t.tier === selectedTier)?.price.toLocaleString()} ETB
                    </p>
                    <p className="text-[#94A3B8] text-sm">per 4 months</p>
                  </div>

                  {/* Wallet Balance */}
                  {walletData && (
                    <div className="bg-[#334155]/30 rounded-lg p-4">
                      <p className="text-[#94A3B8] text-sm mb-1">Your Wallet Balance</p>
                      <p className="text-[#F8FAFC] font-bold text-xl">
                        {walletData.available_balance.toLocaleString()} {walletData.currency}
                      </p>
                      {walletData.available_balance < (pricingTiers.find(t => t.tier === selectedTier)?.price || 0) && (
                        <p className="text-[#EF4444] text-sm mt-2">⚠️ Insufficient balance</p>
                      )}
                    </div>
                  )}

                  {/* Payment Method Selection */}
                  <div>
                    <label className="block text-[#F8FAFC] font-medium mb-3">
                      Payment Method
                    </label>
                    <div className="space-y-3">
                      {/* Wallet Payment */}
                      <button
                        onClick={() => setPaymentMethod('wallet')}
                        className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                          paymentMethod === 'wallet'
                            ? 'border-[#3B82F6] bg-[#3B82F6]/10'
                            : 'border-[#334155] hover:border-[#475569]'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-[#F8FAFC] font-semibold">Pay from Wallet</p>
                            <p className="text-[#94A3B8] text-sm">Instant activation</p>
                          </div>
                          <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                            paymentMethod === 'wallet' ? 'border-[#3B82F6]' : 'border-[#334155]'
                          }`}>
                            {paymentMethod === 'wallet' && (
                              <div className="w-3 h-3 rounded-full bg-[#3B82F6]"></div>
                            )}
                          </div>
                        </div>
                      </button>

                      {/* Manual Payment */}
                      <button
                        onClick={() => setPaymentMethod('manual')}
                        className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                          paymentMethod === 'manual'
                            ? 'border-[#3B82F6] bg-[#3B82F6]/10'
                            : 'border-[#334155] hover:border-[#475569]'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-[#F8FAFC] font-semibold">Manual Payment</p>
                            <p className="text-[#94A3B8] text-sm">Bank transfer (requires verification)</p>
                          </div>
                          <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                            paymentMethod === 'manual' ? 'border-[#3B82F6]' : 'border-[#334155]'
                          }`}>
                            {paymentMethod === 'manual' && (
                              <div className="w-3 h-3 rounded-full bg-[#3B82F6]"></div>
                            )}
                          </div>
                        </div>
                      </button>
                    </div>
                  </div>

                  {/* Info Message */}
                  {paymentMethod === 'manual' && (
                    <div className="bg-[#F59E0B]/10 border border-[#F59E0B]/30 rounded-lg p-4">
                      <p className="text-[#F59E0B] text-sm">
                        ℹ️ Manual payment requires Finance Officer verification. Your subscription will be activated after payment confirmation.
                      </p>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-4 pt-4">
                    <button
                      onClick={() => {
                        setShowPaymentModal(false);
                        setSelectedTier('');
                      }}
                      className="flex-1 px-6 py-3 bg-[#334155] hover:bg-[#475569] text-white rounded-lg font-medium transition-colors"
                      disabled={changePlanMutation.isLoading}
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleConfirmPayment}
                      disabled={changePlanMutation.isLoading || (paymentMethod === 'wallet' && walletData && walletData.available_balance < (pricingTiers.find(t => t.tier === selectedTier)?.price || 0))}
                      className="flex-1 px-6 py-3 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {changePlanMutation.isLoading ? 'Processing...' : 'Confirm & Subscribe'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Cancel Subscription Modal */}
          {showCancelModal && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-[#1E293B] rounded-xl border border-[#334155] p-8 max-w-md w-full mx-4">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-[#F8FAFC]">Cancel Subscription</h2>
                  <button
                    onClick={() => setShowCancelModal(false)}
                    className="text-[#94A3B8] hover:text-[#F8FAFC] transition-colors"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="space-y-6">
                  {/* Warning Message */}
                  <div className="bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <svg className="w-6 h-6 text-[#EF4444] flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <div>
                        <h3 className="text-[#EF4444] font-semibold mb-1">Warning</h3>
                        <p className="text-[#94A3B8] text-sm">
                          Cancelling your subscription will disable access to premium features at the end of your current billing period.
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Reason Input */}
                  <div>
                    <label className="block text-[#F8FAFC] font-medium mb-2">
                      Reason for cancellation (optional)
                    </label>
                    <textarea
                      value={cancelReason}
                      onChange={(e) => setCancelReason(e.target.value)}
                      placeholder="Help us improve by telling us why you're cancelling..."
                      className="w-full px-4 py-3 bg-[#0F172A] border border-[#334155] rounded-lg text-[#F8FAFC] placeholder-[#64748B] focus:outline-none focus:border-[#3B82F6] resize-none"
                      rows={4}
                    />
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-4 pt-4">
                    <button
                      onClick={() => setShowCancelModal(false)}
                      className="flex-1 px-6 py-3 bg-[#334155] hover:bg-[#475569] text-white rounded-lg font-medium transition-colors"
                      disabled={cancelSubscriptionMutation.isLoading}
                    >
                      Keep Subscription
                    </button>
                    <button
                      onClick={handleConfirmCancel}
                      disabled={cancelSubscriptionMutation.isLoading}
                      className="flex-1 px-6 py-3 bg-[#EF4444] hover:bg-[#DC2626] text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {cancelSubscriptionMutation.isLoading ? 'Cancelling...' : 'Cancel Subscription'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}

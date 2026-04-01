import ResearcherPlaceholderPage from '@/components/portal/ResearcherPlaceholderPage';

export default function ResearcherEarningsPage() {
  return (
    <ResearcherPlaceholderPage
      title="Earnings"
      subtitle="Follow pending, approved, and paid rewards as reports move through acceptance and payout."
      description="This page establishes the sidebar route for the researcher payout workflow while the detailed finance widgets are being built."
      workflow={[
        'Surface pending rewards from accepted submissions before they become payable.',
        'Show payment milestones such as review, approval, processing, and completion.',
        'Connect earnings history back to the underlying reports so payout status is always explainable.',
      ]}
      focusAreas={[
        'The final screen should separate pending, scheduled, and completed payouts clearly.',
        'Payment method and compliance dependencies should be visible before a payout fails.',
        'The module will later consume the wallet and payment-method services already present in the backend.',
      ]}
    />
  );
}

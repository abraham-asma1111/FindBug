import ResearcherPlaceholderPage from '@/components/portal/ResearcherPlaceholderPage';

export default function ResearcherAnalyticsPage() {
  return (
    <ResearcherPlaceholderPage
      title="Analytics"
      subtitle="Measure throughput, severity distribution, earnings trends, and performance across engagements."
      description="This module holds the researcher performance views that sit beyond the high-level dashboard summary."
      workflow={[
        'Review submission volume and acceptance outcomes over time.',
        'Compare report quality signals such as validity rate, response cycles, and severity mix.',
        'Use trend data to understand which engagement types are converting into earnings and reputation.',
      ]}
      focusAreas={[
        'Charts should eventually separate engagement types such as Bug Bounty, PTaaS, AI Red Teaming, and Live Events.',
        'Analytics needs to complement the dashboard rather than duplicate the same four KPI cards.',
        'The backend analytics service is already available, so this route is a safe target for the next build phase.',
      ]}
    />
  );
}

import ResearcherPlaceholderPage from '@/components/portal/ResearcherPlaceholderPage';

export default function ResearcherReportsPage() {
  return (
    <ResearcherPlaceholderPage
      title="Reports"
      subtitle="Manage the report lifecycle from draft submission through validation, retest, and closure."
      description="This module is reserved for the real submission workflow used by researchers once they engage with a program."
      workflow={[
        'Start a report from an active engagement and submit the initial finding package.',
        'Track feedback from triage or the organization when more evidence or clarification is required.',
        'Follow accepted reports through remediation, retest, and final closure without losing message context.',
      ]}
      focusAreas={[
        'Status lanes need to reflect the real bug bounty workflow rather than a generic document list.',
        'Each report should tie directly to an engagement, severity, activity thread, and payout outcome.',
        'Horizontal tabs will later mirror states such as New, In Review, Needs Response, Accepted, Retest, and Closed.',
      ]}
    />
  );
}

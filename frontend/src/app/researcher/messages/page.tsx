import ResearcherPlaceholderPage from '@/components/portal/ResearcherPlaceholderPage';

export default function ResearcherMessagesPage() {
  return (
    <ResearcherPlaceholderPage
      title="Messages"
      subtitle="Centralize report conversations, engagement communication, and workflow follow-ups in one inbox."
      description="This route is reserved for the researcher messaging workspace tied to reports and engagement activity."
      workflow={[
        'Receive clarifications, retest requests, and organization feedback without leaving the portal.',
        'Keep report-linked conversations available in a central inbox view for triage continuity.',
        'Separate unread, active, and archived threads once the horizontal navigation is added.',
      ]}
      focusAreas={[
        'Messaging should feel operational, not like a disconnected chat widget.',
        'Each thread will eventually need context about the report, engagement, or payout it belongs to.',
        'The backend messages endpoints are already present, so this page can move from placeholder to real inbox next.',
      ]}
    />
  );
}

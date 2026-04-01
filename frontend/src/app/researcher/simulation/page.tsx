import ResearcherPlaceholderPage from '@/components/portal/ResearcherPlaceholderPage';

export default function ResearcherSimulationPage() {
  return (
    <ResearcherPlaceholderPage
      title="Simulation"
      subtitle="Practice in challenge environments and track private progress before joining live engagements."
      description="The simulation area sits under the researcher portal as a training and preparation workflow."
      workflow={[
        'Start a guided challenge or scenario from the researcher simulation catalog.',
        'Track attempt progress, submissions, and feedback inside a dedicated practice environment.',
        'Review results privately while the platform policy around simulation ranking remains normalized.',
      ]}
      focusAreas={[
        'This route aligns the sidebar with the planning agreement and the `/researcher/simulation/*` direction.',
        'Simulation UX should stay distinct from live report handling so training data never looks like production engagement data.',
        'The backend simulation gateway exists, but privacy and leaderboard behavior still need final product rules.',
      ]}
    />
  );
}

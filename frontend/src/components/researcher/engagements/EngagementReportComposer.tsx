'use client';

import Link from 'next/link';
import { useEngagementReportSubmission } from '@/hooks/useEngagementReportSubmission';

interface EngagementReportComposerProps {
  resetKey?: string;
  reportProgramId?: string;
  reportHref?: string;
}

export default function EngagementReportComposer({
  resetKey,
  reportProgramId,
  reportHref,
}: EngagementReportComposerProps) {
  const { draft, setDraft, submitError, submitSuccess, submittedReportHref, isSubmittingReport, submitReport } =
    useEngagementReportSubmission({
      resetKey,
      reportProgramId,
      reportHref,
    });

  return (
    <div className="rounded-[28px] border border-[#e6ddd4] bg-white dark:bg-[#111111] p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Inline Report Composer</p>
          <h4 className="mt-2 text-xl font-semibold tracking-tight text-[#2d2a26]">Submit vulnerability from this engagement</h4>
        </div>
        <span className="rounded-full bg-[#eef7ef] px-3 py-1 text-xs font-semibold text-[#24613a]">Program joined</span>
      </div>

      {submitError ? (
        <div className="mt-4 rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">{submitError}</div>
      ) : null}

      {submitSuccess ? (
        <div className="mt-4 rounded-2xl border border-[#b8dbbf] bg-[#eef7ef] p-4 text-sm text-[#24613a]">
          {submitSuccess}
          {submittedReportHref ? (
            <div className="mt-3">
              <Link href={submittedReportHref} className="font-semibold underline underline-offset-4">
                Open report queue
              </Link>
            </div>
          ) : null}
        </div>
      ) : null}

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <label className="block">
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Title</span>
          <input
            value={draft.title}
            onChange={(event) => setDraft((current) => ({ ...current, title: event.target.value }))}
            className="mt-2 w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm text-[#2d2a26] outline-none transition focus:border-[#bcae9e]"
            placeholder="Example: Blind XSS in public feedback form"
          />
        </label>

        <label className="block">
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Suggested Severity</span>
          <select
            value={draft.suggestedSeverity}
            onChange={(event) => setDraft((current) => ({ ...current, suggestedSeverity: event.target.value }))}
            className="mt-2 w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm text-[#2d2a26] outline-none transition focus:border-[#bcae9e]"
          >
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </label>

        <label className="block">
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Vulnerability Type</span>
          <input
            value={draft.vulnerabilityType}
            onChange={(event) => setDraft((current) => ({ ...current, vulnerabilityType: event.target.value }))}
            className="mt-2 w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm text-[#2d2a26] outline-none transition focus:border-[#bcae9e]"
            placeholder="XSS, Broken Access Control, SSRF..."
          />
        </label>

        <label className="block">
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Affected Asset</span>
          <input
            value={draft.affectedAsset}
            onChange={(event) => setDraft((current) => ({ ...current, affectedAsset: event.target.value }))}
            className="mt-2 w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm text-[#2d2a26] outline-none transition focus:border-[#bcae9e]"
            placeholder="api.company.com/v1/feedback"
          />
        </label>
      </div>

      <div className="mt-4 grid gap-4">
        <label className="block">
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Description</span>
          <textarea
            value={draft.description}
            onChange={(event) => setDraft((current) => ({ ...current, description: event.target.value }))}
            className="mt-2 min-h-[132px] w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm leading-6 text-[#2d2a26] outline-none transition focus:border-[#bcae9e]"
            placeholder="Describe the issue, entry point, and exploit conditions in enough detail for triage."
          />
        </label>

        <label className="block">
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Steps To Reproduce</span>
          <textarea
            value={draft.stepsToReproduce}
            onChange={(event) => setDraft((current) => ({ ...current, stepsToReproduce: event.target.value }))}
            className="mt-2 min-h-[120px] w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm leading-6 text-[#2d2a26] outline-none transition focus:border-[#bcae9e]"
            placeholder="List exact reproduction steps, payloads, credentials assumptions, and environmental notes."
          />
        </label>

        <label className="block">
          <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Impact Assessment</span>
          <textarea
            value={draft.impactAssessment}
            onChange={(event) => setDraft((current) => ({ ...current, impactAssessment: event.target.value }))}
            className="mt-2 min-h-[120px] w-full rounded-2xl border border-[#d8d0c8] bg-[#fcfaf7] px-4 py-3 text-sm leading-6 text-[#2d2a26] outline-none transition focus:border-[#bcae9e]"
            placeholder="State business impact, data exposure, privilege change, and exploit reliability."
          />
        </label>
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={submitReport}
          disabled={isSubmittingReport}
          className="rounded-full bg-[#2d2a26] px-5 py-2.5 text-xs font-semibold text-white transition hover:bg-[#1f1c19] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmittingReport ? 'Submitting...' : 'Submit vulnerability'}
        </button>
        {reportHref ? (
          <Link
            href={reportHref}
            className="rounded-full border border-[#d8d0c8] px-5 py-2.5 text-xs font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
          >
            Open report workspace
          </Link>
        ) : null}
      </div>
    </div>
  );
}

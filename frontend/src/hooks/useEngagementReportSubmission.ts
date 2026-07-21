'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export interface EngagementReportDraft {
  title: string;
  suggestedSeverity: string;
  vulnerabilityType: string;
  affectedAsset: string;
  description: string;
  stepsToReproduce: string;
  impactAssessment: string;
}

export const initialEngagementReportDraft: EngagementReportDraft = {
  title: '',
  suggestedSeverity: 'medium',
  vulnerabilityType: '',
  affectedAsset: '',
  description: '',
  stepsToReproduce: '',
  impactAssessment: '',
};

function validateEngagementReportDraft(draft: EngagementReportDraft): string {
  if (draft.title.trim().length < 10) {
    return 'Title must be at least 10 characters.';
  }

  if (draft.description.trim().length < 50) {
    return 'Description must be at least 50 characters.';
  }

  if (draft.stepsToReproduce.trim().length < 20) {
    return 'Steps to reproduce must be at least 20 characters.';
  }

  if (draft.impactAssessment.trim().length < 20) {
    return 'Impact assessment must be at least 20 characters.';
  }

  return '';
}

export function useEngagementReportSubmission(params: {
  resetKey?: string;
  reportProgramId?: string;
  reportHref?: string;
}) {
  const { resetKey, reportProgramId, reportHref } = params;
  const [draft, setDraft] = useState<EngagementReportDraft>(initialEngagementReportDraft);
  const [submitError, setSubmitError] = useState('');
  const [submitSuccess, setSubmitSuccess] = useState('');
  const [submittedReportHref, setSubmittedReportHref] = useState('');
  const [isSubmittingReport, setIsSubmittingReport] = useState(false);

  useEffect(() => {
    setDraft(initialEngagementReportDraft);
    setSubmitError('');
    setSubmitSuccess('');
    setSubmittedReportHref('');
  }, [resetKey]);

  async function submitReport() {
    if (!reportProgramId) {
      setSubmitError('This engagement is not linked to a reportable program.');
      return;
    }

    const validationError = validateEngagementReportDraft(draft);

    if (validationError) {
      setSubmitError(validationError);
      return;
    }

    try {
      setIsSubmittingReport(true);
      setSubmitError('');
      setSubmitSuccess('');

      const response = await api.post('/reports', {
        program_id: reportProgramId,
        title: draft.title.trim(),
        description: draft.description.trim(),
        steps_to_reproduce: draft.stepsToReproduce.trim(),
        impact_assessment: draft.impactAssessment.trim(),
        suggested_severity: draft.suggestedSeverity,
        affected_asset: draft.affectedAsset.trim() || null,
        vulnerability_type: draft.vulnerabilityType.trim() || null,
      });

      setSubmitSuccess(
        `Report ${response.data?.report_number || 'draft'} was submitted from this engagement. The next step is triage follow-up.`
      );
      setSubmittedReportHref(reportHref || '/researcher/reports');
      setDraft(initialEngagementReportDraft);
    } catch (err: any) {
      setSubmitError(err.response?.data?.detail || 'Failed to submit the vulnerability report from this engagement.');
    } finally {
      setIsSubmittingReport(false);
    }
  }

  return {
    draft,
    setDraft,
    submitError,
    submitSuccess,
    submittedReportHref,
    isSubmittingReport,
    submitReport,
  };
}

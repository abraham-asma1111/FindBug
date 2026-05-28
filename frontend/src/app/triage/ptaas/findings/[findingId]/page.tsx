'use client';

import { useParams } from 'next/navigation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import TriagePtaasReportDetail from '@/components/triage/TriagePtaasReportDetail';

export default function TriagePTaaSFindingDetailPage() {
  const params = useParams();
  const findingId = params?.findingId as string;

  return (
    <ProtectedRoute allowedRoles={['triage_specialist', 'admin', 'super_admin']}>
      <TriagePtaasReportDetail findingId={findingId} />
    </ProtectedRoute>
  );
}

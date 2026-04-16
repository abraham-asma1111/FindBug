'use client';

import React, { useState } from 'react';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import { FileText, Download, Eye } from 'lucide-react';
import { useToast } from '@/components/ui/Toast';

interface PTaaSReportGeneratorProps {
  engagementId: string;
  engagementName: string;
}

export default function PTaaSReportGenerator({
  engagementId,
  engagementName,
}: PTaaSReportGeneratorProps) {
  const { showToast } = useToast();
  const [generating, setGenerating] = useState<string | null>(null);

  const generateReport = async (type: string) => {
    setGenerating(type);
    
    try {
      const response = await fetch(
        `http://localhost:8002/api/v1/ptaas/engagements/${engagementId}/reports/${type}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      
      if (!response.ok) throw new Error('Failed to generate report');
      
      const data = await response.json();
      
      // Download as JSON
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${engagementName}-${type}-report-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      showToast('Report generated successfully', 'success');
    } catch (error) {
      showToast('Failed to generate report', 'error');
    } finally {
      setGenerating(null);
    }
  };

  const reports = [
    {
      type: 'executive',
      title: 'Executive Summary',
      description: 'High-level overview for stakeholders with risk assessment and recommendations',
      icon: FileText,
      color: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600',
    },
    {
      type: 'technical',
      title: 'Technical Report',
      description: 'Detailed technical findings with reproduction steps and remediation guidance',
      icon: FileText,
      color: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600',
    },
    {
      type: 'compliance',
      title: 'Compliance Report',
      description: 'Compliance status mapped to PCI DSS, OWASP, and ISO 27001 requirements',
      icon: FileText,
      color: 'bg-green-50 dark:bg-green-900/20 text-green-600',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-[#2d2a26] dark:text-[#faf6f1] mb-2">
          Report Generation
        </h2>
        <p className="text-[#6b6662] dark:text-[#a39e9a]">
          Generate comprehensive reports for {engagementName}
        </p>
      </div>

      <div className="grid gap-4">
        {reports.map((report) => {
          const Icon = report.icon;
          const isGenerating = generating === report.type;

          return (
            <Card key={report.type}>
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-lg ${report.color}`}>
                  <Icon className="h-6 w-6" />
                </div>
                
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-[#2d2a26] dark:text-[#faf6f1] mb-1">
                    {report.title}
                  </h3>
                  <p className="text-sm text-[#6b6662] dark:text-[#a39e9a] mb-4">
                    {report.description}
                  </p>
                  
                  <div className="flex gap-2">
                    <Button
                      onClick={() => generateReport(report.type)}
                      disabled={isGenerating}
                      size="sm"
                      className="bg-[#3b82f6] hover:bg-[#2563eb] text-white"
                    >
                      {isGenerating ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <Download className="h-4 w-4 mr-2" />
                          Download JSON
                        </>
                      )}
                    </Button>
                    
                    <Button
                      onClick={() => showToast('PDF generation coming soon', 'info')}
                      size="sm"
                      variant="outline"
                      disabled={isGenerating}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download PDF
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
        <div className="flex gap-3">
          <Eye className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-1">
              Report Customization
            </h4>
            <p className="text-sm text-blue-800 dark:text-blue-200">
              Reports include all findings, analytics, and compliance data. PDF generation with custom branding is coming soon.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}

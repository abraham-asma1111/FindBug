'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import { useFormValidation, validators } from '@/lib/validation';

interface ReportFormData {
  program_id: string;
  title: string;
  description: string;
  suggested_severity: string;
  vulnerability_type: string;
  steps_to_reproduce: string;
  impact_assessment: string;
  affected_asset: string;
  evidence_files: File[];
}

interface VRTEntry {
  id: string;
  name: string;
  category: string;
  description?: string;
}

interface Program {
  id: string;
  name: string;
  status?: string;
}

const steps = ['Program', 'Details', 'Evidence', 'Impact', 'Review'];

export default function ReportSubmissionForm() {
  const [currentStep, setCurrentStep] = useState(0);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [stepError, setStepError] = useState<string>('');

  // Load VRT entries from database
  const { data: vrtData } = useApiQuery<VRTEntry[]>('/vrt/entries?limit=500', { enabled: true });
  const vrtEntries = Array.isArray(vrtData) ? vrtData : [];

  // Load programs
  const { data: programsData } = useApiQuery<Program[]>('/programs', { enabled: true });
  const programs = Array.isArray(programsData) ? programsData : [];

  const { values, errors, touched, handleChange, handleBlur, handleSubmit, setValues } = useFormValidation<ReportFormData>(
    {
      program_id: '',
      title: '',
      description: '',
      suggested_severity: '',
      vulnerability_type: '',
      steps_to_reproduce: '',
      impact_assessment: '',
      affected_asset: '',
      evidence_files: [],
    },
    {
      program_id: [validators.required('Please select a program')],
      title: [validators.required(), validators.minLength(10), validators.maxLength(200)],
      description: [validators.required(), validators.minLength(50)],
      suggested_severity: [validators.required('Please select severity')],
      vulnerability_type: [validators.required('Please select VRT category')],
      steps_to_reproduce: [validators.required(), validators.minLength(20)],
      impact_assessment: [validators.required(), validators.minLength(20)],
    }
  );

  const { mutate: submitReport, isLoading } = useApiMutation('/reports', 'POST', {
    onSuccess: async (response: any) => {
      // If we have files, upload them to the created report
      if (uploadedFiles.length > 0 && response.report_id) {
        try {
          // Upload each file separately
          for (const file of uploadedFiles) {
            const formData = new FormData();
            formData.append('file', file);
            
            await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/reports/${response.report_id}/attachments`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
              },
              body: formData,
            });
          }
        } catch (error) {
          console.error('Error uploading attachments:', error);
        }
      }
      
      setSubmitSuccess(true);
      setCurrentStep(0);
      setUploadedFiles([]);
      setTimeout(() => setSubmitSuccess(false), 5000);
    },
  });

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setUploadedFiles(prev => [...prev, ...files]);
    setValues({ ...values, evidence_files: [...uploadedFiles, ...files] });
  };

  const removeFile = (index: number) => {
    const newFiles = uploadedFiles.filter((_, i) => i !== index);
    setUploadedFiles(newFiles);
    setValues({ ...values, evidence_files: newFiles });
  };

  const handleNext = () => {
    // Clear previous error
    setStepError('');
    
    // Validate current step before proceeding
    let isValid = true;
    let errorMessage = '';

    switch (currentStep) {
      case 0: // Program selection
        if (!values.program_id) {
          isValid = false;
          errorMessage = 'Please select a program before continuing';
          handleBlur('program_id');
        }
        break;
      
      case 1: // Report details
        if (!values.title || values.title.length < 10) {
          isValid = false;
          errorMessage = 'Please enter a title (minimum 10 characters)';
          handleBlur('title');
        } else if (!values.suggested_severity) {
          isValid = false;
          errorMessage = 'Please select a severity level';
          handleBlur('suggested_severity');
        } else if (!values.vulnerability_type) {
          isValid = false;
          errorMessage = 'Please select a VRT category';
          handleBlur('vulnerability_type');
        } else if (!values.description || values.description.length < 50) {
          isValid = false;
          errorMessage = 'Please enter a description (minimum 50 characters)';
          handleBlur('description');
        } else if (!values.steps_to_reproduce || values.steps_to_reproduce.length < 20) {
          isValid = false;
          errorMessage = 'Please enter steps to reproduce (minimum 20 characters)';
          handleBlur('steps_to_reproduce');
        }
        break;
      
      case 2: // Evidence upload
        if (uploadedFiles.length === 0) {
          isValid = false;
          errorMessage = 'Please upload at least one evidence file';
        }
        break;
      
      case 3: // Impact assessment
        if (!values.impact_assessment || values.impact_assessment.length < 20) {
          isValid = false;
          errorMessage = 'Please enter an impact assessment (minimum 20 characters)';
          handleBlur('impact_assessment');
        }
        break;
    }

    if (!isValid) {
      setStepError(errorMessage);
      return;
    }

    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    setStepError(''); // Clear error when going back
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const onSubmit = handleSubmit((data) => {
    // Validate evidence files
    if (uploadedFiles.length === 0) {
      alert('Please upload at least one evidence file');
      setCurrentStep(2); // Go to evidence step
      return;
    }

    // Submit report data (files will be uploaded in onSuccess callback)
    const reportData = {
      program_id: data.program_id,
      title: data.title,
      description: data.description,
      suggested_severity: data.suggested_severity,
      vulnerability_type: data.vulnerability_type,
      steps_to_reproduce: data.steps_to_reproduce,
      impact_assessment: data.impact_assessment,
      affected_asset: data.affected_asset || undefined,
    };

    submitReport(reportData);
  });

  return (
    <div className="space-y-5">
      {/* Success Alert */}
      {submitSuccess && (
        <div className="rounded-2xl border border-[#c8e6c9] bg-[#eef7ef] p-4 text-sm text-[#24613a]">
          <p className="font-semibold">Report Submitted Successfully!</p>
          <p className="mt-1">Your vulnerability report has been submitted. You'll receive updates via email.</p>
        </div>
      )}

      {/* Step Validation Error */}
      {stepError && (
        <div className="rounded-2xl border border-[#f2c0bc] bg-[#fff2f1] p-4 text-sm text-[#b42318]">
          <p className="font-semibold">⚠️ Validation Error</p>
          <p className="mt-1">{stepError}</p>
        </div>
      )}

      {/* Progress Steps */}
      <div className="rounded-2xl bg-[#faf6f1] p-5">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1">
                <div
                  className={`
                    w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm
                    ${currentStep >= index
                      ? 'bg-[#ef2330] text-white'
                      : 'bg-[#e6ddd4] text-[#8b8177]'
                    }
                  `}
                >
                  {index + 1}
                </div>
                <p className="text-xs font-medium text-[#2d2a26] mt-2">{step}</p>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`
                    h-1 flex-1 mx-2
                    ${currentStep > index ? 'bg-[#ef2330]' : 'bg-[#e6ddd4]'}
                  `}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      <form onSubmit={onSubmit} className="space-y-5">
        {/* Step 1: Program Selection */}
        {currentStep === 0 && (
          <div className="rounded-2xl bg-[#faf6f1] p-5">
            <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
              Target Program *
            </label>
            <select
              value={values.program_id}
              onChange={(e) => handleChange('program_id', e.target.value)}
              onBlur={() => handleBlur('program_id')}
              className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
            >
              <option value="">Select a program...</option>
              {programs.map((program) => (
                <option key={program.id} value={program.id}>
                  {program.name}
                </option>
              ))}
            </select>
            {touched.program_id && errors.program_id && (
              <p className="mt-2 text-xs text-[#b42318]">{errors.program_id}</p>
            )}
            <p className="mt-3 text-xs text-[#6d6760]">
              Select the program you're reporting to. Make sure you're enrolled in the program.
            </p>
          </div>
        )}

        {/* Step 2: Report Details */}
        {currentStep === 1 && (
          <div className="rounded-2xl bg-[#faf6f1] p-5 space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                Report Title *
              </label>
              <input
                type="text"
                placeholder="e.g., SQL Injection in login form"
                value={values.title}
                onChange={(e) => handleChange('title', e.target.value)}
                onBlur={() => handleBlur('title')}
                className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] placeholder:text-[#8b8177] focus:border-[#c8bfb6] focus:outline-none"
              />
              {touched.title && errors.title && (
                <p className="mt-2 text-xs text-[#b42318]">{errors.title}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                  Severity *
                </label>
                <select
                  value={values.suggested_severity}
                  onChange={(e) => handleChange('suggested_severity', e.target.value)}
                  onBlur={() => handleBlur('suggested_severity')}
                  className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
                >
                  <option value="">Select severity...</option>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
                {touched.suggested_severity && errors.suggested_severity && (
                  <p className="mt-2 text-xs text-[#b42318]">{errors.suggested_severity}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                  VRT Category * ({vrtEntries.length} available)
                </label>
                <select
                  value={values.vulnerability_type}
                  onChange={(e) => handleChange('vulnerability_type', e.target.value)}
                  onBlur={() => handleBlur('vulnerability_type')}
                  className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] focus:border-[#c8bfb6] focus:outline-none"
                >
                  <option value="">Select category...</option>
                  {vrtEntries.map((vrt) => (
                    <option key={vrt.id} value={vrt.name}>
                      {vrt.category} - {vrt.name}
                    </option>
                  ))}
                </select>
                {touched.vulnerability_type && errors.vulnerability_type && (
                  <p className="mt-2 text-xs text-[#b42318]">{errors.vulnerability_type}</p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                Description *
              </label>
              <textarea
                placeholder="Provide a detailed description of the vulnerability..."
                rows={6}
                value={values.description}
                onChange={(e) => handleChange('description', e.target.value)}
                onBlur={() => handleBlur('description')}
                className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] placeholder:text-[#8b8177] focus:border-[#c8bfb6] focus:outline-none resize-vertical"
              />
              {touched.description && errors.description && (
                <p className="mt-2 text-xs text-[#b42318]">{errors.description}</p>
              )}
              <p className="mt-2 text-xs text-[#6d6760]">Minimum 50 characters</p>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                Steps to Reproduce *
              </label>
              <textarea
                placeholder="1. Go to login page&#10;2. Enter payload in username field&#10;3. Click submit..."
                rows={6}
                value={values.steps_to_reproduce}
                onChange={(e) => handleChange('steps_to_reproduce', e.target.value)}
                onBlur={() => handleBlur('steps_to_reproduce')}
                className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] placeholder:text-[#8b8177] focus:border-[#c8bfb6] focus:outline-none resize-vertical"
              />
              {touched.steps_to_reproduce && errors.steps_to_reproduce && (
                <p className="mt-2 text-xs text-[#b42318]">{errors.steps_to_reproduce}</p>
              )}
              <p className="mt-2 text-xs text-[#6d6760]">Provide clear, numbered steps</p>
            </div>
          </div>
        )}

        {/* Step 3: Evidence Upload (REQUIRED) */}
        {currentStep === 2 && (
          <div className="rounded-2xl bg-[#faf6f1] p-5">
            <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
              Evidence * (Required - Upload at least one file)
            </label>
            
            <input
              type="file"
              id="evidence-upload"
              multiple
              accept="image/*,video/*,.pdf"
              onChange={handleFileUpload}
              className="hidden"
            />
            
            <label
              htmlFor="evidence-upload"
              className="block border-2 border-dashed border-[#d8d0c8] rounded-xl p-8 text-center bg-white dark:bg-[#111111] cursor-pointer hover:border-[#c8bfb6] transition"
            >
              <svg
                className="w-10 h-10 mx-auto text-[#8b8177] mb-3"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              <p className="text-sm text-[#6d6760] mb-1">
                Click to upload or drag and drop files here
              </p>
              <p className="text-xs text-[#8b8177]">
                Supported: Images, Videos, PDFs (Max 10MB each)
              </p>
            </label>

            {/* Uploaded Files List */}
            {uploadedFiles.length > 0 && (
              <div className="mt-4 space-y-2">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">
                  Uploaded Files ({uploadedFiles.length})
                </p>
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-white dark:bg-[#111111] rounded-xl px-4 py-3 border border-[#d8d0c8]">
                    <div className="flex items-center gap-3">
                      <svg className="w-5 h-5 text-[#8b8177]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-[#2d2a26]">{file.name}</p>
                        <p className="text-xs text-[#6d6760]">{(file.size / 1024).toFixed(2)} KB</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      className="text-[#b42318] hover:text-[#9d1f1f] transition"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            )}

            {uploadedFiles.length === 0 && (
              <p className="mt-3 text-xs text-[#b42318]">
                ⚠️ At least one evidence file is required to submit the report
              </p>
            )}
          </div>
        )}

        {/* Step 4: Impact Assessment */}
        {currentStep === 3 && (
          <div className="rounded-2xl bg-[#faf6f1] p-5 space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                Impact Description *
              </label>
              <textarea
                placeholder="Describe the potential impact of this vulnerability..."
                rows={5}
                value={values.impact_assessment}
                onChange={(e) => handleChange('impact_assessment', e.target.value)}
                onBlur={() => handleBlur('impact_assessment')}
                className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] placeholder:text-[#8b8177] focus:border-[#c8bfb6] focus:outline-none resize-vertical"
              />
              {touched.impact_assessment && errors.impact_assessment && (
                <p className="mt-2 text-xs text-[#b42318]">{errors.impact_assessment}</p>
              )}
              <p className="mt-2 text-xs text-[#6d6760]">Explain what an attacker could achieve</p>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177] mb-3">
                Affected Asset (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g., https://example.com/login or Mobile App v2.1"
                value={values.affected_asset}
                onChange={(e) => handleChange('affected_asset', e.target.value)}
                className="w-full rounded-xl border border-[#d8d0c8] bg-white dark:bg-[#111111] px-4 py-2.5 text-sm text-[#2d2a26] placeholder:text-[#8b8177] focus:border-[#c8bfb6] focus:outline-none"
              />
              <p className="mt-2 text-xs text-[#6d6760]">Specify which asset or component is affected</p>
            </div>
          </div>
        )}

        {/* Step 5: Review */}
        {currentStep === 4 && (
          <div className="rounded-2xl bg-[#faf6f1] p-5 space-y-4">
            <p className="text-sm font-semibold text-[#2d2a26] mb-4">Review your report before submitting</p>
            
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Title</p>
                <p className="text-[#2d2a26] mt-1">{values.title || 'Not provided'}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Severity</p>
                <p className="text-[#2d2a26] mt-1">{values.suggested_severity || 'Not provided'}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">VRT Category</p>
                <p className="text-[#2d2a26] mt-1">{values.vulnerability_type || 'Not provided'}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Evidence Files</p>
                <p className="text-[#2d2a26] mt-1">{uploadedFiles.length} file(s) uploaded</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8b8177]">Description</p>
                <p className="text-[#6d6760] mt-1 text-xs">{values.description || 'Not provided'}</p>
              </div>
            </div>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex justify-between items-center pt-4">
          {currentStep > 0 ? (
            <button
              type="button"
              onClick={handlePrevious}
              className="inline-flex rounded-full border border-[#d8d0c8] px-8 py-3 text-sm font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
            >
              Previous
            </button>
          ) : (
            <div></div>
          )}
          
          <div className="flex items-center gap-4">
            <button
              type="button"
              className="inline-flex rounded-full border border-[#d8d0c8] px-8 py-3 text-sm font-semibold text-[#2d2a26] transition hover:border-[#c8bfb6] hover:bg-[#fcfaf7]"
            >
              Save Draft
            </button>
            
            {currentStep < steps.length - 1 ? (
              <button
                type="button"
                onClick={handleNext}
                className="inline-flex rounded-full bg-[#ef2330] px-8 py-3 text-sm font-semibold text-white transition hover:bg-[#d41f2c]"
              >
                Next
              </button>
            ) : (
              <button
                type="submit"
                disabled={isLoading || uploadedFiles.length === 0}
                className="inline-flex items-center gap-2 rounded-full bg-[#ef2330] px-8 py-3 text-sm font-semibold text-white transition hover:bg-[#d41f2c] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Submitting...
                  </>
                ) : (
                  'Submit Report'
                )}
              </button>
            )}
          </div>
        </div>
      </form>
    </div>
  );
}

'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import Textarea from '@/components/ui/Textarea';
import Select from '@/components/ui/Select';
import { AlertCircle, Upload, X, CheckCircle } from 'lucide-react';

interface EnhancedFindingSubmissionModalProps {
  isOpen: boolean;
  onClose: () => void;
  engagementId: string;
  existingFinding?: any; // For edit mode
  onSuccess: () => void;
}

export default function EnhancedFindingSubmissionModal({
  isOpen,
  onClose,
  engagementId,
  existingFinding,
  onSuccess
}: EnhancedFindingSubmissionModalProps) {
  const isEditMode = !!existingFinding;
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [uploadedFiles, setUploadedFiles] = useState<Array<{name: string, url: string}>>([]);
  const [isUploading, setIsUploading] = useState(false);

  // Form state - FREQ-35 mandatory fields
  const [formData, setFormData] = useState({
    // Basic Info
    title: existingFinding?.title || '',
    severity: existingFinding?.severity || 'Medium',
    affected_component: existingFinding?.affected_component || '',
    vulnerability_type: existingFinding?.vulnerability_type || '',
    
    // Description & Reproduction
    description: existingFinding?.description || '',
    reproduction_steps: existingFinding?.reproduction_steps || '',
    
    // Proof of Exploit (mandatory, min 50 chars)
    proof_of_exploit: existingFinding?.proof_of_exploit || '',
    exploit_code: existingFinding?.exploit_code || '',
    exploit_screenshots: existingFinding?.exploit_screenshots || [] as string[],
    exploit_video_url: existingFinding?.exploit_video_url || '',
    
    // Impact Analysis (mandatory, min 50 chars)
    impact_analysis: existingFinding?.impact_description || '',
    business_impact: existingFinding?.business_impact || 'Medium',
    technical_impact: {
      confidentiality: existingFinding?.confidentiality_impact || 'None',
      integrity: existingFinding?.integrity_impact || 'None',
      availability: existingFinding?.availability_impact || 'None'
    },
    affected_users: existingFinding?.affected_users || '',
    data_at_risk: existingFinding?.data_at_risk || '',
    
    // Remediation (mandatory, min 50 chars)
    remediation: existingFinding?.remediation_recommendation || '',
    remediation_priority: existingFinding?.remediation_priority || 'High',
    remediation_effort: existingFinding?.remediation_effort || 'Medium',
    remediation_steps: existingFinding?.remediation_steps || [''],
    code_fix_example: existingFinding?.code_fix_example || '',
    
    // Classification
    cwe_id: existingFinding?.cwe_id || '',
    owasp_category: existingFinding?.owasp_category || '',
    
    // CVSS Metrics
    attack_vector: existingFinding?.attack_vector || 'Network',
    attack_complexity: existingFinding?.attack_complexity || 'Low',
    privileges_required: existingFinding?.privileges_required || 'None',
    user_interaction: existingFinding?.user_interaction || 'None',
    
    cvss_score: existingFinding?.cvss_score?.toString() || ''
  });

  const updateField = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleFileUpload = async (files: FileList) => {
    if (files.length === 0) return;

    setIsUploading(true);
    const newUrls: string[] = [];
    const newFiles: Array<{name: string, url: string}> = [];

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Validate file size (10MB)
        if (file.size > 10 * 1024 * 1024) {
          alert(`File ${file.name} is too large. Maximum size is 10MB.`);
          continue;
        }

        // Create FormData
        const formData = new FormData();
        formData.append('file', file);

        // Upload file
        const response = await api.post('/files/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (response.data && response.data.file_path) {
          const fileUrl = response.data.file_path;
          newUrls.push(fileUrl);
          newFiles.push({ name: file.name, url: fileUrl });
        }
      }

      // Add uploaded file URLs to screenshots
      if (newUrls.length > 0) {
        const updatedScreenshots = [...formData.exploit_screenshots, ...newUrls];
        updateField('exploit_screenshots', updatedScreenshots);
        setUploadedFiles(prev => [...prev, ...newFiles]);
      }

      if (newUrls.length > 0) {
        alert(`Successfully uploaded ${newUrls.length} file(s)`);
      }
    } catch (error: any) {
      console.error('File upload error:', error);
      // Extract error message properly - handle both string and object errors
      let errorMessage = 'Unknown error';
      
      if (error?.response?.data?.detail) {
        const detail = error.response.data.detail;
        // If detail is an array of validation errors, extract messages
        if (Array.isArray(detail)) {
          errorMessage = detail.map((err: any) => err.msg || JSON.stringify(err)).join(', ');
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        } else {
          errorMessage = JSON.stringify(detail);
        }
      } else if (error?.message) {
        errorMessage = error.message;
      }
      
      alert(`File upload failed: ${errorMessage}`);
    } finally {
      setIsUploading(false);
    }
  };

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};

    if (step === 1) {
      if (!formData.title || formData.title.length < 3) {
        newErrors.title = 'Title must be at least 3 characters';
      }
      if (!formData.affected_component) {
        newErrors.affected_component = 'Affected component is required';
      }
      if (!formData.vulnerability_type) {
        newErrors.vulnerability_type = 'Vulnerability type is required';
      }
      if (!formData.description || formData.description.length < 10) {
        newErrors.description = 'Description must be at least 10 characters';
      }
      if (!formData.reproduction_steps || formData.reproduction_steps.length < 20) {
        newErrors.reproduction_steps = 'Reproduction steps must be at least 20 characters';
      }
    }

    if (step === 2) {
      if (!formData.proof_of_exploit || formData.proof_of_exploit.length < 50) {
        newErrors.proof_of_exploit = 'Proof of exploit must be at least 50 characters';
      }
    }

    if (step === 3) {
      if (!formData.impact_analysis || formData.impact_analysis.length < 50) {
        newErrors.impact_analysis = 'Impact analysis must be at least 50 characters';
      }
    }

    if (step === 4) {
      if (!formData.remediation || formData.remediation.length < 50) {
        newErrors.remediation = 'Remediation must be at least 50 characters';
      }
      if (formData.remediation_steps.length === 0 || !formData.remediation_steps[0]) {
        newErrors.remediation_steps = 'At least one remediation step is required';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    setCurrentStep(prev => prev - 1);
  };

  const handleSubmit = async () => {
    if (!validateStep(4)) return;

    setIsSubmitting(true);
    try {
      if (isEditMode && existingFinding) {
        // Update existing finding
        await api.patch(`/ptaas/findings/${existingFinding.id}`, {
          ...formData,
          cvss_score: formData.cvss_score ? parseFloat(formData.cvss_score) : null
        });
        alert('Finding updated successfully!');
      } else {
        // Create new finding
        await api.post('/ptaas/findings', {
          engagement_id: engagementId,
          ...formData,
          cvss_score: formData.cvss_score ? parseFloat(formData.cvss_score) : null
        });
        alert('Finding submitted successfully!');
      }
      
      onSuccess();
      onClose();
      
      // Reset form only if creating new
      if (!isEditMode) {
        setFormData({
          title: '',
          severity: 'Medium',
          affected_component: '',
          vulnerability_type: '',
          description: '',
          reproduction_steps: '',
          proof_of_exploit: '',
          exploit_code: '',
          exploit_screenshots: [],
          exploit_video_url: '',
          impact_analysis: '',
          business_impact: 'Medium',
          technical_impact: {
            confidentiality: 'None',
            integrity: 'None',
            availability: 'None'
          },
          affected_users: '',
          data_at_risk: '',
          remediation: '',
          remediation_priority: 'High',
          remediation_effort: 'Medium',
          remediation_steps: [''],
          code_fix_example: '',
          cwe_id: '',
          owasp_category: '',
          attack_vector: 'Network',
          attack_complexity: 'Low',
          privileges_required: 'None',
          user_interaction: 'None',
          cvss_score: ''
        });
        setCurrentStep(1);
      }
    } catch (error: any) {
      alert(error.message || `Failed to ${isEditMode ? 'update' : 'submit'} finding`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const addRemediationStep = () => {
    setFormData(prev => ({
      ...prev,
      remediation_steps: [...prev.remediation_steps, '']
    }));
  };

  const updateRemediationStep = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      remediation_steps: prev.remediation_steps.map((step, i) => i === index ? value : step)
    }));
  };

  const removeRemediationStep = (index: number) => {
    setFormData(prev => ({
      ...prev,
      remediation_steps: prev.remediation_steps.filter((_, i) => i !== index)
    }));
  };

  const steps = [
    { number: 1, title: 'Basic Info & Description' },
    { number: 2, title: 'Proof of Exploit' },
    { number: 3, title: 'Impact Analysis' },
    { number: 4, title: 'Remediation' }
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditMode ? "Edit Security Finding" : "Submit Security Finding"}
      size="xl"
    >
      <div className="space-y-6">
        {/* Progress Steps */}
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step.number} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                  currentStep >= step.number
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {step.number}
                </div>
                <span className="text-xs mt-2 text-center text-[#6d6760]">{step.title}</span>
              </div>
              {index < steps.length - 1 && (
                <div className={`h-1 flex-1 mx-2 ${
                  currentStep > step.number ? 'bg-blue-600' : 'bg-gray-200'
                }`} />
              )}
            </div>
          ))}
        </div>

        {/* Step Content */}
        <div className="min-h-[400px]">
          {currentStep === 1 && <Step1BasicInfo formData={formData} updateField={updateField} errors={errors} />}
          {currentStep === 2 && <Step2ProofOfExploit formData={formData} updateField={updateField} errors={errors} isUploading={isUploading} uploadedFiles={uploadedFiles} handleFileUpload={handleFileUpload} setUploadedFiles={setUploadedFiles} />}
          {currentStep === 3 && <Step3ImpactAnalysis formData={formData} updateField={updateField} errors={errors} />}
          {currentStep === 4 && (
            <Step4Remediation 
              formData={formData} 
              updateField={updateField} 
              errors={errors}
              addRemediationStep={addRemediationStep}
              updateRemediationStep={updateRemediationStep}
              removeRemediationStep={removeRemediationStep}
            />
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="flex gap-3 pt-4 border-t border-[#e6ddd4]">
          <Button
            variant="outline"
            onClick={currentStep === 1 ? onClose : handleBack}
            className="flex-1"
          >
            {currentStep === 1 ? 'Cancel' : 'Back'}
          </Button>
          {currentStep < 4 ? (
            <Button onClick={handleNext} className="flex-1">
              Next
            </Button>
          ) : (
            <Button
              onClick={handleSubmit}
              isLoading={isSubmitting}
              className="flex-1"
            >
              {isEditMode ? 'Update Finding' : 'Submit Finding'}
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
}


// Step 1: Basic Info & Description
function Step1BasicInfo({ formData, updateField, errors }: any) {
  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 mb-4">
        <div className="flex gap-3">
          <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-blue-900 mb-1">Structured Finding Submission</h4>
            <p className="text-sm text-blue-700">
              Complete all required fields to submit a high-quality security finding.
            </p>
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-[#2d2a26] mb-1">
          Title <span className="text-red-600">*</span>
        </label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => updateField('title', e.target.value)}
          className={`w-full px-3 py-2 border rounded-lg bg-white text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.title ? 'border-red-500' : 'border-[#e6ddd4]'
          }`}
          placeholder="Brief, descriptive title of the vulnerability"
        />
        {errors.title && <p className="mt-1 text-xs text-red-600">{errors.title}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-1">
            Severity <span className="text-red-600">*</span>
          </label>
          <Select
            value={formData.severity}
            onChange={(e) => updateField('severity', e.target.value)}
            options={[
              { value: 'Critical', label: 'Critical' },
              { value: 'High', label: 'High' },
              { value: 'Medium', label: 'Medium' },
              { value: 'Low', label: 'Low' },
              { value: 'Info', label: 'Info' },
            ]}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-1">
            CVSS Score (Optional)
          </label>
          <input
            type="number"
            step="0.1"
            min="0"
            max="10"
            value={formData.cvss_score}
            onChange={(e) => updateField('cvss_score', e.target.value)}
            className="w-full px-3 py-2 border border-[#e6ddd4] rounded-lg bg-white text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="0.0 - 10.0"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-[#2d2a26] mb-1">
          Affected Component <span className="text-red-600">*</span>
        </label>
        <input
          type="text"
          value={formData.affected_component}
          onChange={(e) => updateField('affected_component', e.target.value)}
          className={`w-full px-3 py-2 border rounded-lg bg-white text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.affected_component ? 'border-red-500' : 'border-[#e6ddd4]'
          }`}
          placeholder="e.g., Login API, User Dashboard, Payment Gateway"
        />
        {errors.affected_component && <p className="mt-1 text-xs text-red-600">{errors.affected_component}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-[#2d2a26] mb-1">
          Vulnerability Type <span className="text-red-600">*</span>
        </label>
        <input
          type="text"
          value={formData.vulnerability_type}
          onChange={(e) => updateField('vulnerability_type', e.target.value)}
          className={`w-full px-3 py-2 border rounded-lg bg-white text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.vulnerability_type ? 'border-red-500' : 'border-[#e6ddd4]'
          }`}
          placeholder="e.g., SQL Injection, XSS, CSRF, Authentication Bypass"
        />
        {errors.vulnerability_type && <p className="mt-1 text-xs text-red-600">{errors.vulnerability_type}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-1">
            CWE ID (Optional)
          </label>
          <input
            type="text"
            value={formData.cwe_id}
            onChange={(e) => updateField('cwe_id', e.target.value)}
            className="w-full px-3 py-2 border border-[#e6ddd4] rounded-lg bg-white text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., CWE-79, CWE-89"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-1">
            OWASP Category (Optional)
          </label>
          <input
            type="text"
            value={formData.owasp_category}
            onChange={(e) => updateField('owasp_category', e.target.value)}
            className="w-full px-3 py-2 border border-[#e6ddd4] rounded-lg bg-white text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., A03:2021 - Injection"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-[#2d2a26] mb-1">
          Description <span className="text-red-600">*</span> <span className="text-xs text-[#8b8177]">(min 10 chars)</span>
        </label>
        <Textarea
          value={formData.description}
          onChange={(e) => updateField('description', e.target.value)}
          rows={4}
          className={errors.description ? 'border-red-500' : ''}
          placeholder="Detailed description of the vulnerability, what it affects, and why it's a security issue..."
        />
        {errors.description && <p className="mt-1 text-xs text-red-600">{errors.description}</p>}
        <p className="mt-1 text-xs text-[#8b8177]">{formData.description.length} characters</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-[#2d2a26] mb-1">
          Steps to Reproduce <span className="text-red-600">*</span> <span className="text-xs text-[#8b8177]">(min 20 chars)</span>
        </label>
        <Textarea
          value={formData.reproduction_steps}
          onChange={(e) => updateField('reproduction_steps', e.target.value)}
          rows={6}
          className={errors.reproduction_steps ? 'border-red-500' : ''}
          placeholder="1. Navigate to...&#10;2. Enter the following payload...&#10;3. Click submit...&#10;4. Observe that..."
        />
        {errors.reproduction_steps && <p className="mt-1 text-xs text-red-600">{errors.reproduction_steps}</p>}
        <p className="mt-1 text-xs text-[#8b8177]">{formData.reproduction_steps.length} characters</p>
      </div>
    </div>
  );
}

// Step 2: Proof of Exploit
function Step2ProofOfExploit({ formData, updateField, errors, isUploading, uploadedFiles, handleFileUpload, setUploadedFiles }: any) {
  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-orange-200 bg-orange-50 p-4 mb-4">
        <div className="flex gap-3">
          <AlertCircle className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-orange-900 mb-1">Proof of Exploit Required</h4>
            <p className="text-sm text-orange-700">
              Provide detailed evidence demonstrating the vulnerability. Minimum 50 characters required.
            </p>
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-[#2d2a26] mb-1">
          Proof of Exploit <span className="text-red-600">*</span> <span className="text-xs text-[#8b8177]">(min 50 chars)</span>
        </label>
        <Textarea
          value={formData.proof_of_exploit}
          onChange={(e) => updateField('proof_of_exploit', e.target.value)}
          rows={6}
          className={errors.proof_of_exploit ? 'border-red-500' : ''}
          placeholder="Detailed proof showing the vulnerability can be exploited. Include:&#10;- Exact payloads used&#10;- Server responses&#10;- Evidence of successful exploitation&#10;- Screenshots or logs demonstrating impact"
        />
        {errors.proof_of_exploit && <p className="mt-1 text-xs text-red-600">{errors.proof_of_exploit}</p>}
        <p className="mt-1 text-xs text-[#8b8177]">{formData.proof_of_exploit.length} / 50 characters</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-[#2d2a26] mb-1">
          Exploit Code/Payload (Optional)
        </label>
        <Textarea
          value={formData.exploit_code}
          onChange={(e) => updateField('exploit_code', e.target.value)}
          rows={6}
          placeholder="Paste the exploit code, payload, or script used to demonstrate the vulnerability..."
        />
        <p className="mt-1 text-xs text-[#8b8177]">Include any scripts, payloads, or commands used</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-[#2d2a26] mb-2">
          Evidence Files (Screenshots, Videos, Logs)
        </label>
        
        {/* File Upload Area */}
        <div className={`border-2 border-dashed rounded-xl p-6 text-center transition-colors ${
          isUploading ? 'border-blue-500 bg-blue-50' : 'border-[#e6ddd4] hover:border-blue-400'
        }`}>
          <input
            type="file"
            id="evidence-upload"
            multiple
            accept="image/*,video/*,.txt,.log,.pdf"
            onChange={(e) => {
              if (e.target.files) {
                handleFileUpload(e.target.files);
              }
            }}
            disabled={isUploading}
            className="hidden"
          />
          <label htmlFor="evidence-upload" className={`cursor-pointer ${isUploading ? 'opacity-50' : ''}`}>
            {isUploading ? (
              <>
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2" />
                <p className="text-sm text-blue-600 mb-1">Uploading files...</p>
              </>
            ) : (
              <>
                <Upload className="h-8 w-8 text-[#8b8177] mx-auto mb-2" />
                <p className="text-sm text-[#6d6760] mb-1">Click to upload evidence files</p>
                <p className="text-xs text-[#8b8177]">Images (PNG, JPG, GIF), Videos (MP4, MOV, AVI, WEBM), Documents (PDF, TXT, LOG) up to 10MB each</p>
              </>
            )}
          </label>
        </div>

        {/* Uploaded Files List */}
        {uploadedFiles.length > 0 && (
          <div className="mt-3 space-y-2">
            <label className="block text-sm font-medium text-[#2d2a26]">
              Uploaded Files ({uploadedFiles.length})
            </label>
            {uploadedFiles.map((file, idx) => (
              <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-green-50 border border-green-200">
                <span className="text-sm text-green-700 flex items-center gap-2">
                  <CheckCircle className="h-4 w-4" />
                  {file.name}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    // Remove from uploaded files
                    setUploadedFiles(prev => prev.filter((_, i) => i !== idx));
                    // Remove URL from screenshots
                    const newScreenshots = formData.exploit_screenshots.filter((url: string) => url !== file.url);
                    updateField('exploit_screenshots', newScreenshots);
                  }}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        )}

        {/* Screenshot URLs (Alternative) */}
        <div className="mt-4">
          <label className="block text-sm font-medium text-[#2d2a26] mb-2">
            Or paste screenshot URLs
          </label>
          <div className="space-y-2">
            {formData.exploit_screenshots.filter((url: string) => 
              !uploadedFiles.some(f => f.url === url)
            ).map((url: string, index: number) => (
              <div key={index} className="flex gap-2">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => {
                    const allScreenshots = [...formData.exploit_screenshots];
                    const urlIndex = allScreenshots.indexOf(url);
                    if (urlIndex !== -1) {
                      allScreenshots[urlIndex] = e.target.value;
                      updateField('exploit_screenshots', allScreenshots);
                    }
                  }}
                  className="flex-1 px-3 py-2 border border-[#e6ddd4] rounded-lg bg-white text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://example.com/screenshot.png"
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const newScreenshots = formData.exploit_screenshots.filter((u: string) => u !== url);
                    updateField('exploit_screenshots', newScreenshots);
                  }}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
            <Button
              variant="outline"
              size="sm"
              onClick={() => updateField('exploit_screenshots', [...formData.exploit_screenshots, ''])}
            >
              <Upload className="h-4 w-4 mr-1" />
              Add Screenshot URL
            </Button>
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-[#2d2a26] mb-1">
          Video Demonstration URL (Optional)
        </label>
        <input
          type="url"
          value={formData.exploit_video_url}
          onChange={(e) => updateField('exploit_video_url', e.target.value)}
          className="w-full px-3 py-2 border border-[#e6ddd4] rounded-lg bg-white text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="https://youtube.com/watch?v=..."
        />
        <p className="mt-1 text-xs text-[#8b8177]">Link to video demonstration (YouTube, Vimeo, etc.)</p>
      </div>

      {/* CVSS Metrics */}
      <div className="pt-4 border-t border-[#e6ddd4]">
        <h4 className="font-semibold text-[#2d2a26] mb-3">Attack Vector Details (CVSS)</h4>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">Attack Vector</label>
            <Select
              value={formData.attack_vector}
              onChange={(e) => updateField('attack_vector', e.target.value)}
              options={[
                { value: 'Network', label: 'Network' },
                { value: 'Adjacent', label: 'Adjacent' },
                { value: 'Local', label: 'Local' },
                { value: 'Physical', label: 'Physical' },
              ]}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">Attack Complexity</label>
            <Select
              value={formData.attack_complexity}
              onChange={(e) => updateField('attack_complexity', e.target.value)}
              options={[
                { value: 'Low', label: 'Low' },
                { value: 'High', label: 'High' },
              ]}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">Privileges Required</label>
            <Select
              value={formData.privileges_required}
              onChange={(e) => updateField('privileges_required', e.target.value)}
              options={[
                { value: 'None', label: 'None' },
                { value: 'Low', label: 'Low' },
                { value: 'High', label: 'High' },
              ]}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">User Interaction</label>
            <Select
              value={formData.user_interaction}
              onChange={(e) => updateField('user_interaction', e.target.value)}
              options={[
                { value: 'None', label: 'None' },
                { value: 'Required', label: 'Required' },
              ]}
            />
          </div>
        </div>
      </div>
    </div>
  );
}


// Step 3: Impact Analysis
function Step3ImpactAnalysis({ formData, updateField, errors }: any) {
  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-red-200 bg-red-50 p-4 mb-4">
        <div className="flex gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-red-900 mb-1">Impact Analysis Required</h4>
            <p className="text-sm text-red-700">
              Describe the business and technical impact. Minimum 50 characters required.
            </p>
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-[#2d2a26] mb-1">
          Impact Analysis <span className="text-red-600">*</span> <span className="text-xs text-[#8b8177]">(min 50 chars)</span>
        </label>
        <Textarea
          value={formData.impact_analysis}
          onChange={(e) => updateField('impact_analysis', e.target.value)}
          rows={6}
          className={errors.impact_analysis ? 'border-red-500' : ''}
          placeholder="Detailed analysis of the impact:&#10;- What data or systems are affected?&#10;- What can an attacker achieve?&#10;- What is the business impact?&#10;- How many users are affected?"
        />
        {errors.impact_analysis && <p className="mt-1 text-xs text-red-600">{errors.impact_analysis}</p>}
        <p className="mt-1 text-xs text-[#8b8177]">{formData.impact_analysis.length} / 50 characters</p>
      </div>

      <div>
        <label className="block text-sm font-medium text-[#2d2a26] mb-1">
          Business Impact Level <span className="text-red-600">*</span>
        </label>
        <Select
          value={formData.business_impact}
          onChange={(e) => updateField('business_impact', e.target.value)}
          options={[
            { value: 'Critical', label: 'Critical - Severe business disruption' },
            { value: 'High', label: 'High - Significant business impact' },
            { value: 'Medium', label: 'Medium - Moderate business impact' },
            { value: 'Low', label: 'Low - Minor business impact' },
          ]}
        />
      </div>

      <div>
        <h4 className="font-semibold text-[#2d2a26] mb-3">Technical Impact (CIA Triad) <span className="text-red-600">*</span></h4>
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">Confidentiality</label>
            <Select
              value={formData.technical_impact.confidentiality}
              onChange={(e) => updateField('technical_impact', {
                ...formData.technical_impact,
                confidentiality: e.target.value
              })}
              options={[
                { value: 'None', label: 'None - No impact' },
                { value: 'Low', label: 'Low - Limited disclosure' },
                { value: 'High', label: 'High - Total disclosure' },
              ]}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">Integrity</label>
            <Select
              value={formData.technical_impact.integrity}
              onChange={(e) => updateField('technical_impact', {
                ...formData.technical_impact,
                integrity: e.target.value
              })}
              options={[
                { value: 'None', label: 'None - No impact' },
                { value: 'Low', label: 'Low - Limited modification' },
                { value: 'High', label: 'High - Total modification' },
              ]}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[#2d2a26] mb-1">Availability</label>
            <Select
              value={formData.technical_impact.availability}
              onChange={(e) => updateField('technical_impact', {
                ...formData.technical_impact,
                availability: e.target.value
              })}
              options={[
                { value: 'None', label: 'None - No impact' },
                { value: 'Low', label: 'Low - Performance degradation' },
                { value: 'High', label: 'High - Total shutdown' },
              ]}
            />
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-[#2d2a26] mb-1">
          Affected Users (Optional)
        </label>
        <input
          type="text"
          value={formData.affected_users}
          onChange={(e) => updateField('affected_users', e.target.value)}
          className="w-full px-3 py-2 border border-[#e6ddd4] rounded-lg bg-white text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., All users, Admin users only, Premium subscribers"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-[#2d2a26] mb-1">
          Data at Risk (Optional)
        </label>
        <Textarea
          value={formData.data_at_risk}
          onChange={(e) => updateField('data_at_risk', e.target.value)}
          rows={3}
          placeholder="Describe what data could be compromised: PII, credentials, financial data, etc."
        />
      </div>
    </div>
  );
}

// Step 4: Remediation
function Step4Remediation({ formData, updateField, errors, addRemediationStep, updateRemediationStep, removeRemediationStep }: any) {
  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-green-200 bg-green-50 p-4 mb-4">
        <div className="flex gap-3">
          <AlertCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-green-900 mb-1">Remediation Recommendations Required</h4>
            <p className="text-sm text-green-700">
              Provide clear remediation guidance. Minimum 50 characters required.
            </p>
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-[#2d2a26] mb-1">
          Remediation Overview <span className="text-red-600">*</span> <span className="text-xs text-[#8b8177]">(min 50 chars)</span>
        </label>
        <Textarea
          value={formData.remediation}
          onChange={(e) => updateField('remediation', e.target.value)}
          rows={6}
          className={errors.remediation ? 'border-red-500' : ''}
          placeholder="Detailed remediation recommendations:&#10;- What needs to be fixed?&#10;- How should it be fixed?&#10;- What security controls should be implemented?&#10;- Any architectural changes needed?"
        />
        {errors.remediation && <p className="mt-1 text-xs text-red-600">{errors.remediation}</p>}
        <p className="mt-1 text-xs text-[#8b8177]">{formData.remediation.length} / 50 characters</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-1">
            Remediation Priority <span className="text-red-600">*</span>
          </label>
          <Select
            value={formData.remediation_priority}
            onChange={(e) => updateField('remediation_priority', e.target.value)}
            options={[
              { value: 'Immediate', label: 'Immediate - Fix ASAP' },
              { value: 'High', label: 'High - Within days' },
              { value: 'Medium', label: 'Medium - Within weeks' },
              { value: 'Low', label: 'Low - Can wait' },
            ]}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-[#2d2a26] mb-1">
            Remediation Effort <span className="text-red-600">*</span>
          </label>
          <Select
            value={formData.remediation_effort}
            onChange={(e) => updateField('remediation_effort', e.target.value)}
            options={[
              { value: 'Low', label: 'Low - Quick fix' },
              { value: 'Medium', label: 'Medium - Moderate work' },
              { value: 'High', label: 'High - Significant work' },
              { value: 'Very High', label: 'Very High - Major refactor' },
            ]}
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-[#2d2a26] mb-1">
          Remediation Steps <span className="text-red-600">*</span>
        </label>
        <div className="space-y-2">
          {formData.remediation_steps.map((step: string, index: number) => (
            <div key={index} className="flex gap-2">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-semibold mt-2">
                {index + 1}
              </span>
              <input
                type="text"
                value={step}
                onChange={(e) => updateRemediationStep(index, e.target.value)}
                className="flex-1 px-3 py-2 border border-[#e6ddd4] rounded-lg bg-white text-[#2d2a26] focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder={`Step ${index + 1}`}
              />
              {formData.remediation_steps.length > 1 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => removeRemediationStep(index)}
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          ))}
          {errors.remediation_steps && <p className="mt-1 text-xs text-red-600">{errors.remediation_steps}</p>}
          <Button
            variant="outline"
            size="sm"
            onClick={addRemediationStep}
          >
            + Add Step
          </Button>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-[#2d2a26] mb-1">
          Code Fix Example (Optional)
        </label>
        <Textarea
          value={formData.code_fix_example}
          onChange={(e) => updateField('code_fix_example', e.target.value)}
          rows={6}
          placeholder="Provide example code showing how to fix the vulnerability..."
        />
        <p className="mt-1 text-xs text-[#8b8177]">Include before/after code examples if applicable</p>
      </div>
    </div>
  );
}

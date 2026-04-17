'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import { useApiMutation } from '@/hooks/useApiMutation';
import { AlertCircle, ChevronRight, ChevronLeft, Check } from 'lucide-react';

interface PTaaSEngagementCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const methodologies = [
  { value: 'OWASP', label: 'OWASP Testing Guide' },
  { value: 'PTES', label: 'PTES (Penetration Testing Execution Standard)' },
  { value: 'NIST', label: 'NIST SP 800-115' },
  { value: 'OSSTMM', label: 'OSSTMM (Open Source Security Testing)' },
  { value: 'Custom', label: 'Custom Methodology' },
];

const engagementTypes = [
  { value: 'CONTINUOUS', label: 'Continuous', description: 'Ongoing testing with no fixed end date' },
  { value: 'TIME_BASED', label: 'Time-Based', description: 'Fixed duration engagement (e.g., 30 days)' },
  { value: 'PROJECT_BASED', label: 'Project-Based', description: 'Specific project or release testing' },
];

const researcherModels = [
  { value: 'PRIVATE', label: 'Private PTaaS', description: 'Invite selected researchers only' },
  { value: 'MANAGED_CROWD', label: 'Managed Crowd', description: 'Platform auto-matches researchers' },
  { value: 'HYBRID', label: 'Hybrid', description: 'Combination of private and crowd' },
];

const pricingModels = [
  { value: 'FIXED', label: 'Fixed Payment', description: 'One-time payment for the engagement' },
  { value: 'SUBSCRIPTION', label: 'Subscription', description: 'Recurring payment (monthly/quarterly/yearly)' },
];

const complianceFrameworks = [
  'PCI DSS', 'HIPAA', 'SOC 2', 'ISO 27001', 'GDPR', 'NIST', 'FedRAMP', 'None'
];

export default function PTaaSEngagementCreateModal({
  isOpen,
  onClose,
  onSuccess,
}: PTaaSEngagementCreateModalProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // Step 1: Define Engagement
    name: '',
    description: '',
    engagement_type: 'TIME_BASED',
    
    // Step 2: Scope Definition
    scope: {
      in_scope_targets: [] as string[],
      out_of_scope_targets: [] as string[],
      allowed_techniques: [] as string[],
      testing_methodology: 'OWASP',
      custom_methodology_details: '',
    },
    
    // Step 3: Researcher Model
    researcher_model: 'MANAGED_CROWD',
    skill_requirements: [] as string[],
    min_reputation_score: 0,
    team_size: 1,
    
    // Step 4: SLA & Rules
    response_sla_hours: 24,
    fix_timeline_days: 30,
    retesting_enabled: true,
    communication_rules: '',
    
    // Step 5: Reward Model
    pricing_model: 'FIXED',
    base_price: '',
    subscription_interval: 'monthly',
    
    // Timeline
    start_date: '',
    end_date: '',
    
    // Compliance
    compliance_requirements: [] as string[],
    compliance_notes: '',
    
    // Deliverables
    deliverables: ['Executive Report', 'Technical Report', 'Remediation Guide'] as string[],
  });

  // Temporary input states
  const [inScopeInput, setInScopeInput] = useState('');
  const [outScopeInput, setOutScopeInput] = useState('');
  const [techniqueInput, setTechniqueInput] = useState('');
  const [skillInput, setSkillInput] = useState('');

  const { mutate: createEngagement, isLoading, error } = useApiMutation(
    '/ptaas/engagements',
    'POST',
    {
      onSuccess: () => {
        onSuccess();
        resetForm();
      },
    }
  );

  const resetForm = () => {
    setCurrentStep(1);
    setFormData({
      name: '',
      description: '',
      engagement_type: 'TIME_BASED',
      scope: {
        in_scope_targets: [],
        out_of_scope_targets: [],
        allowed_techniques: [],
        testing_methodology: 'OWASP',
        custom_methodology_details: '',
      },
      researcher_model: 'MANAGED_CROWD',
      skill_requirements: [],
      min_reputation_score: 0,
      team_size: 1,
      response_sla_hours: 24,
      fix_timeline_days: 30,
      retesting_enabled: true,
      communication_rules: '',
      pricing_model: 'FIXED',
      base_price: '',
      subscription_interval: 'monthly',
      start_date: '',
      end_date: '',
      compliance_requirements: [],
      compliance_notes: '',
      deliverables: ['Executive Report', 'Technical Report', 'Remediation Guide'],
    });
    setInScopeInput('');
    setOutScopeInput('');
    setTechniqueInput('');
    setSkillInput('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // For continuous engagements, set end date to 10 years in the future if not provided
    let endDate = formData.end_date;
    if (formData.engagement_type === 'CONTINUOUS' && !endDate) {
      const futureDate = new Date(formData.start_date);
      futureDate.setFullYear(futureDate.getFullYear() + 10);
      endDate = futureDate.toISOString().split('T')[0];
    }
    
    // Transform data to match backend API
    const payload = {
      name: formData.name,
      description: formData.description,
      scope: formData.scope,
      testing_methodology: formData.scope.testing_methodology,
      custom_methodology_details: formData.scope.custom_methodology_details || null,
      start_date: new Date(formData.start_date).toISOString(),
      end_date: new Date(endDate).toISOString(),
      compliance_requirements: formData.compliance_requirements.length > 0 ? formData.compliance_requirements : null,
      compliance_notes: formData.compliance_notes || null,
      deliverables: {
        reports: formData.deliverables,
        additional_items: []
      },
      pricing_model: formData.pricing_model === 'PER_FINDING' || formData.pricing_model === 'NO_REWARD' 
        ? 'FIXED' 
        : formData.pricing_model,
      base_price: formData.base_price ? parseFloat(formData.base_price) : 0,
      subscription_interval: formData.pricing_model === 'SUBSCRIPTION' ? formData.subscription_interval : null,
      team_size: formData.team_size,
      platform_commission_rate: 30.00, // Default 30% commission
    };
    
    createEngagement(payload);
  };

  const handleClose = () => {
    if (!isLoading) {
      resetForm();
      onClose();
    }
  };

  const nextStep = () => {
    if (currentStep < 5) setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const addToArray = (field: string, value: string, setter: (val: string) => void) => {
    if (value.trim()) {
      if (field === 'in_scope_targets') {
        setFormData({
          ...formData,
          scope: {
            ...formData.scope,
            in_scope_targets: [...formData.scope.in_scope_targets, value.trim()]
          }
        });
      } else if (field === 'out_of_scope_targets') {
        setFormData({
          ...formData,
          scope: {
            ...formData.scope,
            out_of_scope_targets: [...formData.scope.out_of_scope_targets, value.trim()]
          }
        });
      } else if (field === 'allowed_techniques') {
        setFormData({
          ...formData,
          scope: {
            ...formData.scope,
            allowed_techniques: [...formData.scope.allowed_techniques, value.trim()]
          }
        });
      } else if (field === 'skill_requirements') {
        setFormData({
          ...formData,
          skill_requirements: [...formData.skill_requirements, value.trim()]
        });
      }
      setter('');
    }
  };

  const removeFromArray = (field: string, index: number) => {
    if (field === 'in_scope_targets') {
      setFormData({
        ...formData,
        scope: {
          ...formData.scope,
          in_scope_targets: formData.scope.in_scope_targets.filter((_, i) => i !== index)
        }
      });
    } else if (field === 'out_of_scope_targets') {
      setFormData({
        ...formData,
        scope: {
          ...formData.scope,
          out_of_scope_targets: formData.scope.out_of_scope_targets.filter((_, i) => i !== index)
        }
      });
    } else if (field === 'allowed_techniques') {
      setFormData({
        ...formData,
        scope: {
          ...formData.scope,
          allowed_techniques: formData.scope.allowed_techniques.filter((_, i) => i !== index)
        }
      });
    } else if (field === 'skill_requirements') {
      setFormData({
        ...formData,
        skill_requirements: formData.skill_requirements.filter((_, i) => i !== index)
      });
    }
  };

  const toggleCompliance = (framework: string) => {
    if (formData.compliance_requirements.includes(framework)) {
      setFormData({
        ...formData,
        compliance_requirements: formData.compliance_requirements.filter(f => f !== framework)
      });
    } else {
      setFormData({
        ...formData,
        compliance_requirements: [...formData.compliance_requirements, framework]
      });
    }
  };

  const steps = [
    { number: 1, title: 'Define Engagement', description: 'Basic information' },
    { number: 2, title: 'Scope Definition', description: 'Testing scope & methodology' },
    { number: 3, title: 'Researcher Model', description: 'Team selection' },
    { number: 4, title: 'SLA & Rules', description: 'Timeline & policies' },
    { number: 5, title: 'Reward Model', description: 'Pricing & payment' },
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Create PTaaS Engagement"
      size="xl"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="font-semibold text-red-900">Error creating engagement</h4>
                <p className="mt-1 text-sm text-red-700">{error.message}</p>
              </div>
            </div>
          </div>
        )}

        {/* Step Indicator */}
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step.number} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  currentStep === step.number
                    ? 'border-[#3b82f6] bg-[#3b82f6] text-white'
                    : currentStep > step.number
                    ? 'border-green-500 bg-green-500 text-white'
                    : 'border-[#e6ddd4] bg-white text-[#8b8177]'
                }`}>
                  {currentStep > step.number ? (
                    <Check className="h-5 w-5" />
                  ) : (
                    <span className="text-sm font-semibold">{step.number}</span>
                  )}
                </div>
                <div className="mt-2 text-center">
                  <p className={`text-xs font-medium ${
                    currentStep === step.number ? 'text-[#3b82f6]' : 'text-[#8b8177]'
                  }`}>
                    {step.title}
                  </p>
                  <p className="text-xs text-[#8b8177] mt-0.5">{step.description}</p>
                </div>
              </div>
              {index < steps.length - 1 && (
                <div className={`h-0.5 w-full mx-2 ${
                  currentStep > step.number ? 'bg-green-500' : 'bg-[#e6ddd4]'
                }`} />
              )}
            </div>
          ))}
        </div>

        {/* Step Content */}
        <div className="min-h-[400px]">
          {/* Step 1: Define Engagement */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-[#2d2a26] mb-4">Define Engagement</h3>
                
                {/* Engagement Name */}
                <div className="mb-4">
                  <label htmlFor="name" className="block text-sm font-medium text-[#2d2a26] mb-2">
                    Engagement Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="name"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                    placeholder="e.g., Q2 2026 Web Application Pentest"
                  />
                </div>

                {/* Description */}
                <div className="mb-4">
                  <label htmlFor="description" className="block text-sm font-medium text-[#2d2a26] mb-2">
                    Description <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    id="description"
                    required
                    rows={3}
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                    placeholder="Describe the engagement objectives and goals..."
                  />
                </div>

                {/* Engagement Type */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-[#2d2a26] mb-3">
                    Engagement Type <span className="text-red-500">*</span>
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {engagementTypes.map((type) => (
                      <button
                        key={type.value}
                        type="button"
                        onClick={() => setFormData({ ...formData, engagement_type: type.value })}
                        className={`p-4 rounded-xl border-2 text-left transition-all ${
                          formData.engagement_type === type.value
                            ? 'border-[#3b82f6] bg-blue-50'
                            : 'border-[#e6ddd4] bg-white hover:border-[#3b82f6]/50'
                        }`}
                      >
                        <p className="font-semibold text-sm text-[#2d2a26]">{type.label}</p>
                        <p className="text-xs text-[#8b8177] mt-1">{type.description}</p>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Timeline */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="start_date" className="block text-sm font-medium text-[#2d2a26] mb-2">
                      Start Date <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      id="start_date"
                      required
                      value={formData.start_date}
                      onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                      className="block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                    />
                  </div>
                  <div>
                    <label htmlFor="end_date" className="block text-sm font-medium text-[#2d2a26] mb-2">
                      End Date {formData.engagement_type !== 'CONTINUOUS' && <span className="text-red-500">*</span>}
                    </label>
                    <input
                      type="date"
                      id="end_date"
                      required={formData.engagement_type !== 'CONTINUOUS'}
                      value={formData.end_date}
                      onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                      className="block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                      disabled={formData.engagement_type === 'CONTINUOUS'}
                    />
                    {formData.engagement_type === 'CONTINUOUS' && (
                      <p className="mt-1.5 text-xs text-[#8b8177]">
                        Continuous engagements have no fixed end date
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Scope Definition */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-[#2d2a26] mb-4">Scope Definition</h3>
              
              {/* In-Scope Targets */}
              <div>
                <label className="block text-sm font-medium text-[#2d2a26] mb-2">
                  In-Scope Targets <span className="text-red-500">*</span>
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={inScopeInput}
                    onChange={(e) => setInScopeInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('in_scope_targets', inScopeInput, setInScopeInput))}
                    className="flex-1 rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                    placeholder="e.g., https://example.com, 192.168.1.0/24"
                  />
                  <Button
                    type="button"
                    onClick={() => addToArray('in_scope_targets', inScopeInput, setInScopeInput)}
                  >
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.scope.in_scope_targets.map((target, index) => (
                    <span key={index} className="inline-flex items-center gap-1.5 rounded-lg bg-blue-50 px-3 py-1.5 text-sm text-blue-700">
                      {target}
                      <button
                        type="button"
                        onClick={() => removeFromArray('in_scope_targets', index)}
                        className="hover:text-blue-900"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Out-of-Scope Targets */}
              <div>
                <label className="block text-sm font-medium text-[#2d2a26] mb-2">
                  Out-of-Scope Targets
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={outScopeInput}
                    onChange={(e) => setOutScopeInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('out_of_scope_targets', outScopeInput, setOutScopeInput))}
                    className="flex-1 rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                    placeholder="e.g., https://example.com/admin"
                  />
                  <Button
                    type="button"
                    onClick={() => addToArray('out_of_scope_targets', outScopeInput, setOutScopeInput)}
                  >
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.scope.out_of_scope_targets.map((target, index) => (
                    <span key={index} className="inline-flex items-center gap-1.5 rounded-lg bg-red-50 px-3 py-1.5 text-sm text-red-700">
                      {target}
                      <button
                        type="button"
                        onClick={() => removeFromArray('out_of_scope_targets', index)}
                        className="hover:text-red-900"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Testing Methodology */}
              <div>
                <label htmlFor="methodology" className="block text-sm font-medium text-[#2d2a26] mb-2">
                  Testing Methodology <span className="text-red-500">*</span>
                </label>
                <select
                  id="methodology"
                  required
                  value={formData.scope.testing_methodology}
                  onChange={(e) => setFormData({
                    ...formData,
                    scope: { ...formData.scope, testing_methodology: e.target.value }
                  })}
                  className="block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                >
                  {methodologies.map((method) => (
                    <option key={method.value} value={method.value}>
                      {method.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Allowed Techniques */}
              <div>
                <label className="block text-sm font-medium text-[#2d2a26] mb-2">
                  Allowed Testing Techniques
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={techniqueInput}
                    onChange={(e) => setTechniqueInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('allowed_techniques', techniqueInput, setTechniqueInput))}
                    className="flex-1 rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                    placeholder="e.g., SQL Injection, XSS, CSRF"
                  />
                  <Button
                    type="button"
                    onClick={() => addToArray('allowed_techniques', techniqueInput, setTechniqueInput)}
                  >
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.scope.allowed_techniques.map((technique, index) => (
                    <span key={index} className="inline-flex items-center gap-1.5 rounded-lg bg-green-50 px-3 py-1.5 text-sm text-green-700">
                      {technique}
                      <button
                        type="button"
                        onClick={() => removeFromArray('allowed_techniques', index)}
                        className="hover:text-green-900"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Compliance Requirements */}
              <div>
                <label className="block text-sm font-medium text-[#2d2a26] mb-3">
                  Compliance Requirements
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {complianceFrameworks.map((framework) => (
                    <button
                      key={framework}
                      type="button"
                      onClick={() => toggleCompliance(framework)}
                      className={`px-3 py-2 rounded-lg border text-sm transition-all ${
                        formData.compliance_requirements.includes(framework)
                          ? 'border-[#3b82f6] bg-blue-50 text-[#3b82f6]'
                          : 'border-[#e6ddd4] bg-white text-[#6d6760] hover:border-[#3b82f6]/50'
                      }`}
                    >
                      {framework}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Researcher Model */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-[#2d2a26] mb-4">Researcher Model Selection</h3>
              
              {/* Researcher Model */}
              <div>
                <label className="block text-sm font-medium text-[#2d2a26] mb-3">
                  Researcher Model <span className="text-red-500">*</span>
                </label>
                <div className="space-y-3">
                  {researcherModels.map((model) => (
                    <button
                      key={model.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, researcher_model: model.value })}
                      className={`w-full p-4 rounded-xl border-2 text-left transition-all ${
                        formData.researcher_model === model.value
                          ? 'border-[#3b82f6] bg-blue-50'
                          : 'border-[#e6ddd4] bg-white hover:border-[#3b82f6]/50'
                      }`}
                    >
                      <p className="font-semibold text-sm text-[#2d2a26]">{model.label}</p>
                      <p className="text-xs text-[#8b8177] mt-1">{model.description}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Team Size */}
              <div>
                <label htmlFor="team_size" className="block text-sm font-medium text-[#2d2a26] mb-2">
                  Team Size <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  id="team_size"
                  required
                  min="1"
                  value={formData.team_size}
                  onChange={(e) => setFormData({ ...formData, team_size: parseInt(e.target.value) || 1 })}
                  className="block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                />
                <p className="mt-1.5 text-xs text-[#8b8177]">
                  Number of researchers needed for this engagement
                </p>
              </div>

              {/* Skill Requirements */}
              <div>
                <label className="block text-sm font-medium text-[#2d2a26] mb-2">
                  Skill Requirements
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={skillInput}
                    onChange={(e) => setSkillInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addToArray('skill_requirements', skillInput, setSkillInput))}
                    className="flex-1 rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                    placeholder="e.g., Web Application Security, API Testing"
                  />
                  <Button
                    type="button"
                    onClick={() => addToArray('skill_requirements', skillInput, setSkillInput)}
                  >
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.skill_requirements.map((skill, index) => (
                    <span key={index} className="inline-flex items-center gap-1.5 rounded-lg bg-purple-50 px-3 py-1.5 text-sm text-purple-700">
                      {skill}
                      <button
                        type="button"
                        onClick={() => removeFromArray('skill_requirements', index)}
                        className="hover:text-purple-900"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Minimum Reputation Score */}
              <div>
                <label htmlFor="min_reputation" className="block text-sm font-medium text-[#2d2a26] mb-2">
                  Minimum Reputation Score
                </label>
                <input
                  type="number"
                  id="min_reputation"
                  min="0"
                  max="100"
                  value={formData.min_reputation_score}
                  onChange={(e) => setFormData({ ...formData, min_reputation_score: parseInt(e.target.value) || 0 })}
                  className="block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                />
                <p className="mt-1.5 text-xs text-[#8b8177]">
                  Minimum reputation score required (0-100)
                </p>
              </div>

              {/* Researcher Browser/Filter - Only for PRIVATE model */}
              {formData.researcher_model === 'PRIVATE' && (
                <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
                  <p className="text-sm text-blue-900 font-medium mb-3">
                    Private PTaaS: You can invite specific researchers after creating the engagement
                  </p>
                  <p className="text-xs text-blue-700">
                    After creating this engagement, you'll be able to browse and filter researchers, then send invitations to your selected team members.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Step 4: SLA & Rules */}
          {currentStep === 4 && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-[#2d2a26] mb-4">SLA & Rules Setup</h3>
              
              {/* Response SLA */}
              <div>
                <label htmlFor="response_sla" className="block text-sm font-medium text-[#2d2a26] mb-2">
                  Response SLA (hours) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  id="response_sla"
                  required
                  min="1"
                  value={formData.response_sla_hours}
                  onChange={(e) => setFormData({ ...formData, response_sla_hours: parseInt(e.target.value) || 24 })}
                  className="block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                />
                <p className="mt-1.5 text-xs text-[#8b8177]">
                  Expected response time for findings (e.g., 24 hours)
                </p>
              </div>

              {/* Fix Timeline */}
              <div>
                <label htmlFor="fix_timeline" className="block text-sm font-medium text-[#2d2a26] mb-2">
                  Fix Timeline (days) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  id="fix_timeline"
                  required
                  min="1"
                  value={formData.fix_timeline_days}
                  onChange={(e) => setFormData({ ...formData, fix_timeline_days: parseInt(e.target.value) || 30 })}
                  className="block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                />
                <p className="mt-1.5 text-xs text-[#8b8177]">
                  Expected timeline to fix vulnerabilities (e.g., 30 days)
                </p>
              </div>

              {/* Retesting Enabled */}
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="retesting"
                  checked={formData.retesting_enabled}
                  onChange={(e) => setFormData({ ...formData, retesting_enabled: e.target.checked })}
                  className="h-5 w-5 rounded border-[#e6ddd4] text-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                />
                <label htmlFor="retesting" className="text-sm font-medium text-[#2d2a26]">
                  Enable Free Retesting
                </label>
              </div>
              <p className="text-xs text-[#8b8177] -mt-4 ml-8">
                Allow researchers to retest fixed vulnerabilities at no additional cost
              </p>

              {/* Communication Rules */}
              <div>
                <label htmlFor="communication_rules" className="block text-sm font-medium text-[#2d2a26] mb-2">
                  Communication Rules
                </label>
                <textarea
                  id="communication_rules"
                  rows={4}
                  value={formData.communication_rules}
                  onChange={(e) => setFormData({ ...formData, communication_rules: e.target.value })}
                  className="block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                  placeholder="Define communication guidelines, escalation procedures, etc."
                />
              </div>
            </div>
          )}

          {/* Step 5: Reward Model */}
          {currentStep === 5 && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-[#2d2a26] mb-4">Reward Model</h3>
              
              {/* Pricing Model */}
              <div>
                <label className="block text-sm font-medium text-[#2d2a26] mb-3">
                  Pricing Model <span className="text-red-500">*</span>
                </label>
                <div className="space-y-3">
                  {pricingModels.map((model) => (
                    <button
                      key={model.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, pricing_model: model.value })}
                      className={`w-full p-4 rounded-xl border-2 text-left transition-all ${
                        formData.pricing_model === model.value
                          ? 'border-[#3b82f6] bg-blue-50'
                          : 'border-[#e6ddd4] bg-white hover:border-[#3b82f6]/50'
                      }`}
                    >
                      <p className="font-semibold text-sm text-[#2d2a26]">{model.label}</p>
                      <p className="text-xs text-[#8b8177] mt-1">{model.description}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Base Price */}
              <div>
                <label htmlFor="base_price" className="block text-sm font-medium text-[#2d2a26] mb-2">
                  Base Price (ETB) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  id="base_price"
                  required
                  min="0"
                  step="0.01"
                  value={formData.base_price}
                  onChange={(e) => setFormData({ ...formData, base_price: e.target.value })}
                  className="block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] placeholder-[#8b8177] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                  placeholder="0.00"
                />
                <p className="mt-1.5 text-xs text-[#8b8177]">
                  Platform commission (30%) will be added automatically
                </p>
              </div>

              {/* Subscription Interval */}
              {formData.pricing_model === 'SUBSCRIPTION' && (
                <div>
                  <label htmlFor="subscription_interval" className="block text-sm font-medium text-[#2d2a26] mb-2">
                    Subscription Interval <span className="text-red-500">*</span>
                  </label>
                  <select
                    id="subscription_interval"
                    required
                    value={formData.subscription_interval}
                    onChange={(e) => setFormData({ ...formData, subscription_interval: e.target.value })}
                    className="block w-full rounded-xl border border-[#e6ddd4] bg-white px-4 py-2.5 text-[#2d2a26] focus:border-[#3b82f6] focus:outline-none focus:ring-2 focus:ring-[#3b82f6]/20"
                  >
                    <option value="monthly">Monthly</option>
                    <option value="quarterly">Quarterly</option>
                    <option value="yearly">Yearly</option>
                  </select>
                </div>
              )}

              {/* Summary */}
              <div className="rounded-xl border border-[#e6ddd4] bg-[#faf6f1] p-4">
                <h4 className="font-semibold text-[#2d2a26] mb-3">Engagement Summary</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-[#6d6760]">Engagement Name:</span>
                    <span className="font-medium text-[#2d2a26]">{formData.name || 'Not set'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#6d6760]">Type:</span>
                    <span className="font-medium text-[#2d2a26]">{formData.engagement_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#6d6760]">Methodology:</span>
                    <span className="font-medium text-[#2d2a26]">{formData.scope?.testing_methodology || formData.testing_methodology || 'Not set'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#6d6760]">Team Size:</span>
                    <span className="font-medium text-[#2d2a26]">{formData.team_size} researcher(s)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#6d6760]">Pricing Model:</span>
                    <span className="font-medium text-[#2d2a26]">{formData.pricing_model}</span>
                  </div>
                  {formData.base_price && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-[#6d6760]">Base Price:</span>
                        <span className="font-medium text-[#2d2a26]">{parseFloat(formData.base_price).toFixed(2)} ETB</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[#6d6760]">Platform Commission (30%):</span>
                        <span className="font-medium text-[#2d2a26]">{(parseFloat(formData.base_price) * 0.30).toFixed(2)} ETB</span>
                      </div>
                      <div className="flex justify-between border-t border-[#e6ddd4] pt-2 mt-2">
                        <span className="font-semibold text-[#2d2a26]">Total:</span>
                        <span className="font-semibold text-[#2d2a26]">{(parseFloat(formData.base_price) * 1.30).toFixed(2)} ETB</span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between border-t border-[#e6ddd4] pt-6">
          <div>
            {currentStep > 1 && (
              <Button
                type="button"
                variant="outline"
                onClick={prevStep}
                disabled={isLoading}
              >
                <ChevronLeft className="h-4 w-4 mr-1.5" />
                Previous
              </Button>
            )}
          </div>
          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            {currentStep < 5 ? (
              <Button
                type="button"
                onClick={nextStep}
              >
                Next
                <ChevronRight className="h-4 w-4 ml-1.5" />
              </Button>
            ) : (
              <Button
                type="submit"
                isLoading={isLoading}
                disabled={isLoading}
              >
                Create Engagement
              </Button>
            )}
          </div>
        </div>
      </form>
    </Modal>
  );
}

'use client';

import { useState } from 'react';
import {
  Button,
  Input,
  Select,
  Textarea,
  Checkbox,
  Radio,
  Badge,
  Alert,
  Spinner,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Modal,
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
  Avatar,
  EmptyState,
  Tooltip,
  ToastProvider,
  useToast,
} from '@/components/ui';

function ShowcaseContent() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { showToast } = useToast();

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-slate-100 mb-2">
            FindBug UI Component Showcase
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Phase 0 Complete - All 15 Components Ready
          </p>
        </div>

        {/* Buttons */}
        <Card>
          <CardHeader>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Buttons</h2>
          </CardHeader>
          <CardBody>
            <div className="flex flex-wrap gap-3">
              <Button variant="primary">Primary</Button>
              <Button variant="danger">Danger</Button>
              <Button variant="success">Success</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="primary" size="sm">Small</Button>
              <Button variant="primary" size="lg">Large</Button>
              <Button variant="primary" isLoading>Loading</Button>
              <Button variant="primary" disabled>Disabled</Button>
            </div>
          </CardBody>
        </Card>

        {/* Badges */}
        <Card>
          <CardHeader>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Badges</h2>
          </CardHeader>
          <CardBody>
            <div className="flex flex-wrap gap-3">
              <Badge variant="critical">Critical</Badge>
              <Badge variant="high">High</Badge>
              <Badge variant="medium">Medium</Badge>
              <Badge variant="low">Low</Badge>
              <Badge variant="info">Info</Badge>
              <Badge variant="new">New</Badge>
              <Badge variant="pending">Pending</Badge>
              <Badge variant="approved">Approved</Badge>
              <Badge variant="rejected">Rejected</Badge>
              <Badge variant="resolved">Resolved</Badge>
            </div>
          </CardBody>
        </Card>

        {/* Alerts */}
        <Card>
          <CardHeader>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Alerts</h2>
          </CardHeader>
          <CardBody className="space-y-4">
            <Alert variant="success" title="Success">
              Your report has been submitted successfully!
            </Alert>
            <Alert variant="error" title="Error">
              Failed to process payment. Please try again.
            </Alert>
            <Alert variant="warning" title="Warning">
              Your KYC verification is pending review.
            </Alert>
            <Alert variant="info" title="Info">
              New features are available in the dashboard.
            </Alert>
          </CardBody>
        </Card>

        {/* Form Inputs */}
        <Card>
          <CardHeader>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Form Inputs</h2>
          </CardHeader>
          <CardBody className="space-y-4">
            <Input label="Email" type="email" placeholder="Enter your email" />
            <Input label="Password" type="password" placeholder="Enter password" />
            <Input label="With Error" error="This field is required" />
            <Input label="With Helper" helperText="We'll never share your email" />
            <Select
              label="Select Option"
              options={[
                { value: '', label: 'Choose...' },
                { value: '1', label: 'Option 1' },
                { value: '2', label: 'Option 2' },
              ]}
            />
            <Textarea label="Description" placeholder="Enter description" rows={4} />
            <div className="space-y-2">
              <Checkbox label="I agree to the terms and conditions" />
              <Checkbox label="Subscribe to newsletter" />
            </div>
            <div className="space-y-2">
              <Radio name="plan" label="Free Plan" />
              <Radio name="plan" label="Pro Plan" />
              <Radio name="plan" label="Enterprise Plan" />
            </div>
          </CardBody>
        </Card>

        {/* Tabs */}
        <Card>
          <CardHeader>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Tabs</h2>
          </CardHeader>
          <CardBody>
            <Tabs defaultValue="tab1">
              <TabsList>
                <TabsTrigger value="tab1">Overview</TabsTrigger>
                <TabsTrigger value="tab2">Details</TabsTrigger>
                <TabsTrigger value="tab3">Settings</TabsTrigger>
              </TabsList>
              <TabsContent value="tab1">
                <p className="text-slate-600 dark:text-slate-400">Overview content goes here</p>
              </TabsContent>
              <TabsContent value="tab2">
                <p className="text-slate-600 dark:text-slate-400">Details content goes here</p>
              </TabsContent>
              <TabsContent value="tab3">
                <p className="text-slate-600 dark:text-slate-400">Settings content goes here</p>
              </TabsContent>
            </Tabs>
          </CardBody>
        </Card>

        {/* Avatars & Spinners */}
        <Card>
          <CardHeader>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Avatars & Spinners</h2>
          </CardHeader>
          <CardBody>
            <div className="flex items-center gap-6">
              <div className="space-y-2">
                <p className="text-sm text-slate-600 dark:text-slate-400">Avatars</p>
                <div className="flex gap-3">
                  <Avatar fallback="NT" size="sm" />
                  <Avatar fallback="AA" size="md" />
                  <Avatar fallback="MT" size="lg" />
                  <Avatar fallback="YW" size="xl" />
                </div>
              </div>
              <div className="space-y-2">
                <p className="text-sm text-slate-600 dark:text-slate-400">Spinners</p>
                <div className="flex gap-3 items-center">
                  <Spinner size="sm" />
                  <Spinner size="md" />
                  <Spinner size="lg" />
                </div>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Interactive Components */}
        <Card>
          <CardHeader>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Interactive Components</h2>
          </CardHeader>
          <CardBody className="space-y-4">
            <div className="flex gap-3">
              <Button variant="primary" onClick={() => setIsModalOpen(true)}>
                Open Modal
              </Button>
              <Button variant="success" onClick={() => showToast('Success message!', 'success')}>
                Show Success Toast
              </Button>
              <Button variant="danger" onClick={() => showToast('Error occurred!', 'error')}>
                Show Error Toast
              </Button>
              <Tooltip content="This is a helpful tooltip">
                <Button variant="outline">Hover Me</Button>
              </Tooltip>
            </div>
          </CardBody>
        </Card>

        {/* Empty State */}
        <Card>
          <CardBody>
            <EmptyState
              icon={
                <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              }
              title="No reports yet"
              description="Get started by submitting your first vulnerability report"
              action={<Button variant="primary">Submit Report</Button>}
            />
          </CardBody>
        </Card>

        {/* Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Example Modal"
          size="md"
        >
          <div className="space-y-4">
            <p className="text-slate-600 dark:text-slate-400">
              This is an example modal dialog. It supports keyboard navigation (Escape to close),
              click outside to close, and has multiple size options.
            </p>
            <div className="flex justify-end gap-3 pt-4 border-t border-slate-200 dark:border-slate-800">
              <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                Cancel
              </Button>
              <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                Confirm
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </div>
  );
}

export default function ComponentShowcase() {
  return (
    <ToastProvider>
      <ShowcaseContent />
    </ToastProvider>
  );
}

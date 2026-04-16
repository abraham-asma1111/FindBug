import { ReactNode, ComponentType } from 'react';
import Button from './Button';

export interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode | {
    label: string;
    onClick: () => void;
    icon?: ComponentType<{ className?: string }>;
  };
}

export default function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  // Handle action as either ReactNode or object
  const renderAction = () => {
    if (!action) return null;
    
    // If action is an object with label/onClick, render as Button
    if (typeof action === 'object' && 'label' in action && 'onClick' in action) {
      const ActionIcon = action.icon;
      return (
        <Button onClick={action.onClick}>
          {ActionIcon && <ActionIcon className="h-4 w-4 mr-2" />}
          {action.label}
        </Button>
      );
    }
    
    // Otherwise render as ReactNode
    return action;
  };

  return (
    <div className="text-center py-12">
      {icon && (
        <div className="flex justify-center mb-4 text-slate-400 dark:text-slate-600">
          {icon}
        </div>
      )}
      <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">
        {title}
      </h3>
      {description && (
        <p className="text-slate-600 dark:text-slate-400 mb-4 max-w-md mx-auto">
          {description}
        </p>
      )}
      {action && (
        <div className="mt-6">
          {renderAction()}
        </div>
      )}
    </div>
  );
}

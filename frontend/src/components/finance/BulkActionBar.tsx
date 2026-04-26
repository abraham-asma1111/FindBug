'use client';

import Button from '@/components/ui/Button';

interface BulkAction {
  label: string;
  icon?: React.ReactNode;
  onClick: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
}

interface BulkActionBarProps {
  selectedCount: number;
  totalCount: number;
  actions: BulkAction[];
  onClearSelection: () => void;
}

export default function BulkActionBar({
  selectedCount,
  totalCount,
  actions,
  onClearSelection,
}: BulkActionBarProps) {
  if (selectedCount === 0) return null;

  return (
    <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50">
      <div className="bg-[#1E293B] border border-[#334155] rounded-lg shadow-2xl px-6 py-4 flex items-center gap-4">
        {/* Selection Info */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[#3B82F6] flex items-center justify-center text-white font-bold">
            {selectedCount}
          </div>
          <div>
            <p className="text-sm font-semibold text-[#F8FAFC]">
              {selectedCount} of {totalCount} selected
            </p>
            <button
              onClick={onClearSelection}
              className="text-xs text-[#94A3B8] hover:text-[#F8FAFC] transition"
            >
              Clear selection
            </button>
          </div>
        </div>

        {/* Divider */}
        <div className="w-px h-10 bg-[#334155]"></div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {actions.map((action, index) => (
            <Button
              key={index}
              onClick={action.onClick}
              disabled={action.disabled}
              variant={action.variant || 'primary'}
              size="sm"
              className={
                action.variant === 'danger'
                  ? 'bg-[#EF4444] hover:bg-[#DC2626]'
                  : action.variant === 'primary'
                  ? 'bg-[#3B82F6] hover:bg-[#2563EB]'
                  : ''
              }
            >
              {action.icon && <span className="mr-2">{action.icon}</span>}
              {action.label}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}

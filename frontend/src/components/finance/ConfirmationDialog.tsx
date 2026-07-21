'use client';

import { useState } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Textarea from '@/components/ui/Textarea';

interface ConfirmationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (notes?: string) => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'approve' | 'reject' | 'delete' | 'warning';
  requireNotes?: boolean;
  notesLabel?: string;
  notesPlaceholder?: string;
  isLoading?: boolean;
}

export default function ConfirmationDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  type = 'warning',
  requireNotes = false,
  notesLabel = 'Notes',
  notesPlaceholder = 'Add notes (optional)...',
  isLoading = false,
}: ConfirmationDialogProps) {
  const [notes, setNotes] = useState('');

  const handleConfirm = () => {
    if (requireNotes && !notes.trim()) {
      return;
    }
    onConfirm(notes.trim() || undefined);
    setNotes('');
  };

  const handleClose = () => {
    setNotes('');
    onClose();
  };

  const getIcon = () => {
    switch (type) {
      case 'approve':
        return (
          <div className="w-12 h-12 rounded-full bg-[#10B981]/20 flex items-center justify-center">
            <svg className="w-6 h-6 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        );
      case 'reject':
      case 'delete':
        return (
          <div className="w-12 h-12 rounded-full bg-[#EF4444]/20 flex items-center justify-center">
            <svg className="w-6 h-6 text-[#EF4444]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        );
      case 'warning':
      default:
        return (
          <div className="w-12 h-12 rounded-full bg-[#F59E0B]/20 flex items-center justify-center">
            <svg className="w-6 h-6 text-[#F59E0B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
        );
    }
  };

  const getConfirmButtonClass = () => {
    switch (type) {
      case 'approve':
        return 'bg-[#10B981] hover:bg-[#059669]';
      case 'reject':
      case 'delete':
        return 'bg-[#EF4444] hover:bg-[#DC2626]';
      case 'warning':
      default:
        return 'bg-[#F59E0B] hover:bg-[#D97706]';
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="">
      <div className="p-6">
        {/* Icon */}
        <div className="flex justify-center mb-4">{getIcon()}</div>

        {/* Title */}
        <h3 className="text-xl font-bold text-[#F8FAFC] text-center mb-2">{title}</h3>

        {/* Message */}
        <p className="text-sm text-[#94A3B8] text-center mb-6">{message}</p>

        {/* Notes Input */}
        {(requireNotes || type === 'reject') && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-[#F8FAFC] mb-2">
              {notesLabel}
              {requireNotes && <span className="text-[#EF4444] ml-1">*</span>}
            </label>
            <Textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder={notesPlaceholder}
              rows={4}
              className="w-full"
            />
            {requireNotes && !notes.trim() && (
              <p className="text-xs text-[#EF4444] mt-1">Notes are required</p>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={isLoading}
            className="flex-1"
          >
            {cancelText}
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={isLoading || (requireNotes && !notes.trim())}
            className={`flex-1 ${getConfirmButtonClass()}`}
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Processing...
              </span>
            ) : (
              confirmText
            )}
          </Button>
        </div>
      </div>
    </Modal>
  );
}

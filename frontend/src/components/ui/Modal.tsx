'use client';

import { ReactNode, useEffect } from 'react';
import { createPortal } from 'react-dom';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showCloseButton?: boolean;
}

export default function Modal({ 
  isOpen, 
  onClose, 
  title,
  children,
  size = 'md',
  showCloseButton = true,
}: ModalProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);
  
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);
  
  if (!isOpen) return null;
  
  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  };
  
  const modalContent = (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Overlay */}
      <div 
        className="fixed inset-0 bg-black/50 dark:bg-black/70 transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div 
        className={`
          relative w-full ${sizes[size]}
          bg-white
          border border-[#e6ddd4]
          rounded-2xl shadow-2xl
          max-h-[90vh] overflow-y-auto
        `}
      >
        {/* Header */}
        {(title || showCloseButton) && (
          <div className="flex items-center justify-between px-6 py-4 border-b border-[#e6ddd4]">
            {title && (
              <h2 className="text-xl font-bold text-[#2d2a26]">
                {title}
              </h2>
            )}
            {showCloseButton && (
              <button
                onClick={onClose}
                className="ml-auto text-[#8b8177] hover:text-[#2d2a26] transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        )}
        
        {/* Body */}
        <div className="px-6 py-4">
          {children}
        </div>
      </div>
    </div>
  );
  
  return createPortal(modalContent, document.body);
}

export function ModalFooter({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div className={`flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-200 dark:border-slate-800 ${className}`}>
      {children}
    </div>
  );
}

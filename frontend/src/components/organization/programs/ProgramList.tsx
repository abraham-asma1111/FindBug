'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { formatCurrency, formatDateTime } from '@/lib/portal';
import api from '@/lib/api';

interface Program {
  id: string;
  name: string;
  description?: string;
  type: string;
  status: string;
  visibility: string;
  budget?: number;
  created_at: string;
  updated_at?: string;
}

interface ProgramListProps {
  programs: Program[];
  onUpdate: () => void;
  isArchived?: boolean;
}

export default function ProgramList({ programs, onUpdate, isArchived = false }: ProgramListProps) {
  const [openDropdownId, setOpenDropdownId] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setOpenDropdownId(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleArchive = async (programId: string) => {
    if (!confirm('Are you sure you want to archive this program? You can restore it later.')) {
      return;
    }

    try {
      await api.post(`/programs/${programId}/archive`);
      alert('Program archived successfully');
      onUpdate();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to archive program');
    }
  };

  const handleRestore = async (programId: string) => {
    try {
      await api.post(`/programs/${programId}/restore`);
      alert('Program restored successfully');
      onUpdate();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to restore program');
    }
  };

  const handleDelete = async (programId: string) => {
    if (!confirm('Are you sure you want to permanently delete this program? This action cannot be undone.')) {
      return;
    }

    try {
      await api.post(`/programs/${programId}/delete`);
      alert('Program deleted successfully');
      onUpdate();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to delete program');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'public':
        return 'bg-[#e6f7ed] text-[#0d7a3d]';
      case 'draft':
        return 'bg-[#faf1e1] text-[#9a6412]';
      case 'paused':
        return 'bg-[#fff4e6] text-[#b54708]';
      case 'closed':
        return 'bg-[#f3ede6] text-[#5f5851]';
      default:
        return 'bg-[#f3ede6] text-[#5f5851]';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'bounty':
        return 'bg-[#edf5fb] text-[#2d78a8]';
      case 'vdp':
        return 'bg-[#f3e8ff] text-[#6b21a8]';
      default:
        return 'bg-[#f3ede6] text-[#5f5851]';
    }
  };

  return (
    <>
      <div className="space-y-6">
        {programs.map((program) => (
          <div 
            key={program.id} 
            className="rounded-2xl border border-[#e6ddd4] dark:border-slate-700 bg-white dark:bg-slate-800 p-6 hover:border-[#d4c5b3] dark:hover:border-slate-600 transition-all hover:shadow-sm"
          >
            <div className="flex items-start justify-between gap-6">
              <div className="flex-1 min-w-0">
                {/* Badges */}
                <div className="flex flex-wrap items-center gap-3 mb-4">
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getTypeColor(program.type)}`}>
                    {program.type.toUpperCase()}
                  </span>
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getStatusColor(program.status)}`}>
                    {program.status.charAt(0).toUpperCase() + program.status.slice(1)}
                  </span>
                  {program.visibility && (
                    <span className="rounded-full bg-[#f3ede6] dark:bg-slate-700 px-3 py-1 text-xs font-semibold text-[#5f5851] dark:text-slate-300">
                      {program.visibility}
                    </span>
                  )}
                </div>

                {/* Program Name */}
                <h3 className="text-xl font-bold text-[#2d2a26] dark:text-slate-100 mb-3">
                  {program.name}
                </h3>

                {/* Description */}
                {program.description && (
                  <p className="text-sm text-[#6d6760] dark:text-slate-300 leading-relaxed mb-5 line-clamp-2">
                    {program.description}
                  </p>
                )}

                {/* Metadata */}
                <div className="flex flex-wrap items-center gap-8 text-sm pt-4 border-t border-[#e6ddd4] dark:border-slate-700">
                  {program.budget !== undefined && program.budget !== null && (
                    <div>
                      <p className="text-xs text-[#8b8177] dark:text-slate-400 mb-1">Budget</p>
                      <p className="font-semibold text-[#2d2a26] dark:text-slate-100">
                        {formatCurrency(program.budget)}
                      </p>
                    </div>
                  )}
                  <div>
                    <p className="text-xs text-[#8b8177] dark:text-slate-400 mb-1">Created</p>
                    <p className="font-semibold text-[#2d2a26] dark:text-slate-100">
                      {formatDateTime(program.created_at)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex-shrink-0 flex items-center gap-2">
                <Link
                  href={`/organization/programs/${program.id}`}
                  className="rounded-full border-2 border-gray-300 dark:border-slate-500 bg-white dark:bg-slate-700 px-5 py-2.5 text-sm font-semibold text-gray-900 dark:text-slate-100 transition hover:border-gray-400 dark:hover:border-slate-400 hover:bg-gray-50 dark:hover:bg-slate-600 shadow-sm"
                >
                  View Details
                </Link>

                {/* Dropdown Menu */}
                <div className="relative" ref={openDropdownId === program.id ? dropdownRef : null}>
                  <button
                    onClick={() => setOpenDropdownId(openDropdownId === program.id ? null : program.id)}
                    className="rounded-full border-2 border-gray-300 dark:border-slate-500 bg-white dark:bg-slate-700 p-2.5 text-gray-900 dark:text-slate-100 transition hover:border-gray-400 dark:hover:border-slate-400 hover:bg-gray-50 dark:hover:bg-slate-600 shadow-sm"
                  >
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" />
                    </svg>
                  </button>

                  {openDropdownId === program.id && (
                    <div className="absolute right-0 mt-2 w-48 rounded-xl border border-[#e6ddd4] dark:border-slate-700 bg-white dark:bg-slate-800 shadow-lg z-10">
                      {isArchived ? (
                        <>
                          {/* Archived program actions */}
                          <button
                            onClick={() => {
                              setOpenDropdownId(null);
                              handleRestore(program.id);
                            }}
                            className="flex w-full items-center gap-3 px-4 py-3 text-sm text-[#2d2a26] dark:text-slate-100 transition hover:bg-[#faf6f1] dark:hover:bg-slate-700"
                          >
                            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                            Restore
                          </button>
                          <button
                            onClick={() => {
                              setOpenDropdownId(null);
                              handleDelete(program.id);
                            }}
                            className="flex w-full items-center gap-3 px-4 py-3 text-sm text-[#b42318] dark:text-red-400 transition hover:bg-[#fff2f1] dark:hover:bg-red-950"
                          >
                            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
            Delete Permanently
                          </button>
                        </>
                      ) : (
                        <>
                          {/* Active/Draft program actions */}
                          {program.status === 'draft' && (
                            <Link
                              href={`/organization/programs/${program.id}`}
                              onClick={() => setOpenDropdownId(null)}
                              className="flex w-full items-center gap-3 px-4 py-3 text-sm text-[#2d2a26] dark:text-slate-100 transition hover:bg-[#faf6f1] dark:hover:bg-slate-700"
                            >
                              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                              </svg>
                              Edit
                            </Link>
                          )}
                          <button
                            onClick={() => {
                              setOpenDropdownId(null);
                              handleArchive(program.id);
                            }}
                            className="flex w-full items-center gap-3 px-4 py-3 text-sm text-[#2d2a26] dark:text-slate-100 transition hover:bg-[#faf6f1] dark:hover:bg-slate-700"
                          >
                            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                            </svg>
                            Archive
                          </button>
                          {program.status === 'draft' && (
                            <button
                              onClick={() => {
                                setOpenDropdownId(null);
                                handleDelete(program.id);
                              }}
                              className="flex w-full items-center gap-3 px-4 py-3 text-sm text-[#b42318] dark:text-red-400 transition hover:bg-[#fff2f1] dark:hover:bg-red-950"
                            >
                              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                              Delete
                            </button>
                          )}
                        </>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

'use client';

import { useState } from 'react';
import Link from 'next/link';

interface Column {
  key: string;
  label: string;
  sortable?: boolean;
  render?: (value: any, row: any) => React.ReactNode;
}

interface TransactionTableProps {
  data: any[];
  columns: Column[];
  onRowClick?: (row: any) => void;
  selectable?: boolean;
  onSelectionChange?: (selectedIds: string[]) => void;
  linkPrefix?: string;
}

export default function TransactionTable({
  data,
  columns,
  onRowClick,
  selectable = false,
  onSelectionChange,
  linkPrefix,
}: TransactionTableProps) {
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const handleSort = (columnKey: string) => {
    if (sortColumn === columnKey) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      const allIds = new Set(data.map((row) => row.id));
      setSelectedIds(allIds);
      onSelectionChange?.(Array.from(allIds));
    } else {
      setSelectedIds(new Set());
      onSelectionChange?.([]);
    }
  };

  const handleSelectRow = (id: string, checked: boolean) => {
    const newSelected = new Set(selectedIds);
    if (checked) {
      newSelected.add(id);
    } else {
      newSelected.delete(id);
    }
    setSelectedIds(newSelected);
    onSelectionChange?.(Array.from(newSelected));
  };

  const sortedData = [...data].sort((a, b) => {
    if (!sortColumn) return 0;
    const aVal = a[sortColumn];
    const bVal = b[sortColumn];
    if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  const allSelected = data.length > 0 && selectedIds.size === data.length;
  const someSelected = selectedIds.size > 0 && selectedIds.size < data.length;

  return (
    <div className="bg-[#1E293B] rounded-lg border border-[#334155] overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-[#0F172A] border-b border-[#334155]">
            <tr>
              {selectable && (
                <th className="px-4 py-3 text-left w-12">
                  <input
                    type="checkbox"
                    checked={allSelected}
                    ref={(input) => {
                      if (input) input.indeterminate = someSelected;
                    }}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="w-4 h-4 rounded border-[#334155] bg-[#1E293B] text-[#3B82F6] focus:ring-[#3B82F6] focus:ring-offset-0"
                  />
                </th>
              )}
              {columns.map((column) => (
                <th
                  key={column.key}
                  className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-[#94A3B8]"
                >
                  {column.sortable ? (
                    <button
                      onClick={() => handleSort(column.key)}
                      className="flex items-center gap-1 hover:text-[#F8FAFC] transition"
                    >
                      {column.label}
                      {sortColumn === column.key && (
                        <svg
                          className={`w-4 h-4 transition-transform ${
                            sortDirection === 'desc' ? 'rotate-180' : ''
                          }`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 15l7-7 7 7"
                          />
                        </svg>
                      )}
                    </button>
                  ) : (
                    column.label
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#334155]">
            {sortedData.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length + (selectable ? 1 : 0)}
                  className="px-4 py-8 text-center text-[#94A3B8]"
                >
                  No data found
                </td>
              </tr>
            ) : (
              sortedData.map((row) => {
                const isSelected = selectedIds.has(row.id);
                const RowWrapper = linkPrefix
                  ? ({ children }: { children: React.ReactNode }) => (
                      <Link href={`${linkPrefix}/${row.id}`}>{children}</Link>
                    )
                  : ({ children }: { children: React.ReactNode }) => <>{children}</>;

                return (
                  <RowWrapper key={row.id}>
                    <tr
                      className={`hover:bg-[#334155] transition cursor-pointer ${
                        isSelected ? 'bg-[#1E40AF]/20' : ''
                      }`}
                      onClick={() => onRowClick?.(row)}
                    >
                      {selectable && (
                        <td className="px-4 py-3">
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={(e) => {
                              e.stopPropagation();
                              handleSelectRow(row.id, e.target.checked);
                            }}
                            onClick={(e) => e.stopPropagation()}
                            className="w-4 h-4 rounded border-[#334155] bg-[#1E293B] text-[#3B82F6] focus:ring-[#3B82F6] focus:ring-offset-0"
                          />
                        </td>
                      )}
                      {columns.map((column) => (
                        <td key={column.key} className="px-4 py-3 text-sm text-[#F8FAFC]">
                          {column.render
                            ? column.render(row[column.key], row)
                            : row[column.key]}
                        </td>
                      ))}
                    </tr>
                  </RowWrapper>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

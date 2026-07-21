'use client';

import { CheckCircle, Circle, Target } from 'lucide-react';

interface AssetCoverageProps {
  coverage: {
    in_scope_assets: string[];
    tested_assets: string[];
    tested: number;
    total: number;
    percentage: number;
  };
}

export default function PTaaSAssetCoverage({ coverage }: AssetCoverageProps) {
  const { in_scope_assets, tested_assets, percentage } = coverage;

  return (
    <div className="rounded-xl border border-[#e6ddd4] bg-white p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-[#2d2a26]">Asset Coverage</h3>
        <div className="flex items-center gap-2">
          <Target className="h-5 w-5 text-green-600" />
          <span className="text-2xl font-bold text-green-600">{percentage.toFixed(0)}%</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="h-3 bg-[#e6ddd4] rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-green-500 to-green-600 transition-all duration-500"
            style={{ width: `${percentage}%` }}
          />
        </div>
        <div className="flex justify-between mt-2 text-xs text-[#8b8177]">
          <span>{coverage.tested} tested</span>
          <span>{coverage.total} total</span>
        </div>
      </div>

      {/* Asset List */}
      {in_scope_assets.length > 0 ? (
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {in_scope_assets.map((asset, index) => {
            const isTested = tested_assets.includes(asset);
            return (
              <div
                key={index}
                className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
                  isTested ? 'bg-green-50' : 'bg-[#faf6f1]'
                }`}
              >
                {isTested ? (
                  <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
                ) : (
                  <Circle className="h-5 w-5 text-[#8b8177] flex-shrink-0" />
                )}
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium truncate ${
                    isTested ? 'text-green-900' : 'text-[#2d2a26]'
                  }`}>
                    {asset}
                  </p>
                  <p className={`text-xs ${
                    isTested ? 'text-green-700' : 'text-[#8b8177]'
                  }`}>
                    {isTested ? 'Tested' : 'Pending'}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-8">
          <Target className="mx-auto h-10 w-10 text-[#8b8177] mb-2" />
          <p className="text-sm text-[#6d6760]">No assets defined in scope</p>
        </div>
      )}
    </div>
  );
}

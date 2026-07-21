'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import api from '@/lib/api';
import { labsHubUrl } from '@/lib/simulation-lab';

export default function SimulationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [isStarting, setIsStarting] = useState(false);
  const [startError, setStartError] = useState<string | null>(null);
  const [reportTitle, setReportTitle] = useState('');
  const [reportSteps, setReportSteps] = useState('');
  const [reportPoc, setReportPoc] = useState('');
  const [reportImpact, setReportImpact] = useState('');
  const [reportSeverity, setReportSeverity] = useState('low');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<any>(null);
  const [unlockedHints, setUnlockedHints] = useState<Record<number, string>>({});
  const [xpBalance, setXpBalance] = useState(0);
  const [writeupTitle, setWriteupTitle] = useState('');
  const [writeupContent, setWriteupContent] = useState('');
  const [communityList, setCommunityList] = useState<any[]>([]);
  const [urlCopied, setUrlCopied] = useState(false);

  useEffect(() => { if (params.id) fetchDetails(); }, [params.id]);

  const fetchDetails = async () => {
    try {
      const res = await api.get(`/simulation/challenges/${params.id}`);
      setData(res.data);
      setCommunityList(res.data.community_solutions || []);
      const unlocked: Record<number, string> = {};
      (res.data.challenge?.hints_preview || []).forEach((h: any) => {
        if (h.unlocked && h.preview) unlocked[h.index] = h.preview;
      });
      setUnlockedHints(unlocked);
      setXpBalance(res.data.user_xp?.balance ?? 0);
    } catch {
      router.push('/researcher/simulation');
    } finally {
      setLoading(false);
    }
  };

  const fetchCommunity = async () => {
    try {
      const res = await api.get(`/simulation/challenges/${params.id}/solutions`);
      setCommunityList(res.data.solutions || []);
    } catch (e) {
      console.error(e);
    }
  };

  const openLabHub = async () => {
    setIsStarting(true);
    setStartError(null);
    try {
      await api.post(`/simulation/challenges/${params.id}/start`);
      router.push(labsHubUrl(params.id as string));
    } catch (e: any) {
      const d = e.response?.data?.detail;
      if (typeof d === 'object' && d !== null) {
        const steps = Array.isArray(d.fix_steps) ? d.fix_steps.join('\n') : '';
        setStartError(`${d.error || 'Lab failed'}\n\n${steps}`);
      } else {
        setStartError(typeof d === 'string' ? d : 'Failed to open lab. Is Docker running?');
      }
    } finally {
      setIsStarting(false);
    }
  };

  const copyLabLink = async () => {
    const url = labsHubUrl(params.id as string);
    try {
      await navigator.clipboard.writeText(url);
      setUrlCopied(true);
      setTimeout(() => setUrlCopied(false), 2000);
    } catch {
      alert('Copy failed — select the URL below and copy manually.');
    }
  };

  const unlockHint = async (index: number) => {
    try {
      const res = await api.post(`/simulation/challenges/${params.id}/hints/${index}/unlock`);
      setUnlockedHints((prev) => ({ ...prev, [index]: res.data.hint }));
      if (typeof res.data.xp_balance === 'number') setXpBalance(res.data.xp_balance);
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Could not unlock hint');
    }
  };

  const submitWriteup = async () => {
    try {
      await api.post(`/simulation/challenges/${params.id}/solutions`, {
        title: writeupTitle,
        content: writeupContent,
      });
      setWriteupTitle('');
      setWriteupContent('');
      alert('Writeup submitted for admin approval');
      fetchCommunity();
    } catch {
      alert('Failed to post writeup');
    }
  };

  const submitReport = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await api.post(`/simulation/challenges/${params.id}/submit`, {
        title: reportTitle,
        steps_to_reproduce: reportSteps,
        poc: reportPoc,
        impact: reportImpact,
        severity: reportSeverity,
      });
      setSubmitResult(res.data);
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Failed to submit report');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading || !data) {
    return (
      <div className="flex justify-center py-32">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-emerald-500" />
      </div>
    );
  }

  const { challenge, user_progress } = data;
  const challengeId = params.id as string;
  const labAccessUrl = labsHubUrl(challengeId);
  type HintRow = {
    index: number;
    tier: 'free' | 'paid';
    title: string;
    xp_cost: number;
    unlocked: boolean;
    preview?: string | null;
  };
  const hintsPreview: HintRow[] = challenge.hints_preview || [];
  const freeHints = hintsPreview.filter((h) => h.tier === 'free');
  const paidHints = hintsPreview.filter((h) => h.tier === 'paid');

  const renderHintCard = (h: HintRow) => {
    const revealed = unlockedHints[h.index] || h.preview;
    const isPaid = h.tier === 'paid';
    const canAfford = !isPaid || xpBalance >= h.xp_cost;
    return (
      <div key={h.index} className="bg-[#111] border border-gray-800 rounded-lg p-4">
        <div className="flex justify-between items-start gap-3 mb-2">
          <div>
            <h4 className="text-white font-medium text-sm">{h.title}</h4>
            {isPaid && !revealed && (
              <p className="text-amber-400/90 text-[10px] mt-0.5">Costs {h.xp_cost} XP</p>
            )}
          </div>
          {!revealed && (
            <button
              type="button"
              onClick={() => unlockHint(h.index)}
              disabled={isPaid && !canAfford}
              className={`text-xs px-3 py-1 rounded shrink-0 border ${
                isPaid
                  ? canAfford
                    ? 'bg-amber-600/20 text-amber-300 border-amber-500/40 hover:bg-amber-600/30'
                    : 'bg-gray-800 text-gray-600 border-gray-700 cursor-not-allowed'
                  : 'bg-emerald-600/20 text-emerald-400 border-emerald-500/30 hover:bg-emerald-600/30'
              }`}
            >
              {isPaid ? `Unlock (${h.xp_cost} XP)` : 'Reveal free'}
            </button>
          )}
        </div>
        {revealed ? (
          <p className="text-gray-400 font-mono text-xs bg-[#0d0d0d] p-3 rounded border border-gray-800">{revealed}</p>
        ) : (
          <p className="text-gray-600 text-xs italic">
            {isPaid ? 'Locked — spend XP to unlock' : 'Locked — free for all researchers'}
          </p>
        )}
      </div>
    );
  };

  const tabs = [
    { id: 'overview', label: 'Theory' },
    { id: 'lab', label: 'Lab' },
    { id: 'hints', label: 'Hints' },
    { id: 'community', label: 'Community' },
    { id: 'walkthrough', label: 'Video' },
    { id: 'submit', label: 'Report' },
  ];

  return (
    <div className="animate-in fade-in duration-500">
      <div className="mb-6">
        <Link href="/researcher/simulation" className="text-emerald-500 hover:text-emerald-400 text-sm">← Back</Link>
        <h1 className="text-2xl font-bold text-white mt-3">{challenge.name}</h1>
        <div className="flex items-center gap-3 mt-2 text-xs flex-wrap">
          <span className="px-2 py-0.5 bg-gray-800 text-gray-300 rounded uppercase tracking-wider border border-gray-700 font-medium">{challenge.difficulty_level}</span>
          <span className="text-emerald-400 font-bold">+{challenge.points} XP</span>
          {user_progress.status === 'completed' && (
            <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded font-medium">SOLVED</span>
          )}
        </div>
      </div>

      <div className="flex overflow-x-auto border-b border-gray-800 mb-6 gap-1">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => {
              if (t.id === 'lab') {
                router.push(labsHubUrl(challengeId));
                return;
              }
              setActiveTab(t.id);
              if (t.id === 'community') fetchCommunity();
            }}
            className={`whitespace-nowrap px-4 py-2.5 text-xs font-medium border-b-2 rounded-t-md transition-colors ${activeTab === t.id ? 'border-emerald-500 text-emerald-400 bg-emerald-500/5' : 'border-transparent text-gray-500 hover:text-gray-300'}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="bg-[#161616] border border-gray-800 rounded-xl p-6 min-h-[400px]">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <p className="text-gray-300 leading-relaxed text-base">{challenge.description}</p>
            <div className="bg-[#111] border border-gray-800 rounded-lg p-6 space-y-4">
              <p className="text-[10px] uppercase tracking-widest text-emerald-500 font-semibold">Theory &amp; lab walkthrough</p>
              <div className="text-gray-300 text-sm leading-relaxed space-y-3">
                {(challenge.documentation || '').split('\n').map((line: string, i: number) => {
                  if (line.startsWith('## ')) {
                    return <h3 key={i} className="text-white font-semibold text-base mt-4 first:mt-0">{line.replace(/^##\s*/, '')}</h3>;
                  }
                  if (line.startsWith('### ')) {
                    return <h4 key={i} className="text-emerald-400/90 font-medium text-sm mt-2">{line.replace(/^###\s*/, '')}</h4>;
                  }
                  if (line.startsWith('```')) return null;
                  if (line.trim() === '') return <br key={i} />;
                  if (line.startsWith('- ')) {
                    return <li key={i} className="ml-4 list-disc text-gray-400">{line.slice(2)}</li>;
                  }
                  return <p key={i} className="text-gray-400">{line}</p>;
                })}
              </div>
            </div>
            {challenge.external_resources?.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-white mb-3 uppercase tracking-wider">Resources</h3>
                <ul className="space-y-2">
                  {challenge.external_resources.map((r: any, i: number) => (
                    <li key={i}>
                      <a href={r.url} target="_blank" rel="noopener noreferrer" className="text-emerald-400 hover:underline text-sm">{r.title} →</a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {activeTab === 'lab' && (
          <div className="py-6 max-w-xl mx-auto text-center">
            <h2 className="text-xl font-semibold text-white mb-2">Academy Lab</h2>
            <p className="text-gray-500 text-sm mb-6">
              You can access your lab at this link. All lab modules are in one place — your current
              challenge is selected automatically.
            </p>

            <div className="p-4 bg-emerald-950/20 border border-emerald-500/30 rounded-xl text-left mb-6">
              <p className="text-xs text-emerald-400 uppercase tracking-wider mb-2">Your lab link</p>
              <p className="text-emerald-300 font-mono text-sm break-all">{labAccessUrl}</p>
            </div>

            {!data.docker_available && (
              <p className="text-amber-500/90 text-xs mb-4">
                Docker offline — run: docker compose -f simulation/docker-compose.yml up -d
              </p>
            )}
            {startError && (
              <pre className="text-left text-xs text-red-400 bg-red-950/30 border border-red-900/50 rounded-lg p-4 mb-4 whitespace-pre-wrap">{startError}</pre>
            )}

            <div className="flex flex-col sm:flex-row gap-3">
              <button
                type="button"
                onClick={openLabHub}
                disabled={isStarting}
                className="flex-1 py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-xl disabled:opacity-50"
              >
                {isStarting ? 'Opening...' : 'Open lab environment'}
              </button>
              <Link
                href={labAccessUrl}
                className="flex-1 py-3.5 bg-[#1a1a1a] text-gray-200 font-medium rounded-xl border border-gray-700 text-sm flex items-center justify-center hover:border-gray-500"
              >
                Go without restart
              </Link>
            </div>
            <button
              type="button"
              onClick={copyLabLink}
              className="mt-3 text-xs text-gray-500 hover:text-gray-300"
            >
              {urlCopied ? 'Link copied!' : 'Copy lab link'}
            </button>
          </div>
        )}

        {activeTab === 'hints' && (
          <div className="max-w-xl mx-auto space-y-6 py-4">
            <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-[#111] border border-gray-800 rounded-lg">
              <p className="text-gray-400 text-sm">
                <span className="text-emerald-400 font-medium">Free hints</span> — no XP cost.
                <span className="text-gray-600 mx-2">|</span>
                <span className="text-amber-400 font-medium">Paid hints</span> — deducted from your XP balance.
              </p>
              <p className="text-xs text-gray-500">
                XP balance: <span className="text-emerald-400 font-bold">{xpBalance}</span>
              </p>
            </div>

            {hintsPreview.length === 0 ? (
              <p className="text-gray-500 text-center">No hints for this challenge.</p>
            ) : (
              <>
                {freeHints.length > 0 && (
                  <section className="space-y-3">
                    <h3 className="text-sm font-semibold text-emerald-400 uppercase tracking-wider">
                      Free hints ({freeHints.length})
                    </h3>
                    {freeHints.map(renderHintCard)}
                  </section>
                )}
                {paidHints.length > 0 && (
                  <section className="space-y-3">
                    <h3 className="text-sm font-semibold text-amber-400 uppercase tracking-wider">
                      Paid hints ({paidHints.length})
                    </h3>
                    {paidHints.map(renderHintCard)}
                  </section>
                )}
              </>
            )}
          </div>
        )}

        {activeTab === 'community' && (
          <div className="space-y-8 max-w-2xl mx-auto">
            <div>
              <h3 className="text-lg font-medium text-white mb-4">Community Writeups</h3>
              {communityList.length === 0 ? (
                <p className="text-gray-500 text-sm">No approved writeups yet. Be the first!</p>
              ) : (
                <ul className="space-y-3">
                  {communityList.map((s: any) => (
                    <li key={s.id} className="bg-[#111] border border-gray-800 rounded-lg p-4">
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-white font-medium">{s.title}</span>
                        <span className="text-gray-500">{s.author}</span>
                      </div>
                      {s.is_approved && s.content ? (
                        <p className="text-gray-400 text-xs whitespace-pre-wrap">{s.content}</p>
                      ) : (
                        <p className="text-amber-500/80 text-xs">Pending moderation</p>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="border-t border-gray-800 pt-6">
              <h4 className="text-white font-medium mb-3">Post your writeup</h4>
              <input value={writeupTitle} onChange={(e) => setWriteupTitle(e.target.value)} placeholder="Title" className="w-full mb-3 bg-[#111] border border-gray-700 rounded-lg px-4 py-2 text-white text-sm" />
              <textarea value={writeupContent} onChange={(e) => setWriteupContent(e.target.value)} rows={4} placeholder="Methodology, payloads..." className="w-full mb-3 bg-[#111] border border-gray-700 rounded-lg px-4 py-2 text-white text-sm font-mono" />
              <button type="button" onClick={submitWriteup} className="px-5 py-2 border border-gray-700 text-gray-300 rounded-lg hover:bg-gray-800 text-sm">Submit for review</button>
            </div>
          </div>
        )}

        {activeTab === 'walkthrough' && challenge.tutorial_video_url && (
          <div className="py-4 flex flex-col items-center">
            <h3 className="text-lg font-semibold text-white mb-4">Official Walkthrough</h3>
            <div className="w-full max-w-3xl aspect-video rounded-xl overflow-hidden border border-gray-700 shadow-2xl">
              <iframe src={challenge.tutorial_video_url} className="w-full h-full" allowFullScreen title="Walkthrough" />
            </div>
          </div>
        )}

        {activeTab === 'submit' && (
          <div className="max-w-2xl mx-auto">
            {submitResult ? (
              <div className="text-center py-12 space-y-4">
                <div className="w-16 h-16 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center mx-auto border border-emerald-500/30 text-3xl">✓</div>
                <h3 className="text-xl font-semibold text-white">Submitted</h3>
                <p className="text-gray-400 text-sm">{submitResult.message}</p>
                {submitResult.automated_feedback && (
                  <div className="text-left bg-[#111] border border-gray-800 rounded-lg p-4 mt-4">
                    <p className="text-xs text-gray-500 uppercase mb-2">Automated preview (score {submitResult.automated_score}%)</p>
                    <pre className="text-gray-400 text-xs whitespace-pre-wrap">{submitResult.automated_feedback}</pre>
                  </div>
                )}
                <Link href="/researcher/simulation/my-progress" className="inline-block px-5 py-2.5 bg-emerald-600 text-white rounded-lg text-sm mt-4">My Progress</Link>
              </div>
            ) : (
              <form onSubmit={submitReport} className="space-y-5">
                <h2 className="text-lg font-semibold text-white mb-4">Submit Exploit Report</h2>
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1.5 uppercase">Title</label>
                  <input type="text" required value={reportTitle} onChange={(e) => setReportTitle(e.target.value)} className="w-full bg-[#111] border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm focus:border-emerald-500 focus:outline-none" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1.5 uppercase">Severity</label>
                  <select value={reportSeverity} onChange={(e) => setReportSeverity(e.target.value)} className="w-full bg-[#111] border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm">
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1.5 uppercase">Steps to Reproduce</label>
                  <textarea required value={reportSteps} onChange={(e) => setReportSteps(e.target.value)} rows={5} className="w-full bg-[#111] border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm font-mono focus:border-emerald-500 focus:outline-none" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1.5 uppercase">Impact</label>
                  <textarea value={reportImpact} onChange={(e) => setReportImpact(e.target.value)} rows={3} className="w-full bg-[#111] border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm focus:border-emerald-500 focus:outline-none" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1.5 uppercase">Proof of Concept</label>
                  <textarea required value={reportPoc} onChange={(e) => setReportPoc(e.target.value)} rows={3} className="w-full bg-[#111] border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm font-mono focus:border-emerald-500 focus:outline-none" />
                </div>
                <button type="submit" disabled={isSubmitting} className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-xl disabled:opacity-50 text-sm">
                  {isSubmitting ? 'Submitting...' : 'Submit Report'}
                </button>
              </form>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

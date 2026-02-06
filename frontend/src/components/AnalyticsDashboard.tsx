import { useEffect, useMemo, useRef, useState } from 'react';
import type { FC } from 'react';
import * as echarts from 'echarts';

type DashboardSong = {
  track_id?: string;
  track_name?: string;
  artist_name?: string;
  tempo?: number | string;
  valence?: number | string;
  energy?: number | string;
};

type Props = {
  songs?: DashboardSong[];
};

function statAvg(arr: number[]) {
  const nums = arr.filter((x) => Number.isFinite(x));
  if (!nums.length) return null;
  return nums.reduce((a, b) => a + b, 0) / nums.length;
}

function round2(x: number | null) {
  return Number.isFinite(x as number) ? Math.round((x as number) * 100) / 100 : null;
}

function safeNum(x: unknown): number | null {
  const n = typeof x === 'number' ? x : Number(x);
  return Number.isFinite(n) ? n : null;
}

function quantile(sorted: number[], q: number) {
  if (!sorted.length) return null;
  const pos = (sorted.length - 1) * q;
  const base = Math.floor(pos);
  const rest = pos - base;
  if (sorted[base + 1] !== undefined) {
    return sorted[base] + rest * (sorted[base + 1] - sorted[base]);
  }
  return sorted[base];
}

function iqrBounds(values: number[]) {
  if (values.length < 4) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const q1 = quantile(sorted, 0.25);
  const q3 = quantile(sorted, 0.75);
  if (q1 === null || q3 === null) return null;
  const iqr = q3 - q1;
  return { low: q1 - 1.5 * iqr, high: q3 + 1.5 * iqr };
}

function buildTempoBins(tempos: number[], binSize = 10) {
  const bins = new Map<number, number>();
  for (const t of tempos) {
    const start = Math.floor(t / binSize) * binSize;
    bins.set(start, (bins.get(start) || 0) + 1);
  }
  const starts = Array.from(bins.keys()).sort((a, b) => a - b);
  return {
    labels: starts.map((s) => `${s}-${s + binSize}`),
    counts: starts.map((s) => bins.get(s) || 0),
  };
}

const AnalyticsDashboard: FC<Props> = ({ songs = [] }) => {
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<
    'tempo' | 'energy' | 'valence' | 'track_name' | 'artist_name' | ''
  >('');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [outliersOnly, setOutliersOnly] = useState(false);
  const [tempoFilter, setTempoFilter] = useState<'slow' | 'mid' | 'fast' | ''>('');
  const [moodFilter, setMoodFilter] = useState<'negative' | 'neutral' | 'positive' | ''>('');
  const [lastUpdated, setLastUpdated] = useState<number | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const prevStatsRef = useRef<{
    count: number;
    uniqueArtists: number;
    avgTempo: number | null;
    avgEnergy: number | null;
    avgValence: number | null;
  } | null>(null);

  // Normalize once to avoid NaN/strings breaking charts
  const normalized = useMemo(() => {
    return (songs || []).map((s) => ({
      track_id: s.track_id,
      track_name: s.track_name ?? '',
      artist_name: s.artist_name ?? '',
      tempo: safeNum(s.tempo),
      valence: safeNum(s.valence),
      energy: safeNum(s.energy),
    }));
  }, [songs]);

  // KPI stats
  const stats = useMemo(() => {
    const tempos = normalized.map((s) => s.tempo).filter((x): x is number => x !== null);
    const energies = normalized.map((s) => s.energy).filter((x): x is number => x !== null);
    const valences = normalized.map((s) => s.valence).filter((x): x is number => x !== null);

    const uniqueArtists = new Set(
      normalized.map((s) => (s.artist_name ?? '').trim()).filter(Boolean)
    ).size;

    return {
      count: normalized.length,
      uniqueArtists,
      avgTempo: round2(statAvg(tempos)),
      avgEnergy: round2(statAvg(energies)),
      avgValence: round2(statAvg(valences)),
    };
  }, [normalized]);

  const deltas = useMemo(() => {
    const prev = prevStatsRef.current;
    if (!prev) return null;
    return {
      count: stats.count - prev.count,
      uniqueArtists: stats.uniqueArtists - prev.uniqueArtists,
      avgTempo:
        stats.avgTempo !== null && prev.avgTempo !== null
          ? round2(stats.avgTempo - prev.avgTempo)
          : null,
      avgEnergy:
        stats.avgEnergy !== null && prev.avgEnergy !== null
          ? round2(stats.avgEnergy - prev.avgEnergy)
          : null,
      avgValence:
        stats.avgValence !== null && prev.avgValence !== null
          ? round2(stats.avgValence - prev.avgValence)
          : null,
    };
  }, [stats]);

  const tableRows = useMemo(() => {
    let list = normalized;
    const query = search.trim().toLowerCase();
    if (query) {
      list = list.filter((s) => {
        const track = (s.track_name ?? '').toLowerCase();
        const artist = (s.artist_name ?? '').toLowerCase();
        return track.includes(query) || artist.includes(query);
      });
    }

    if (tempoFilter) {
      list = list.filter((s) => {
        if (s.tempo === null) return false;
        if (tempoFilter == 'slow') return s.tempo < 90;
        if (tempoFilter == 'mid') return s.tempo >= 90 && s.tempo < 120;
        return s.tempo >= 120;
      });
    }

    if (moodFilter) {
      list = list.filter((s) => {
        if (s.valence === null) return false;
        if (moodFilter == 'negative') return s.valence < 0.4;
        if (moodFilter == 'neutral') return s.valence >= 0.4 && s.valence < 0.6;
        return s.valence >= 0.6;
      });
    }

    if (outliersOnly) {
      const tempos = list.map((s) => s.tempo).filter((x): x is number => x !== null);
      const energies = list.map((s) => s.energy).filter((x): x is number => x !== null);
      const valences = list.map((s) => s.valence).filter((x): x is number => x !== null);
      const tempoBounds = iqrBounds(tempos);
      const energyBounds = iqrBounds(energies);
      const valenceBounds = iqrBounds(valences);

      list = list.filter((s) => {
        const t = s.tempo;
        const e = s.energy;
        const v = s.valence;
        const tempoOutlier =
          tempoBounds && t !== null && (t < tempoBounds.low || t > tempoBounds.high);
        const energyOutlier =
          energyBounds && e !== null && (e < energyBounds.low || e > energyBounds.high);
        const valenceOutlier =
          valenceBounds && v !== null && (v < valenceBounds.low || v > valenceBounds.high);
        return tempoOutlier || energyOutlier || valenceOutlier;
      });
    }

    if (sortBy) {
      list = [...list].sort((a, b) => {
        const dir = sortDir === 'asc' ? 1 : -1;
        const av = a[sortBy];
        const bv = b[sortBy];
        if (av === null && bv === null) return 0;
        if (av === null) return 1;
        if (bv === null) return -1;
        if (typeof av == 'string' && typeof bv == 'string') {
          return av.localeCompare(bv) * dir;
        }
        if (av == bv) return 0;
        return av > bv ? -1 * dir : 1 * dir;
      });
    }

    return list;
  }, [moodFilter, normalized, outliersOnly, search, sortBy, sortDir, tempoFilter]);

  useEffect(() => {
    prevStatsRef.current = stats;
  }, [stats]);

  useEffect(() => {
    setLastUpdated(Date.now());
  }, [songs]);

  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), 30000);
    return () => window.clearInterval(id);
  }, []);

  const updatedLabel = useMemo(() => {
    if (!lastUpdated) return 'Not updated';
    const seconds = Math.max(0, Math.floor((now - lastUpdated) / 1000));
    if (seconds < 30) return 'Updated just now';
    if (seconds < 60) return `Updated ${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `Updated ${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `Updated ${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `Updated ${days}d ago`;
  }, [lastUpdated, now]);

  const handleSort = (field: 'tempo' | 'energy' | 'valence' | 'track_name' | 'artist_name') => {
    if (sortBy === field) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortBy(field);
      setSortDir('desc');
    }
  };

  const handleExportCsv = () => {
    const rows = tableRows.length ? tableRows : normalized;
    const headers = ['track_name', 'artist_name', 'tempo', 'valence', 'energy'];
    const lines = [
      headers.join(','),
      ...rows.map((r) =>
        headers
          .map((h) => {
            const value = (r as Record<string, string | number | null | undefined>)[h];
            const safe = value === null || value === undefined ? '' : String(value);
            return `"${safe.replace(/"/g, '""')}"`;
          })
          .join(',')
      ),
    ].join('\n');
    const blob = new Blob([lines], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'vibemap-results.csv';
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleExportPng = () => {
    const chart =
      moodChartRef.current ?? tempoChartRef.current ?? artistChartRef.current;
    if (!chart) return;
    const url = chart.getDataURL({ type: 'png', pixelRatio: 2, backgroundColor: '#0b0f16' });
    const link = document.createElement('a');
    link.href = url;
    link.download = 'vibemap-chart.png';
    link.click();
  };

  // DOM refs
  const tempoRef = useRef<HTMLDivElement | null>(null);
  const moodRef = useRef<HTMLDivElement | null>(null);
  const artistRef = useRef<HTMLDivElement | null>(null);

  // Chart instances
  const tempoChartRef = useRef<echarts.EChartsType | null>(null);
  const moodChartRef = useRef<echarts.EChartsType | null>(null);
  const artistChartRef = useRef<echarts.EChartsType | null>(null);

  // Init once + cleanup
  useEffect(() => {
    if (tempoRef.current && !tempoChartRef.current) {
      tempoChartRef.current = echarts.init(tempoRef.current);
    }
    if (moodRef.current && !moodChartRef.current) {
      moodChartRef.current = echarts.init(moodRef.current);
    }
    if (artistRef.current && !artistChartRef.current) {
      artistChartRef.current = echarts.init(artistRef.current);
    }

    const onResize = () => {
      tempoChartRef.current?.resize();
      moodChartRef.current?.resize();
      artistChartRef.current?.resize();
    };
    window.addEventListener('resize', onResize);

    return () => {
      window.removeEventListener('resize', onResize);
      tempoChartRef.current?.dispose();
      moodChartRef.current?.dispose();
      artistChartRef.current?.dispose();
      tempoChartRef.current = null;
      moodChartRef.current = null;
      artistChartRef.current = null;
    };
  }, []);

  // Tempo histogram update
  useEffect(() => {
    const chart = tempoChartRef.current;
    if (!chart) return;

    const tempos = normalized.map((s) => s.tempo).filter((x): x is number => x !== null);
    const { labels, counts } = buildTempoBins(tempos, 10);

    chart.setOption(
      {
        title: { text: 'Tempo Distribution (BPM)' },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: labels, axisLabel: { rotate: 35 } },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: counts }],
        grid: { left: 40, right: 20, top: 60, bottom: 60 },
      },
      { notMerge: true }
    );
  }, [normalized]);

  // Valence vs Energy scatter update
  useEffect(() => {
    const chart = moodChartRef.current;
    if (!chart) return;

    const points = normalized
      .map((s) => {
        if (s.valence === null || s.energy === null) return null;
        return {
          value: [s.valence, s.energy] as [number, number],
          name: `${s.track_name || 'Track'} — ${s.artist_name || 'Artist'}`,
        };
      })
      .filter(Boolean) as Array<{ value: [number, number]; name: string }>;

      chart.setOption(
      {
        title: { text: 'Mood Space (Valence vs Energy)' },
        tooltip: {
          formatter: (p: any) =>
            `${p.data.name}<br/>Valence: ${p.value[0]}<br/>Energy: ${p.value[1]}`,
        },

        xAxis: {
          type: 'value',
          min: 0,
          max: 1,
          name: 'Valence',
          nameLocation: 'middle',
          nameGap: 28,
          splitLine: { show: true },
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 1,
          name: 'Energy',
          nameLocation: 'middle',
          nameGap: 34,
          splitLine: { show: true },
        },

        grid: { left: 60, right: 20, top: 70, bottom: 60 },

        series: [
          {
            name: 'Songs',
            type: 'scatter',
            data: points,
            symbolSize: 10,

            // 1) Quadrant shading
            markArea: {
              silent: true,
              itemStyle: { opacity: 0.08 },
              data: [
                // Calm + Dark (low valence, low energy)
                [
                  { xAxis: 0, yAxis: 0, itemStyle: { color: '#ffffff' } },
                  { xAxis: 0.5, yAxis: 0.5 },
                ],
                // Calm + Positive (high valence, low energy)
                [
                  { xAxis: 0.5, yAxis: 0, itemStyle: { color: '#1DB954' } },
                  { xAxis: 1, yAxis: 0.5 },
                ],
                // Energetic + Dark (low valence, high energy)
                [
                  { xAxis: 0, yAxis: 0.5, itemStyle: { color: '#7c3aed' } },
                  { xAxis: 0.5, yAxis: 1 },
                ],
                // Energetic + Positive (high valence, high energy)
                [
                  { xAxis: 0.5, yAxis: 0.5, itemStyle: { color: '#1DB954' } },
                  { xAxis: 1, yAxis: 1 },
                ],
              ],
            },

            // 2) Quadrant divider lines
            markLine: {
              silent: true,
              symbol: ['none', 'none'],
              lineStyle: { type: 'dashed', opacity: 0.35 },
              data: [{ xAxis: 0.5 }, { yAxis: 0.5 }],
            },
          },

          // 3) Labels overlay (as a text-only scatter)
          {
            type: 'scatter',
            data: [
              { value: [0.25, 0.85], label: 'Energetic + Dark' },
              { value: [0.75, 0.85], label: 'Energetic + Positive' },
              { value: [0.25, 0.15], label: 'Calm + Dark' },
              { value: [0.75, 0.15], label: 'Calm + Positive' },
            ],
            symbolSize: 1,
            itemStyle: { opacity: 0 },
            label: {
              show: true,
              formatter: (p: any) => p.data.label,
              color: 'rgba(255,255,255,0.65)',
              fontSize: 11,
              fontWeight: 600,
            },
            tooltip: { show: false },
            z: 1,
          },
        ],
      },
      { notMerge: true }
    );

  }, [normalized]);

  // Top artists update
  useEffect(() => {
    const chart = artistChartRef.current;
    if (!chart) return;

    const counts = new Map<string, number>();
    for (const s of normalized) {
      const a = (s.artist_name ?? '').trim();
      if (!a) continue;
      counts.set(a, (counts.get(a) || 0) + 1);
    }

    const sorted = Array.from(counts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);

    const artists = sorted.map(([a]) => a);
    const values = sorted.map(([, c]) => c);

    chart.setOption(
      {
        title: { text: 'Top Artists in These Results' },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'value' },
        yAxis: { type: 'category', data: artists },
        series: [{ type: 'bar', data: values }],
        grid: { left: 140, right: 20, top: 60, bottom: 30 },
      },
      { notMerge: true }
    );
  }, [normalized]);
  const distInsights = useMemo(() => {
    const n = normalized.length;
    if (!n) {
      return {
        tempoDominant: '—',
        tempoDominantPct: 0,
        highEnergyPct: 0,
        positiveValencePct: 0,
        topArtist: '—',
        topArtistPct: 0,
        diversityLabel: '—',
      };
    }

    // Tempo buckets
    const tempos = normalized.map((s) => s.tempo).filter((x): x is number => x !== null);
    const slow = tempos.filter((t) => t < 90).length;
    const mid = tempos.filter((t) => t >= 90 && t < 120).length;
    const fast = tempos.filter((t) => t >= 120).length;

    const tempoBucket = [
      { label: 'Slow (<90 BPM)', count: slow },
      { label: 'Mid (90–119 BPM)', count: mid },
      { label: 'Fast (≥120 BPM)', count: fast },
    ].sort((a, b) => b.count - a.count)[0];

    const tempoDominant = tempoBucket.label;
    const tempoDominantPct = tempos.length ? Math.round((tempoBucket.count / tempos.length) * 100) : 0;

    // Energy / Valence distribution
    const energies = normalized.map((s) => s.energy).filter((x): x is number => x !== null);
    const valences = normalized.map((s) => s.valence).filter((x): x is number => x !== null);

    const highEnergyPct = energies.length
      ? Math.round((energies.filter((e) => e >= 0.7).length / energies.length) * 100)
      : 0;

    const positiveValencePct = valences.length
      ? Math.round((valences.filter((v) => v >= 0.6).length / valences.length) * 100)
      : 0;

    // Top artist concentration
    const counts = new Map<string, number>();
    for (const s of normalized) {
      const a = (s.artist_name ?? '').trim();
      if (!a) continue;
      counts.set(a, (counts.get(a) || 0) + 1);
    }

    const top = Array.from(counts.entries()).sort((a, b) => b[1] - a[1])[0];
    const topArtist = top?.[0] ?? '—';
    const topArtistPct = top ? Math.round((top[1] / n) * 100) : 0;

    // Diversity label (simple, readable)
    const unique = stats.uniqueArtists;
    const ratio = n ? unique / n : 0;
    const diversityLabel =
      ratio >= 0.6 ? 'High' : ratio >= 0.35 ? 'Medium' : 'Low';

    return {
      tempoDominant,
      tempoDominantPct,
      highEnergyPct,
      positiveValencePct,
      topArtist,
      topArtistPct,
      diversityLabel,
    };
  }, [normalized, stats.uniqueArtists]);

  // helpers for Tempo Range KPI
  const tempoRange = useMemo(() => {
    const tempos = normalized.map((s) => s.tempo).filter((x): x is number => x !== null);
    if (!tempos.length) return null;
    const min = Math.round(Math.min(...tempos));
    const max = Math.round(Math.max(...tempos));
    return { min, max };
  }, [normalized]);

  return (
    <div className="grid gap-4">
      {/* =========================
          HEADER
      ========================== */}
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-block h-2 w-2 rounded-full bg-spotify-green" />
            <h2 className="text-xl font-semibold">Live Analytics</h2>
          </div>
          <p className="text-sm text-text-secondary">
            Updates every time you generate recommendations
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full border border-dark-highlight bg-dark-elevated px-3 py-1 text-xs text-text-secondary">
            Songs: {stats.count}
          </span>
          <span className="rounded-full border border-dark-highlight bg-dark-elevated px-3 py-1 text-xs text-text-secondary">
            Artists: {stats.uniqueArtists}
          </span>
          <span className="rounded-full border border-dark-highlight bg-dark-elevated px-3 py-1 text-xs text-text-secondary">
            {updatedLabel}
          </span>

          <div className="w-px self-stretch bg-dark-highlight mx-1 hidden sm:block" />

          <button
            className="rounded-lg border border-dark-highlight bg-dark-elevated px-3 py-1.5 text-xs hover:border-spotify-green transition"
            onClick={handleExportPng}
          >
            Export PNG
          </button>
          <button
            className="rounded-lg border border-dark-highlight bg-dark-elevated px-3 py-1.5 text-xs hover:border-spotify-green transition"
            onClick={handleExportCsv}
          >
            Download CSV
          </button>
        </div>
      </div>

      {/* =========================
          KPI GRID
      ========================== */}
      <div className="grid gap-3 grid-cols-2 md:grid-cols-3 xl:grid-cols-6">
        <KPI title="Songs Returned" value={stats.count} delta={deltas?.count ?? null} />
        <KPI title="Unique Artists" value={stats.uniqueArtists} delta={deltas?.uniqueArtists ?? null} />
        <KPI title="Avg Tempo" value={stats.avgTempo ?? '--'} suffix=" BPM" delta={deltas?.avgTempo ?? null} />
        <KPI
          title="Tempo Range"
          value={tempoRange ? `${tempoRange.min} - ${tempoRange.max}` : '--'}
          suffix=" BPM"
        />
        <KPI title="Avg Energy" value={stats.avgEnergy ?? '--'} delta={deltas?.avgEnergy ?? null} />
        <KPI title="Avg Valence" value={stats.avgValence ?? '--'} delta={deltas?.avgValence ?? null} />
      </div>
            {/* =========================
          DISTRIBUTION INSIGHTS
      ========================== */}
      <div className="rounded-2xl border border-dark-highlight bg-dark-elevated p-4">
        <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
          <div>
            <h3 className="text-sm font-semibold">Distribution Insights</h3>
            <p className="text-xs text-text-secondary">
              Quick breakdown of this recommendation set
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <span className="rounded-full border border-dark-highlight bg-black/20 px-3 py-1 text-xs text-text-secondary">
              Diversity: <span className="text-white">{distInsights.diversityLabel}</span>
            </span>
            <span className="rounded-full border border-dark-highlight bg-black/20 px-3 py-1 text-xs text-text-secondary">
              Top artist share: <span className="text-white">{distInsights.topArtistPct}%</span>
            </span>
            <span className="rounded-full border border-dark-highlight bg-black/20 px-3 py-1 text-xs text-text-secondary">
              High-energy: <span className="text-white">{distInsights.highEnergyPct}%</span>
            </span>
            <span className="rounded-full border border-dark-highlight bg-black/20 px-3 py-1 text-xs text-text-secondary">
              Positive mood: <span className="text-white">{distInsights.positiveValencePct}%</span>
            </span>
          </div>
        </div>

        <div className="mt-3 grid gap-2 md:grid-cols-2">
          <div className="rounded-xl border border-dark-highlight bg-black/20 p-3 text-sm text-text-secondary">
            • Dominant tempo bucket: <span className="text-white">{distInsights.tempoDominant}</span>{' '}
            <span className="text-white">({distInsights.tempoDominantPct}%)</span>
          </div>

          <div className="rounded-xl border border-dark-highlight bg-black/20 p-3 text-sm text-text-secondary">
            • Most frequent artist: <span className="text-white">{distInsights.topArtist}</span>{' '}
            <span className="text-white">({distInsights.topArtistPct}% of results)</span>
          </div>
        </div>
      </div>


      {/* =========================
          INSIGHT SUMMARY
      ========================== */}
      <div className="rounded-2xl border border-dark-highlight bg-dark-elevated p-4">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h3 className="text-sm font-semibold">Recommendation Profile</h3>
            <p className="text-xs text-text-secondary">
              Quick summary based on current recommendation set
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <span className="rounded-full bg-spotify-green/10 border border-spotify-green/20 px-3 py-1 text-xs text-spotify-green">
              {Number(stats.avgEnergy) >= 0.7 ? 'High Energy' : 'Balanced Energy'}
            </span>
            <span className="rounded-full bg-spotify-green/10 border border-spotify-green/20 px-3 py-1 text-xs text-spotify-green">
              {Number(stats.avgValence) >= 0.6 ? 'Positive Mood' : 'Neutral Mood'}
            </span>
            <span className="rounded-full bg-spotify-green/10 border border-spotify-green/20 px-3 py-1 text-xs text-spotify-green">
              {Number(stats.avgTempo) >= 120
                ? 'Fast Leaning'
                : Number(stats.avgTempo) >= 90
                ? 'Mid Tempo'
                : 'Slow Leaning'}
            </span>
          </div>
        </div>
      </div>

      {/* =========================
          CHART GRID
      ========================== */}
      <div className="grid gap-4 grid-cols-1 lg:grid-cols-2">
        <div className="rounded-2xl border border-dark-highlight bg-dark-elevated p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold">Tempo Distribution</h3>
            <span className="text-xs text-text-secondary">BPM bins</span>
          </div>
          <div className="h-[340px]">
            <div ref={tempoRef} className="h-full w-full" />
          </div>
        </div>

        <div className="rounded-2xl border border-dark-highlight bg-dark-elevated p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold">Mood Space</h3>
            <span className="text-xs text-text-secondary">Valence vs Energy</span>
          </div>
          <div className="h-[340px]">
            <div ref={moodRef} className="h-full w-full" />
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-dark-highlight bg-dark-elevated p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold">Top Artists</h3>
          <span className="text-xs text-text-secondary">Most frequent in result set</span>
        </div>
        <div className="h-[320px]">
          <div ref={artistRef} className="h-full w-full" />
        </div>
      </div>

      {/* =========================
          EXPLAINABILITY
      ========================== */}
      <details className="rounded-2xl border border-dark-highlight bg-dark-elevated p-4">
        <summary className="cursor-pointer list-none flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold">Why these songs?</h3>
            <p className="text-xs text-text-secondary">
              Explainability notes (simple but powerful)
            </p>
          </div>
          <span className="text-xs text-text-secondary">Toggle</span>
        </summary>

        <div className="mt-4 grid gap-2 text-sm text-text-secondary">
          <div className="rounded-xl border border-dark-highlight p-3">
            • Songs are selected because they are close in{' '}
            <span className="text-white">mood space</span> (valence + energy).
          </div>
          <div className="rounded-xl border border-dark-highlight p-3">
            • Tempo is constrained around a similar range to keep the vibe consistent.
          </div>
          <div className="rounded-xl border border-dark-highlight p-3">
            • Artist diversity helps avoid repeating the same creator too often.
          </div>
        </div>
      </details>

      {/* =========================
          TABLE PREVIEW
      ========================== */}
      <div className="rounded-2xl border border-dark-highlight bg-dark-elevated p-4">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between mb-3">
          <h3 className="text-sm font-semibold">Result Preview</h3>

          <div className="flex flex-wrap items-center gap-2">
            <input
              className="h-9 w-52 rounded-lg border border-dark-highlight bg-black/20 px-3 text-sm outline-none focus:border-spotify-green"
              placeholder="Search track/artist..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <select
              className="h-9 rounded-lg border border-dark-highlight bg-black/20 px-3 text-sm outline-none focus:border-spotify-green"
              value={sortBy}
              onChange={(e) =>
                setSortBy(
                  e.target.value as
                    | 'tempo'
                    | 'energy'
                    | 'valence'
                    | 'track_name'
                    | 'artist_name'
                    | ''
                )
              }
            >
              <option value="">Sort by</option>
              <option value="track_name">Track</option>
              <option value="artist_name">Artist</option>
              <option value="tempo">Tempo</option>
              <option value="energy">Energy</option>
              <option value="valence">Valence</option>
            </select>
            <button
              className="h-9 rounded-lg border border-dark-highlight bg-black/20 px-3 text-xs text-text-secondary hover:border-spotify-green transition"
              onClick={() => setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'))}
            >
              {sortDir === 'asc' ? 'Asc' : 'Desc'}
            </button>
            <button
              className={`h-9 rounded-lg border border-dark-highlight bg-black/20 px-3 text-sm transition ${
                outliersOnly ? 'border-spotify-green text-spotify-green' : 'hover:border-spotify-green'
              }`}
              onClick={() => setOutliersOnly((prev) => !prev)}
            >
              Outliers
            </button>
            <span className="text-xs text-text-secondary" title="Outliers are values outside 1.5x IQR for tempo, energy, or valence.">
              (i)
            </span>
            <button
              className="h-9 rounded-lg border border-dark-highlight bg-black/20 px-3 text-xs text-text-secondary hover:border-spotify-green transition"
              onClick={() => {
                setSearch('');
                setSortBy('');
                setSortDir('desc');
                setOutliersOnly(false);
                setTempoFilter('');
                setMoodFilter('');
              }}
            >
              Reset filters
            </button>
          </div>
        </div>

        <div className="mb-2 flex flex-wrap items-center gap-2 text-xs">
          <span className="text-text-secondary">Tempo:</span>
          {[
            { label: 'Slow', value: 'slow' },
            { label: 'Mid', value: 'mid' },
            { label: 'Fast', value: 'fast' },
          ].map((chip) => (
            <button
              key={chip.value}
              className={`rounded-full border px-3 py-1 ${
                tempoFilter === chip.value
                  ? 'border-spotify-green text-spotify-green bg-black/30'
                  : 'border-dark-highlight text-text-secondary bg-black/10'
              }`}
              onClick={() =>
                setTempoFilter((prev) =>
                  prev === chip.value ? '' : (chip.value as 'slow' | 'mid' | 'fast')
                )
              }
            >
              {chip.label}
            </button>
          ))}
          <span className="text-text-secondary ml-2">Mood:</span>
          {[
            { label: 'Negative', value: 'negative' },
            { label: 'Neutral', value: 'neutral' },
            { label: 'Positive', value: 'positive' },
          ].map((chip) => (
            <button
              key={chip.value}
              className={`rounded-full border px-3 py-1 ${
                moodFilter === chip.value
                  ? 'border-spotify-green text-spotify-green bg-black/30'
                  : 'border-dark-highlight text-text-secondary bg-black/10'
              }`}
              onClick={() =>
                setMoodFilter((prev) =>
                  prev === chip.value ? '' : (chip.value as 'negative' | 'neutral' | 'positive')
                )
              }
            >
              {chip.label}
            </button>
          ))}
        </div>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr>
                {['track_name', 'artist_name', 'tempo', 'valence', 'energy'].map((h) => (
                  <th
                    key={h}
                    className="text-left p-2 border-b border-dark-highlight text-xs text-text-secondary uppercase tracking-wide cursor-pointer select-none"
                    onClick={() =>
                      handleSort(
                        h as 'track_name' | 'artist_name' | 'tempo' | 'valence' | 'energy'
                      )
                    }
                  >
                    <span className="flex items-center gap-1">
                      {h.replace('_', ' ')}
                      {sortBy === h && (
                        <span className="text-[10px] text-text-secondary">
                          {sortDir === 'asc' ? '^' : 'v'}
                        </span>
                      )}
                    </span>
                  </th>
                ))}
              </tr>
            </thead>

            <tbody>
              {tableRows.slice(0, 20).map((s, i) => (
                <tr key={s.track_id ?? `${s.track_name}-${s.artist_name}-${i}`}>
                  <td className="p-2 border-b border-dark-highlight">{s.track_name}</td>
                  <td className="p-2 border-b border-dark-highlight">{s.artist_name}</td>
                  <td className="p-2 border-b border-dark-highlight">{s.tempo ?? '—'}</td>
                  <td className="p-2 border-b border-dark-highlight">{s.valence ?? '—'}</td>
                  <td className="p-2 border-b border-dark-highlight">{s.energy ?? '—'}</td>
                </tr>
              ))}

              {tableRows.length === 0 && (
                <tr>
                  <td className="p-2 text-text-secondary" colSpan={5}>
                    No data yet — generate recommendations to populate analytics.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

function KPI({
  title,
  value,
  suffix = '',
  delta,
}: {
  title: string;
  value: number | string;
  suffix?: string;
  delta?: number | null;
}) {
  const deltaLabel =
    delta === null || delta === undefined
      ? null
      : delta > 0
        ? `+${delta}`
        : String(delta);

  return (
    <div className="rounded-xl border border-dark-highlight bg-dark-elevated p-3">
      <div className="text-xs text-text-secondary">{title}</div>
      <div className="text-2xl font-bold mt-1">
        {value}
        <span className="text-xs text-text-secondary ml-1">{suffix}</span>
      </div>
      {deltaLabel && (
        <div className="mt-1 text-xs text-text-secondary">
          {delta > 0 ? '^' : delta < 0 ? 'v' : '-'} {deltaLabel}
        </div>
      )}
    </div>
  );
}

export default AnalyticsDashboard;

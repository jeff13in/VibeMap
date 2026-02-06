import { useEffect, useMemo, useRef } from 'react';
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
      { notMerge: true, lazyUpdate: false }
    );
  }, [normalized]);

  // Valence vs Energy scatter update + quadrant counts overlay
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

    // ✅ IMPORTANT: Count QUADRANTS based on the same points you're plotting
    let calmDark = 0;
    let calmPositive = 0;
    let energeticDark = 0;
    let energeticPositive = 0;

    for (const p of points) {
      const v = p.value[0];
      const e = p.value[1];

      if (v < 0.5 && e < 0.5) calmDark++;
      else if (v >= 0.5 && e < 0.5) calmPositive++;
      else if (v < 0.5 && e >= 0.5) energeticDark++;
      else energeticPositive++;
    }

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
          // 1) Main scatter + quadrants
          {
            name: 'Songs',
            type: 'scatter',
            data: points,
            symbolSize: 10,

            markArea: {
              silent: true,
              itemStyle: { opacity: 0.10 },
              data: [
                // Calm + Dark
                [{ xAxis: 0, yAxis: 0, itemStyle: { color: '#ffffff' } }, { xAxis: 0.5, yAxis: 0.5 }],
                // Calm + Positive
                [{ xAxis: 0.5, yAxis: 0, itemStyle: { color: '#1DB954' } }, { xAxis: 1, yAxis: 0.5 }],
                // Energetic + Dark
                [{ xAxis: 0, yAxis: 0.5, itemStyle: { color: '#7c3aed' } }, { xAxis: 0.5, yAxis: 1 }],
                // Energetic + Positive
                [{ xAxis: 0.5, yAxis: 0.5, itemStyle: { color: '#1DB954' } }, { xAxis: 1, yAxis: 1 }],
              ],
            },

            markLine: {
              silent: true,
              symbol: ['none', 'none'],
              lineStyle: { type: 'dashed', opacity: 0.35 },
              data: [{ xAxis: 0.5 }, { yAxis: 0.5 }],
            },
          },

          // 2) Labels + counts overlay (text-only scatter)
          {
            type: 'scatter',
            data: [
              { value: [0.25, 0.88], label: `Energetic + Dark (${energeticDark})` },
              { value: [0.75, 0.88], label: `Energetic + Positive (${energeticPositive})` },
              { value: [0.25, 0.12], label: `Calm + Dark (${calmDark})` },
              { value: [0.75, 0.12], label: `Calm + Positive (${calmPositive})` },
            ],
            symbolSize: 1,
            itemStyle: { opacity: 0 },
            label: {
              show: true,
              formatter: (p: any) => p.data.label,
              color: 'rgba(255,255,255,0.78)',
              fontSize: 12,
              fontWeight: 800,
              backgroundColor: 'rgba(0,0,0,0.25)',
              padding: [4, 8],
              borderRadius: 8,
            },
            tooltip: { show: false },

            // ✅ FIX #1: ensure overlay renders on top
            z: 10,
          },
        ],
      },
      // ✅ FIX #2: force redraw so labels update reliably
      { notMerge: true, lazyUpdate: false }
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
      { notMerge: true, lazyUpdate: false }
    );
  }, [normalized]);

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
      {/* KPI GRID */}
      <div className="grid gap-3 grid-cols-2 md:grid-cols-3 xl:grid-cols-6">
        <KPI title="Songs Returned" value={stats.count} />
        <KPI title="Unique Artists" value={stats.uniqueArtists} />
        <KPI title="Avg Tempo" value={stats.avgTempo ?? '—'} suffix=" BPM" />
        <KPI
          title="Tempo Range"
          value={tempoRange ? `${tempoRange.min} - ${tempoRange.max}` : '—'}
          suffix=" BPM"
        />
        <KPI title="Avg Energy" value={stats.avgEnergy ?? '—'} />
        <KPI title="Avg Valence" value={stats.avgValence ?? '—'} />
      </div>

      {/* CHART GRID */}
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
    </div>
  );
};

function KPI({
  title,
  value,
  suffix = '',
}: {
  title: string;
  value: number | string;
  suffix?: string;
}) {
  return (
    <div className="rounded-xl border border-dark-highlight bg-dark-elevated p-3">
      <div className="text-xs text-text-secondary">{title}</div>
      <div className="text-2xl font-bold mt-1">
        {value}
        <span className="text-xs text-text-secondary ml-1">{suffix}</span>
      </div>
    </div>
  );
}

export default AnalyticsDashboard;

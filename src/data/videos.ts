import raw from './videos.json';
import { withBase } from '../utils';

/** 视频号「爪哇爹」AI 讲解短视频（清单由 videos.json 提供，最新在前） */
export interface Video {
  slug: string;
  title: string;
  /** YYYY-MM-DD */
  date: string;
  duration_sec: number;
  width: number;
  height: number;
  /** 相对 public/ 的路径，如 posters/xxx.webp */
  poster: string;
  /** 相对 public/ 的路径，如 videos/xxx.mp4 */
  src: string;
  size_mb: number;
  category: string;
  description: string;
}

export const VIDEOS: Video[] = (raw as Video[]).slice().sort((a, b) => b.date.localeCompare(a.date));

/** 视频号主页信息（截至 2026-11-11） */
export const CHANNEL = {
  name: '爪哇爹',
  platform: '微信视频号',
  location: '湖南 长沙',
  asOf: '2026-11-11',
  cta: '微信搜索视频号「爪哇爹」',
  stats: [
    { label: '关注', value: 914 },
    { label: '获赞', value: 3441 },
    { label: '喜欢', value: 5390 },
    { label: '原创', value: 233 },
  ],
} as const;

/** 分类固定顺序与配色（色相），未列出的分类排在最后 */
export const CATEGORY_META: Record<string, { hue: number; en: string }> = {
  'AI Agent': { hue: 250, en: 'Agent' },
  'Claude Code / AI 编程': { hue: 200, en: 'AI Coding' },
  '大模型与行业': { hue: 285, en: 'LLM' },
  'RAG / 数据': { hue: 165, en: 'RAG' },
  'GitHub 热榜': { hue: 35, en: 'Trending' },
  '系统设计': { hue: 330, en: 'Design' },
};

export function categoryHue(category: string): number {
  return CATEGORY_META[category]?.hue ?? 230;
}

export function videoCategories(list: Video[] = VIDEOS): { category: string; count: number }[] {
  const map = new Map<string, number>();
  for (const v of list) map.set(v.category, (map.get(v.category) || 0) + 1);
  const order = Object.keys(CATEGORY_META);
  return [...map.entries()]
    .map(([category, count]) => ({ category, count }))
    .sort((a, b) => b.count - a.count || order.indexOf(a.category) - order.indexOf(b.category));
}

export function videoSrc(v: Video): string {
  return withBase(`/${v.src.replace(/^\//, '')}`);
}

export function posterSrc(v: Video): string {
  return withBase(`/${v.poster.replace(/^\//, '')}`);
}

/** 秒 → mm:ss */
export function formatDuration(sec: number): string {
  const s = Math.max(0, Math.round(sec));
  return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
}

export function totalDurationMinutes(list: Video[] = VIDEOS): number {
  return Math.round(list.reduce((n, v) => n + v.duration_sec, 0) / 60);
}

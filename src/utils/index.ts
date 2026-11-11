import { getCollection, type CollectionEntry } from 'astro:content';

export type Post = CollectionEntry<'blog'>;

/** 拼接 base 路径，兼容 GitHub Pages 子路径部署 */
export function withBase(path = '/'): string {
  if (/^(https?:|mailto:|#)/.test(path)) return path;
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${base}${p}` || '/';
}

export async function getPosts(): Promise<Post[]> {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  return posts.sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
}

export function postUrl(post: Post): string {
  return withBase(`/blog/${post.id}/`);
}

export function tagUrl(tag: string): string {
  return withBase(`/tags/${encodeURIComponent(tag)}/`);
}

export function formatDate(d: Date): string {
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}-${String(d.getUTCDate()).padStart(2, '0')}`;
}

export function formatDateZh(d: Date): string {
  return `${d.getUTCFullYear()} 年 ${d.getUTCMonth() + 1} 月 ${d.getUTCDate()} 日`;
}

/** 中文按字计（约 400 字/分钟），英文按词计（约 200 词/分钟） */
export function readingTime(body = ''): { minutes: number; words: number } {
  const text = body
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1');
  const cjk = (text.match(/[\u4e00-\u9fff\u3400-\u4dbf]/g) || []).length;
  const en = (text.replace(/[\u4e00-\u9fff\u3400-\u4dbf]/g, ' ').match(/[A-Za-z0-9_]+/g) || []).length;
  const minutes = Math.max(1, Math.round(cjk / 400 + en / 200));
  return { minutes, words: cjk + en };
}

export function allTags(posts: Post[]): { tag: string; count: number }[] {
  const map = new Map<string, number>();
  for (const p of posts) for (const t of p.data.tags) map.set(t, (map.get(t) || 0) + 1);
  return [...map.entries()].map(([tag, count]) => ({ tag, count })).sort((a, b) => b.count - a.count || a.tag.localeCompare(b.tag, 'zh'));
}

export const SITE = {
  title: '周正 · Zheng Zhou',
  shortTitle: 'Zheng Zhou',
  description:
    '周正（Jeff Chou / 正哥 / 爪哇爹）——程序员、Java & Python & AI Agent 讲师、创作者。记录代码之外的思考、日常与成长。',
  author: '周正 Zheng Zhou',
  locale: 'zh-CN',
  email: 'zhouzhengjeff@gmail.com',
  github: 'https://github.com/zhouzhengjeff',
  x: 'https://x.com/JeffChouCheng',
  xHandle: '@JeffChouCheng',
};

export const ROLES = ['程序员', 'Java & Python & AI Agent 讲师', '创作者'];

export const NAV = [
  { href: '/', label: '首页' },
  { href: '/blog/', label: '博客' },
  { href: '/videos/', label: '视频' },
  { href: '/archive/', label: '归档' },
  { href: '/tags/', label: '标签' },
  { href: '/about/', label: '关于' },
];

export type SeriesKey = 'beyond-working' | 'daily' | 'annual' | 'beyond-code';

export const SERIES: Record<SeriesKey, { title: string; en: string; desc: string; icon: 'compass' | 'coffee' | 'calendar' | 'mic' }> = {
  'beyond-working': {
    title: '工作之外系列',
    en: 'Beyond Working',
    desc: '工作之外的人物、音乐与思考，关于如何更好地工作与生活。',
    icon: 'compass',
  },
  daily: {
    title: '我的日常',
    en: 'My Daily',
    desc: '一个 IT 人的日常记录：工具、骑行、家人与琐碎的美好。',
    icon: 'coffee',
  },
  annual: {
    title: '年度总结',
    en: 'Year in Review',
    desc: '每一年的回顾：随心而活，好剧好歌，年度工具折腾之旅。',
    icon: 'calendar',
  },
  'beyond-code': {
    title: '代码之外',
    en: 'Beyond Code',
    desc: '播客「代码之外 Beyond Code」的随想与延伸。',
    icon: 'mic',
  },
};

export const SKILLS: { group: string; items: string[] }[] = [
  { group: '后端 & 架构', items: ['Java', 'Spring Boot', 'Spring Cloud Alibaba', 'Nacos', 'Python', 'Node.js'] },
  { group: 'AI & Agent', items: ['LLM APIs', 'Spring AI', 'LangChain', 'LangGraph', 'MCP', 'AI Agent'] },
  { group: '前端 & 工具', items: ['Vue 3', 'TypeScript', 'Astro', 'Git', 'Notion', 'Logseq'] },
];

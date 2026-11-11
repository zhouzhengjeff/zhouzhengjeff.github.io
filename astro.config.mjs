// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

/**
 * GitHub Pages 配置：
 *  - SITE：站点根地址（默认 https://zhouzhengjeff.github.io）
 *  - BASE：子路径（用户主页仓库为 "/"；项目仓库如 "/my-repo/"）
 */
const SITE = process.env.SITE || 'https://zhouzhengjeff.github.io';
const BASE = process.env.BASE || '/';

export default defineConfig({
  site: SITE,
  base: BASE,
  output: 'static',
  trailingSlash: 'ignore',
  integrations: [mdx(), sitemap({ filter: (page) => !page.includes('/posts/') })],
  markdown: {
    syntaxHighlight: 'shiki',
    shikiConfig: { theme: 'tokyo-night', wrap: false },
  },
  image: {
    responsiveStyles: true,
  },
  build: {
    format: 'directory',
  },
});

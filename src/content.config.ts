import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '*.{md,mdx}', base: './src/content/blog' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      date: z.coerce.date(),
      description: z.string().optional().default(''),
      series: z.enum(['beyond-working', 'daily', 'annual', 'beyond-code']).optional(),
      tags: z.array(z.string()).default([]),
      cover: image().optional(),
      draft: z.boolean().optional().default(false),
      sourceFile: z.string().optional(),
    }),
});

export const collections = { blog };

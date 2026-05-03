import matter from 'gray-matter';

export interface FrontmatterResult {
  data: Record<string, unknown>;
  content: string;
}

export function parseFrontmatter(raw: string): FrontmatterResult {
  try {
    const parsed = matter(raw);
    return { data: parsed.data as Record<string, unknown>, content: parsed.content };
  } catch {
    return { data: {}, content: raw };
  }
}

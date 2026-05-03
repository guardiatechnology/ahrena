/**
 * Extracts name and description from Markdown files without YAML frontmatter.
 * Used for .claude/rules/ files that start directly with a heading.
 *
 * Example: "# Lexis: Python Error Handling\n\n> **Prefix:...**\n\n## Law\n\n> **Bare except..."
 * → name: "Python Error Handling"
 * → description: "Bare except: are FORBIDDEN unless paired with logging..."
 */

const H1_RE = /^#\s+(?:Lexis|Codex|Kata|Warrior|Cry)?:?\s*(.*)/m;
const BLOCKQUOTE_LAW_RE = /^>\s+\*\*.*?\*\*\s+(.*)/m;
const FIRST_SENTENCE_RE = /([^.!?]{10,}[.!?])/;

export interface MarkdownTitleResult {
  name: string;
  description: string;
}

export function parseMarkdownTitle(content: string): MarkdownTitleResult {
  const h1Match = H1_RE.exec(content);
  const name = h1Match ? h1Match[1].trim() : '';

  // Try to extract description from the Law blockquote (bold prefix)
  const lawMatch = BLOCKQUOTE_LAW_RE.exec(content);
  if (lawMatch) {
    const raw = lawMatch[1].replace(/\*\*/g, '').trim();
    const sentence = FIRST_SENTENCE_RE.exec(raw);
    return { name, description: sentence ? sentence[1].trim() : raw.slice(0, 120) };
  }

  // Fallback: first non-heading, non-blockquote, non-empty line after H1
  const lines = content.split('\n');
  let pastH1 = !h1Match;
  for (const line of lines) {
    const trimmed = line.trim();
    if (!pastH1) {
      if (H1_RE.test(trimmed)) { pastH1 = true; }
      continue;
    }
    if (!trimmed || trimmed.startsWith('#') || trimmed.startsWith('>') || trimmed.startsWith('---')) {
      continue;
    }
    const sentence = FIRST_SENTENCE_RE.exec(trimmed);
    return { name, description: sentence ? sentence[1].trim() : trimmed.slice(0, 120) };
  }

  return { name, description: '' };
}

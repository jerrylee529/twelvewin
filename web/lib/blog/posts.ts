import fs from "node:fs";
import path from "node:path";

import matter from "gray-matter";

import type { BlogPost, BlogPostFrontmatter, BlogPostSummary } from "@/lib/blog/types";

const BLOG_CONTENT_DIR = path.join(process.cwd(), "content", "blog");

function normalizeDate(raw: unknown): string {
  if (raw instanceof Date) {
    return raw.toISOString().slice(0, 10);
  }
  return String(raw ?? "").trim();
}

function parseFrontmatter(slug: string, raw: BlogPostFrontmatter): BlogPostFrontmatter {
  if (!raw.title?.trim()) {
    throw new Error(`Blog post "${slug}" is missing required frontmatter field: title`);
  }
  if (!raw.description?.trim()) {
    throw new Error(
      `Blog post "${slug}" is missing required frontmatter field: description`,
    );
  }
  if (!raw.date || !normalizeDate(raw.date)) {
    throw new Error(`Blog post "${slug}" is missing required frontmatter field: date`);
  }

  return {
    title: raw.title.trim(),
    description: raw.description.trim(),
    date: normalizeDate(raw.date),
    published: raw.published !== false,
    tags: raw.tags?.filter(Boolean) ?? [],
    cta: raw.cta?.href && raw.cta?.label ? raw.cta : undefined,
  };
}

function readPostFile(filename: string): BlogPost {
  const slug = filename.replace(/\.md$/, "");
  const filePath = path.join(BLOG_CONTENT_DIR, filename);
  const source = fs.readFileSync(filePath, "utf8");
  const { data, content } = matter(source);
  const frontmatter = parseFrontmatter(slug, data as BlogPostFrontmatter);

  return {
    slug,
    ...frontmatter,
    content: content.trim(),
  };
}

function listMarkdownFilenames(): string[] {
  if (!fs.existsSync(BLOG_CONTENT_DIR)) {
    return [];
  }

  return fs
    .readdirSync(BLOG_CONTENT_DIR)
    .filter((name) => name.endsWith(".md"))
    .sort();
}

export function getAllPosts(includeDrafts = false): BlogPost[] {
  return listMarkdownFilenames()
    .map((filename) => readPostFile(filename))
    .filter((post) => includeDrafts || post.published)
    .sort((a, b) => b.date.localeCompare(a.date));
}

export function getAllPostSummaries(includeDrafts = false): BlogPostSummary[] {
  return getAllPosts(includeDrafts).map(({ content: _content, ...summary }) => summary);
}

export function getPostBySlug(slug: string, includeDrafts = false): BlogPost | null {
  const filePath = path.join(BLOG_CONTENT_DIR, `${slug}.md`);
  if (!fs.existsSync(filePath)) {
    return null;
  }

  const post = readPostFile(`${slug}.md`);
  if (!includeDrafts && !post.published) {
    return null;
  }

  return post;
}

export function getAllPostSlugs(includeDrafts = false): string[] {
  return getAllPostSummaries(includeDrafts).map((post) => post.slug);
}

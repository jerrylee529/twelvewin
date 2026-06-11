import Link from "next/link";
import { Clock3 } from "lucide-react";

import { estimateReadingMinutes } from "@/lib/blog/reading-time";
import type { BlogPostSummary } from "@/lib/blog/types";

const THUMB_BARS = Array.from({ length: 9 }, (_, i) => i);

export function BlogPostCard({ post }: { post: BlogPostSummary }) {
  const readingMinutes = estimateReadingMinutes(post.description);

  return (
    <article className="blog-card group">
      <div className="blog-card-meta">
        <div className="blog-card-meta-row">
          <time dateTime={post.date}>{post.date}</time>
          <span className="blog-card-meta-divider" aria-hidden />
          <span className="blog-card-meta-row">
            <Clock3 className="h-3 w-3" aria-hidden />
            {readingMinutes} 分钟阅读
          </span>
        </div>
      </div>

      {post.tags && post.tags.length > 0 ? (
        <div className="blog-card-tags">
          {post.tags.map((tag) => (
            <span key={tag} className="blog-tag">
              {tag}
            </span>
          ))}
        </div>
      ) : null}

      <h2 className="blog-card-title">
        <Link href={`/blog/${post.slug}`}>{post.title}</Link>
      </h2>

      <p className="blog-card-desc">{post.description}</p>

      <div className="blog-card-footer">
        <Link href={`/blog/${post.slug}`} className="blog-read-link">
          阅读全文
          <svg
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M14 5l7 7m0 0l-7 7m7-7H3"
            />
          </svg>
        </Link>

        <div className="blog-thumb" aria-hidden>
          <div className="blog-thumb-chart">
            {THUMB_BARS.map((i) => (
              <span key={i} className="blog-thumb-bar" />
            ))}
          </div>
        </div>
      </div>
    </article>
  );
}

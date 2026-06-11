import Link from "next/link";
import { notFound } from "next/navigation";
import { Clock3 } from "lucide-react";

import { ArticleBody } from "@/components/blog/article-body";
import { JsonLd } from "@/components/json-ld";
import { estimateReadingMinutes } from "@/lib/blog/reading-time";
import { getAllPostSlugs, getPostBySlug } from "@/lib/blog/posts";
import { absoluteUrl, buildBlogPostMetadata } from "@/lib/seo";

type BlogPostPageProps = {
  params: Promise<{ slug: string }>;
};

export function generateStaticParams() {
  return getAllPostSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: BlogPostPageProps) {
  const { slug } = await params;
  const post = getPostBySlug(slug);
  if (!post) {
    return {};
  }

  return buildBlogPostMetadata({
    title: post.title,
    description: post.description,
    slug: post.slug,
    date: post.date,
    tags: post.tags,
  });
}

export default async function BlogPostPage({ params }: BlogPostPageProps) {
  const { slug } = await params;
  const post = getPostBySlug(slug);
  if (!post) {
    notFound();
  }

  const readingMinutes = estimateReadingMinutes(post.content);
  const url = absoluteUrl(`/blog/${post.slug}`);
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: post.title,
    description: post.description,
    datePublished: post.date,
    url,
    author: {
      "@type": "Organization",
      name: "团赢数据",
    },
    publisher: {
      "@type": "Organization",
      name: "团赢数据",
    },
    keywords: post.tags?.join(", "),
  };

  return (
    <main className="blog-main">
      <JsonLd data={jsonLd} />

      <Link href="/blog" className="blog-article-back">
        ← 返回博客
      </Link>

      <header className="blog-article-header">
        <div className="blog-article-meta">
          <time dateTime={post.date}>{post.date}</time>
          <span className="blog-card-meta-divider" aria-hidden />
          <span className="blog-card-meta-row">
            <Clock3 className="h-3 w-3" aria-hidden />
            {readingMinutes} 分钟阅读
          </span>
        </div>

        {post.tags && post.tags.length > 0 ? (
          <div className="blog-card-tags mt-4">
            {post.tags.map((tag) => (
              <span key={tag} className="blog-tag">
                {tag}
              </span>
            ))}
          </div>
        ) : null}

        <h1 className="blog-article-title">{post.title}</h1>
        <p className="blog-article-desc">{post.description}</p>
      </header>

      <ArticleBody content={post.content} className="mt-8" />

      {post.cta ? (
        <div className="blog-cta-box">
          <p className="blog-cta-label">相关工具</p>
          <p className="blog-cta-text">
            在团赢数据研究终端中打开交互式聚类图表与热力图。
          </p>
          <Link href={post.cta.href} className="blog-cta-button">
            {post.cta.label}
          </Link>
        </div>
      ) : null}

      <footer className="blog-disclaimer">
        本文为研究方法说明，不构成投资建议。股市有风险，决策需谨慎。
      </footer>
    </main>
  );
}

import type { Metadata } from "next";

import { BlogPostCard } from "@/components/blog/blog-post-card";
import { buildBlogIndexMetadata } from "@/lib/seo";
import { getAllPostSummaries } from "@/lib/blog/posts";

export const metadata: Metadata = buildBlogIndexMetadata();

const BLOG_LEAD =
  "团赢数据提供 A 股日终量化研究服务，包括基本面排行与筛选（市盈率、市净率、ROE、股息率）、技术面异动榜单（创新高、突破均线、涨跌幅等）、指数与行业相关性聚类、个股财务估值研究及行业分析报告。本博客发布配套的研究方法、数据解读与实战案例，帮助你将终端里的分析能力应用到实际投资决策中。";

export default function BlogIndexPage() {
  const posts = getAllPostSummaries();

  return (
    <main className="blog-main">
      <header className="blog-hero">
        <div className="blog-breadcrumb">
          <span>研究博客</span>
          <span className="blog-breadcrumb-sep">/</span>
          <span className="blog-breadcrumb-current">量化研究系列</span>
        </div>

        <h1 className="blog-title">量化研究方法与实践</h1>

        <p className="blog-lead">{BLOG_LEAD}</p>
      </header>

      {posts.length === 0 ? (
        <p className="blog-empty">暂无已发布文章。</p>
      ) : (
        <div className="blog-post-list">
          {posts.map((post) => (
            <BlogPostCard key={post.slug} post={post} />
          ))}
        </div>
      )}
    </main>
  );
}

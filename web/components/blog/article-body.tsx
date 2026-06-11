import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSanitize from "rehype-sanitize";

function isInternalHref(href: string | undefined): href is string {
  return Boolean(href && (href.startsWith("/") || href.startsWith("#")));
}

type ArticleBodyProps = {
  content: string;
  className?: string;
};

export function ArticleBody({ content, className = "" }: ArticleBodyProps) {
  return (
    <article className={`blog-prose ${className}`.trim()}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeSanitize]}
        components={{
          a: ({ href, children }) => {
            if (isInternalHref(href)) {
              return <Link href={href}>{children}</Link>;
            }

            return (
              <a href={href} target="_blank" rel="noopener noreferrer">
                {children}
              </a>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </article>
  );
}

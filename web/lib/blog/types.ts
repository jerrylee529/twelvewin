export type BlogPostCta = {
  href: string;
  label: string;
};

export type BlogPostFrontmatter = {
  title: string;
  description: string;
  date: string;
  published?: boolean;
  tags?: string[];
  cta?: BlogPostCta;
};

export type BlogPost = BlogPostFrontmatter & {
  slug: string;
  content: string;
};

export type BlogPostSummary = BlogPostFrontmatter & {
  slug: string;
};

import { LandingHeader } from "@/components/landing/landing-header";
import "./blog.css";

export default function BlogLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="blog-shell">
      <LandingHeader />
      {children}
    </div>
  );
}

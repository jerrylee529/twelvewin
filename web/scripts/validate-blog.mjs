import fs from "node:fs";
import path from "node:path";

import matter from "gray-matter";

const contentDir = path.join(process.cwd(), "content", "blog");

function fail(message) {
  console.error(`validate-blog: ${message}`);
  process.exitCode = 1;
}

if (!fs.existsSync(contentDir)) {
  console.log("validate-blog: no content/blog directory (ok for empty blog)");
  process.exit(0);
}

const files = fs.readdirSync(contentDir).filter((name) => name.endsWith(".md"));

if (files.length === 0) {
  console.log("validate-blog: no markdown files found");
  process.exit(0);
}

let errors = 0;

for (const filename of files) {
  const slug = filename.replace(/\.md$/, "");
  const source = fs.readFileSync(path.join(contentDir, filename), "utf8");
  const { data, content } = matter(source);

  for (const field of ["title", "description", "date"]) {
    const value = data[field];
    const normalized =
      value instanceof Date ? value.toISOString().slice(0, 10) : String(value ?? "").trim();
    if (!normalized) {
      fail(`${filename}: missing required frontmatter "${field}"`);
      errors += 1;
    }
  }

  const dateValue = data.date;
  const dateString =
    dateValue instanceof Date
      ? dateValue.toISOString().slice(0, 10)
      : String(dateValue ?? "").trim();
  if (dateString && Number.isNaN(Date.parse(`${dateString}T00:00:00`))) {
    fail(`${filename}: invalid date "${dateString}" (use YYYY-MM-DD)`);
    errors += 1;
  }

  if (!content.trim()) {
    fail(`${filename}: empty body`);
    errors += 1;
  }

  if (data.cta && (!data.cta.href || !data.cta.label)) {
    fail(`${filename}: cta requires both href and label`);
    errors += 1;
  }

  console.log(`validate-blog: ok ${slug}`);
}

if (errors > 0) {
  process.exit(1);
}

console.log(`validate-blog: ${files.length} file(s) passed`);

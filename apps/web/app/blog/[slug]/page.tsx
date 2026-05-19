import fs from "node:fs/promises";
import path from "node:path";
import Link from "next/link";
import { notFound } from "next/navigation";

type PageProps = {
  params: Promise<{ slug: string }>;
};

async function readDoc(slug: string): Promise<string | null> {
  const root = process.cwd();
  const docsDir = path.join(root, "..", "generated_medical_pillars");
  const fullPath = path.join(docsDir, `${slug}.md`);

  try {
    return await fs.readFile(fullPath, "utf-8");
  } catch {
    return null;
  }
}

export const dynamic = "force-dynamic";

export default async function BlogDocPage({ params }: PageProps) {
  const { slug } = await params;
  const content = await readDoc(slug);

  if (!content) {
    notFound();
  }

  return (
    <main style={{ maxWidth: 980, margin: "0 auto", padding: "2rem 1rem" }}>
      <p style={{ marginBottom: "1rem" }}>
        <Link href="/blog">← Back to blog index</Link>
      </p>
      <h1 style={{ fontSize: "1.6rem", marginBottom: "1rem" }}>{slug}</h1>
      <pre
        style={{
          whiteSpace: "pre-wrap",
          lineHeight: 1.45,
          border: "1px solid #ddd",
          borderRadius: 8,
          padding: "1rem",
          background: "#fafafa",
        }}
      >
        {content}
      </pre>
    </main>
  );
}

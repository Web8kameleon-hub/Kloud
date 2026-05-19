import fs from "node:fs/promises";
import path from "node:path";
import Link from "next/link";

type DocItem = {
  slug: string;
  fileName: string;
  updatedAt: string;
};

async function getDocs(): Promise<DocItem[]> {
  const root = process.cwd();
  const docsDir = path.join(root, "..", "generated_medical_pillars");

  try {
    const entries = await fs.readdir(docsDir, { withFileTypes: true });
    const mdFiles = entries.filter((e) => e.isFile() && e.name.endsWith(".md"));

    const docs = await Promise.all(
      mdFiles.map(async (entry) => {
        const fullPath = path.join(docsDir, entry.name);
        const stat = await fs.stat(fullPath);
        const slug = entry.name.replace(/\.md$/, "");
        return {
          slug,
          fileName: entry.name,
          updatedAt: stat.mtime.toISOString(),
        };
      }),
    );

    return docs.sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1));
  } catch {
    return [];
  }
}

export const dynamic = "force-dynamic";

export default async function BlogIndexPage() {
  const docs = await getDocs();

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>Kameleon Blog</h1>
      <p style={{ marginBottom: "1.5rem", opacity: 0.8 }}>
        Dokumentat e gjeneruara publikohen automatikisht nga folderi generated_medical_pillars.
      </p>

      {docs.length === 0 ? (
        <p>No generated markdown documents found.</p>
      ) : (
        <ul style={{ display: "grid", gap: "0.75rem", listStyle: "none", padding: 0 }}>
          {docs.map((doc) => (
            <li key={doc.slug} style={{ border: "1px solid #ddd", borderRadius: 8, padding: "0.75rem" }}>
              <Link href={`/blog/${doc.slug}`} style={{ fontWeight: 600 }}>
                {doc.fileName}
              </Link>
              <div style={{ fontSize: "0.85rem", opacity: 0.7 }}>Updated: {doc.updatedAt}</div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}

import { existsSync, readFileSync } from "fs";
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";
export const revalidate = 0;

type DeploymentEntry = {
  raw: string;
  date?: string;
  time?: string;
  sha?: string;
  services?: string;
  status?: string;
  notes?: string;
};

function readDeploymentLog(): string[] {
  const candidates = [
    process.env.KLOUD_DEPLOYMENT_LOG_PATH,
    `${process.cwd()}\\DEPLOYMENT_LOG.txt`,
    `${process.cwd()}\\deployment_log.txt`,
  ].filter(Boolean) as string[];

  for (const candidate of candidates) {
    if (existsSync(candidate)) {
      return readFileSync(candidate, "utf8").split(/\r?\n/).filter(Boolean);
    }
  }

  return [];
}

function parseEntries(lines: string[]): DeploymentEntry[] {
  return lines.map((line) => {
    const parts = line.split("|").map((part) => part.trim());
    return {
      raw: line,
      date: parts[0],
      time: parts[1],
      sha: parts[2],
      services: parts[3],
      status: parts[4],
      notes: parts.slice(5).join(" | ") || undefined,
    };
  });
}

export async function GET() {
  const lines = readDeploymentLog();
  const entries = parseEntries(lines);
  const recent = entries.slice(-10).reverse();
  const last = recent[0] ?? null;

  return NextResponse.json({
    success: true,
    source: lines.length > 0 ? "local_deployment_log" : "missing",
    count: entries.length,
    last,
    recent,
    has_log: lines.length > 0,
  });
}
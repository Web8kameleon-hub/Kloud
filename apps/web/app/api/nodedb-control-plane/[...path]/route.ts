import { NextRequest, NextResponse } from "next/server";

const CONTROL_PLANE_BASE_URL =
  process.env.NODEDB_CONTROL_PLANE_URL ||
  process.env.NEXT_PUBLIC_CONTROL_PLANE_URL ||
  "http://kloud-nodedb-control-plane:9090";

function buildTargetUrl(request: NextRequest, path: string[]): string {
  const joined = path.join("/");
  const qs = request.nextUrl.search;
  return `${CONTROL_PLANE_BASE_URL}/${joined}${qs}`;
}

async function proxy(request: NextRequest, path: string[]): Promise<NextResponse> {
  const url = buildTargetUrl(request, path);
  const method = request.method;

  const headers: Record<string, string> = {
    Accept: "application/json",
  };

  const contentType = request.headers.get("content-type");
  if (contentType) {
    headers["Content-Type"] = contentType;
  }

  const body = method === "GET" ? undefined : await request.text();

  try {
    const upstream = await fetch(url, {
      method,
      headers,
      body,
      cache: "no-store",
    });

    const text = await upstream.text();

    const contentType = upstream.headers.get("content-type") || "application/json";
    const isHtml = contentType.includes("text/html");

    if (upstream.status >= 500 && isHtml) {
      return NextResponse.json(
        {
          error: "control_plane_bad_gateway",
          message: "Control plane returned an upstream gateway error",
          status: upstream.status,
          target: url,
        },
        { status: upstream.status },
      );
    }

    return new NextResponse(text, {
      status: upstream.status,
      headers: {
        "Content-Type": contentType,
      },
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "NodeDB control plane unavailable";
    return NextResponse.json(
      {
        error: "control_plane_unreachable",
        message,
        target: CONTROL_PLANE_BASE_URL,
      },
      { status: 502 },
    );
  }
}

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  return proxy(request, path || []);
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  return proxy(request, path || []);
}

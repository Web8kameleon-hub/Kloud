import { NextRequest, NextResponse } from 'next/server'

const OPENMIND_BASE_URL =
  process.env.OPENMIND_BASE_URL ||
  process.env.AI_9999_URL ||
  'http://ai-global-9999:9999'

function buildTargetUrl(path: string[], search: string): string {
  const cleanPath = path.join('/')
  return `${OPENMIND_BASE_URL}/api/v1/${cleanPath}${search}`
}

async function forward(request: NextRequest, path: string[]) {
  try {
    const targetUrl = buildTargetUrl(path, request.nextUrl.search)
    const method = request.method

    const headers = new Headers()
    const incomingContentType = request.headers.get('content-type')
    const incomingAccept = request.headers.get('accept')

    if (incomingContentType) headers.set('content-type', incomingContentType)
    if (incomingAccept) headers.set('accept', incomingAccept)

    const init: RequestInit = { method, headers }

    if (!['GET', 'HEAD'].includes(method)) {
      const body = await request.text()
      if (body) init.body = body
    }

    const upstream = await fetch(targetUrl, init)
    const responseText = await upstream.text()

    const outHeaders = new Headers()
    const upstreamContentType = upstream.headers.get('content-type')
    if (upstreamContentType) outHeaders.set('content-type', upstreamContentType)

    return new NextResponse(responseText, {
      status: upstream.status,
      headers: outHeaders,
    })
  } catch (error) {
    return NextResponse.json(
      {
        error: 'OpenMind upstream unavailable',
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 502 },
    )
  }
}

type RouteContext = {
  params: Promise<{ path: string[] }>
}

export async function GET(request: NextRequest, context: RouteContext) {
  const { path } = await context.params
  return forward(request, path)
}

export async function POST(request: NextRequest, context: RouteContext) {
  const { path } = await context.params
  return forward(request, path)
}

export async function PUT(request: NextRequest, context: RouteContext) {
  const { path } = await context.params
  return forward(request, path)
}

export async function PATCH(request: NextRequest, context: RouteContext) {
  const { path } = await context.params
  return forward(request, path)
}

export async function DELETE(request: NextRequest, context: RouteContext) {
  const { path } = await context.params
  return forward(request, path)
}

export async function OPTIONS(request: NextRequest, context: RouteContext) {
  const { path } = await context.params
  return forward(request, path)
}

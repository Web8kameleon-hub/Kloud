/**
 * Kloud Cloud - Chat API with History
 *
 * Persistent chat with Ocean Core AI
 *
 * @author Ledjan Ahmati
 * @copyright 2026 Kloud Cloud
 */

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";

const OCEAN_CORE_URL =
  process.env.NEXT_PUBLIC_OCEAN_API_URL || "http://localhost:8030";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string;
}

interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  model: string;
  createdAt: string;
  updatedAt: string;
}

// In-memory store (replace with database in production)
const chatSessions = new Map<string, ChatSession>();

export async function POST(request: NextRequest) {
  try {
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { message, sessionId, model = "ocean-core" } = body;

    if (!message) {
      return NextResponse.json(
        { error: "Message is required" },
        { status: 400 },
      );
    }

    // Get or create session
    let session: ChatSession;
    const sessionKey = `${userId}-${sessionId || "default"}`;

    if (chatSessions.has(sessionKey)) {
      session = chatSessions.get(sessionKey)!;
    } else {
      session = {
        id: sessionId || crypto.randomUUID(),
        title: message.substring(0, 50) + (message.length > 50 ? "..." : ""),
        messages: [],
        model: model,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    }

    // Add user message
    const userMessage: ChatMessage = {
      role: "user",
      content: message,
      timestamp: new Date().toISOString(),
    };
    session.messages.push(userMessage);

    // Query Ocean Core
    let assistantContent: string;

    try {
      const response = await fetch(`${OCEAN_CORE_URL}/api/v1/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: message,
          context: session.messages.slice(-10).map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        assistantContent =
          data.response || data.answer || "I'm processing your request...";
      } else {
        assistantContent =
          "I'm having trouble connecting to Ocean Core. Please try again.";
      }
    } catch {
      // Fallback response
      assistantContent =
        "Ocean Core is currently unavailable. Your message has been saved.";
    }

    // Add assistant message
    const assistantMessage: ChatMessage = {
      role: "assistant",
      content: assistantContent,
      timestamp: new Date().toISOString(),
    };
    session.messages.push(assistantMessage);

    // Update session
    session.updatedAt = new Date().toISOString();
    chatSessions.set(sessionKey, session);

    // Save to database (async, don't wait)
    saveChatToDatabase(userId, session).catch(console.error);

    return NextResponse.json({
      sessionId: session.id,
      message: assistantMessage,
      title: session.title,
    });
  } catch (error) {
    console.error("Chat error:", error);
    return NextResponse.json(
      { error: "Failed to process chat" },
      { status: 500 },
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get("sessionId");

    if (sessionId) {
      // Get specific session
      const sessionKey = `${userId}-${sessionId}`;
      const session = chatSessions.get(sessionKey);

      if (!session) {
        return NextResponse.json(
          { error: "Session not found" },
          { status: 404 },
        );
      }

      return NextResponse.json(session);
    }

    // Get all sessions for user
    const userSessions: ChatSession[] = [];
    chatSessions.forEach((session, key) => {
      if (key.startsWith(`${userId}-`)) {
        userSessions.push({
          ...session,
          messages: [], // Don't include full messages in list
        });
      }
    });

    // Sort by updatedAt descending
    userSessions.sort(
      (a, b) =>
        new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
    );

    return NextResponse.json({
      sessions: userSessions.slice(0, 50), // Limit to 50 sessions
    });
  } catch (error) {
    console.error("Get chat error:", error);
    return NextResponse.json(
      { error: "Failed to get chat history" },
      { status: 500 },
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get("sessionId");

    if (!sessionId) {
      return NextResponse.json(
        { error: "Session ID required" },
        { status: 400 },
      );
    }

    const sessionKey = `${userId}-${sessionId}`;

    if (chatSessions.has(sessionKey)) {
      chatSessions.delete(sessionKey);
      return NextResponse.json({ deleted: true });
    }

    return NextResponse.json({ error: "Session not found" }, { status: 404 });
  } catch (error) {
    console.error("Delete chat error:", error);
    return NextResponse.json(
      { error: "Failed to delete chat" },
      { status: 500 },
    );
  }
}

async function saveChatToDatabase(userId: string, session: ChatSession) {
  try {
    await fetch(`${API_URL}/internal/save-chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Internal-Key": process.env.INTERNAL_API_KEY || "internal-secret",
      },
      body: JSON.stringify({
        userId,
        session,
      }),
    });
  } catch (error) {
    console.error("Failed to save chat to database:", error);
  }
}


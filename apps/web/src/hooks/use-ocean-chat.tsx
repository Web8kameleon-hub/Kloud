/**
 * useOceanChat - Hook për komunikim me Ocean API
 * 
 * Automatikisht dërgon Clerk user ID me çdo request
 * për personalizim të përgjigjeve.
 * 
 * @author Ledjan Ahmati
 * @copyright 2026 Kloud Cloud
 */

import { useAuth, useUser } from "@clerk/nextjs";
import { useCallback, useState } from "react";

const OCEAN_API_URL = process.env.NEXT_PUBLIC_OCEAN_API_URL || "http://localhost:8030";

interface OceanMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface OceanResponse {
  response: string;
  sources?: string[];
  confidence?: number;
  language?: string;
}

interface UseOceanChatResult {
  messages: OceanMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (message: string) => Promise<void>;
  clearMessages: () => void;
}

export function useOceanChat(): UseOceanChatResult {
  const { userId } = useAuth();
  const { user } = useUser();
  const [messages, setMessages] = useState<OceanMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;

    setIsLoading(true);
    setError(null);

    // Add user message immediately
    const userMessage: OceanMessage = {
      role: "user",
      content: message,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      // Build request with user context
      const requestBody: Record<string, unknown> = {
        message: message,
        query: message,
      };

      // Add Clerk user ID if authenticated
      if (userId) {
        requestBody.clerk_user_id = userId;
        requestBody.user_name = user?.firstName || user?.username || undefined;
        requestBody.user_language = user?.unsafeMetadata?.language || "sq";
      }

      const response = await fetch(`${OCEAN_API_URL}/api/v1/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Add clerk token for backend verification
          ...(userId && { "X-Clerk-User-Id": userId }),
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`Ocean API error: ${response.status}`);
      }

      const data: OceanResponse = await response.json();

      // Add assistant response
      const assistantMessage: OceanMessage = {
        role: "assistant",
        content: data.response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Gabim i panjohur";
      setError(errorMessage);
      
      // Add error message as assistant response
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `❌ ${errorMessage}. Ju lutem provoni përsëri.`,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [userId, user]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
  };
}

/**
 * Hook për të marrë informacionin e userit për Ocean
 */
export function useOceanUserContext() {
  const { userId, isSignedIn } = useAuth();
  const { user } = useUser();

  return {
    isAuthenticated: isSignedIn,
    userId: userId,
    userName: user?.firstName || user?.username || null,
    userEmail: user?.primaryEmailAddress?.emailAddress || null,
    userLanguage: (user?.unsafeMetadata?.language as string) || "sq",
    userPlan: (user?.publicMetadata?.plan as string) || "free",
    isAdmin: user?.publicMetadata?.role === "admin",
  };
}


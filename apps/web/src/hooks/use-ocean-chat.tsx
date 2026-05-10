/**
 * useOceanChat - Hook për komunikim me Ocean API
 * 
 * Automatikisht dërgon internal auth context (token / user)
 * për personalizim të përgjigjeve pa varësi nga Clerk.
 * 
 * @author Ledjan Ahmati
 * @copyright 2026 Kloud Cloud
 */

import { useCallback, useState } from "react";

const OCEAN_API_URL = process.env.NEXT_PUBLIC_OCEAN_API_URL || "http://localhost:8030";

type InternalAuthContext = {
  isAuthenticated: boolean;
  token: string | null;
  userId: string | null;
  userName: string | null;
  userEmail: string | null;
  userLanguage: string;
  userPlan: string;
  isAdmin: boolean;
};

function readInternalAuthContext(): InternalAuthContext {
  if (typeof window === "undefined") {
    return {
      isAuthenticated: false,
      token: null,
      userId: null,
      userName: null,
      userEmail: null,
      userLanguage: "sq",
      userPlan: "free",
      isAdmin: false,
    };
  }

  const token =
    window.localStorage.getItem("kloud_auth_token") ||
    window.sessionStorage.getItem("kloud_auth_token");

  const userId =
    window.localStorage.getItem("kloud_user_id") ||
    window.sessionStorage.getItem("kloud_user_id");

  const userName =
    window.localStorage.getItem("kloud_user_name") ||
    window.sessionStorage.getItem("kloud_user_name");

  const userEmail =
    window.localStorage.getItem("kloud_user_email") ||
    window.sessionStorage.getItem("kloud_user_email");

  const userLanguage =
    window.localStorage.getItem("kloud_user_language") ||
    window.sessionStorage.getItem("kloud_user_language") ||
    "sq";

  const userPlan =
    window.localStorage.getItem("kloud_user_plan") ||
    window.sessionStorage.getItem("kloud_user_plan") ||
    "free";

  const role =
    window.localStorage.getItem("kloud_user_role") ||
    window.sessionStorage.getItem("kloud_user_role") ||
    "user";

  return {
    isAuthenticated: Boolean(token || userId),
    token,
    userId,
    userName,
    userEmail,
    userLanguage,
    userPlan,
    isAdmin: role === "admin",
  };
}

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
      const authContext = readInternalAuthContext();

      // Build request with user context
      const requestBody: Record<string, unknown> = {
        message: message,
        query: message,
      };

      if (authContext.userId) {
        requestBody.user_id = authContext.userId;
      }
      if (authContext.userName) {
        requestBody.user_name = authContext.userName;
      }
      if (authContext.userEmail) {
        requestBody.user_email = authContext.userEmail;
      }
      requestBody.user_language = authContext.userLanguage;

      const response = await fetch(`${OCEAN_API_URL}/api/v1/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Auth-Mode": "internal",
          ...(authContext.userId && { "X-Kloud-User-Id": authContext.userId }),
          ...(authContext.token && {
            Authorization: `Bearer ${authContext.token}`,
          }),
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
  }, []);

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
  const authContext = readInternalAuthContext();

  return {
    isAuthenticated: authContext.isAuthenticated,
    userId: authContext.userId,
    userName: authContext.userName,
    userEmail: authContext.userEmail,
    userLanguage: authContext.userLanguage,
    userPlan: authContext.userPlan,
    isAdmin: authContext.isAdmin,
  };
}


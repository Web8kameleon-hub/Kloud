'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { Send, Sparkles, RefreshCw, ChevronRight, Loader2, Mic, Camera, FileText, X, Square, Plus, Settings2, ArrowLeft, Volume2, VolumeX } from 'lucide-react';

// Clerk — safe runtime access (no hooks, avoids ClerkProvider requirement)
function getClerkUser(): { userId: string | null; firstName: string | null; username: string | null } {
  try {
    // Access Clerk's client-side singleton if available
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w = window as any;
    if (w?.Clerk?.user) {
      const u = w.Clerk.user;
      return { userId: u.id || null, firstName: u.firstName || null, username: u.username || null };
    }
    if (w?.Clerk?.session?.user) {
      const u = w.Clerk.session.user;
      return { userId: u.id || null, firstName: u.firstName || null, username: u.username || null };
    }
  } catch {
    // Clerk not available
  }
  return { userId: null, firstName: null, username: null };
}

/**
 * CURIOSITY OCEAN — Ultra-Modern AI Chat
 * Clean, minimal, powerful. Streaming + Multimodal.
 */

// ============================================================================
// TRANSLATIONS
// ============================================================================
const translations: Record<string, {
  welcome: string;
  chatCleared: string;
  modules: string;
  title: string;
  subtitle: string;
  streaming: string;
  normal: string;
  curious: string;
  wild: string;
  chaos: string;
  genius: string;
  tryAsking: string;
  askAnything: string;
  thinking: string;
  streamingIndicator: string;
  exploreFurther: string;
  continueWith: string;
  stopButton: string;
  capture: string;
  switchCam: string;
  close: string;
}> = {
  en: {
    welcome: "Hi! I'm Curiosity Ocean — ask me anything and let's explore the depths of knowledge together. What sparks your curiosity today?",
    chatCleared: "Chat cleared! Ready for new explorations. What would you like to discover?",
    modules: "Modules",
    title: "Curiosity Ocean",
    subtitle: "Infinite Knowledge Engine",
    streaming: "Stream",
    normal: "Normal",
    curious: "Curious",
    wild: "Wild",
    chaos: "Chaos",
    genius: "Genius",
    tryAsking: "Try asking",
    askAnything: "Ask anything...",
    thinking: "Thinking",
    streamingIndicator: "streaming...",
    exploreFurther: "Explore further",
    continueWith: "Continue with",
    stopButton: "Stop",
    capture: "Capture",
    switchCam: "Switch",
    close: "Close",
  },
  sq: {
    welcome: "Përshëndetje! Jam Curiosity Ocean — më pyet çdo gjë dhe le të eksplorojmë thellësitë e dijes së bashku. Çfarë ngjall kuriozitetin tënd sot?",
    chatCleared: "Biseda u pastrua! Gati për eksplorime të reja. Çfarë dëshiron të zbulosh?",
    modules: "Module",
    title: "Curiosity Ocean",
    subtitle: "Motor i Dijes së Pakufishme",
    streaming: "Stream",
    normal: "Normal",
    curious: "Kurioz",
    wild: "I egër",
    chaos: "Kaos",
    genius: "Gjeni",
    tryAsking: "Provo të pyesësh",
    askAnything: "Pyet çdo gjë...",
    thinking: "Duke menduar",
    streamingIndicator: "duke transmetuar...",
    exploreFurther: "Eksploro më shumë",
    continueWith: "Vazhdo me",
    stopButton: "Ndalo",
    capture: "Kap",
    switchCam: "Ndrysho",
    close: "Mbyll",
  },
  de: {
    welcome: "Willkommen bei Curiosity Ocean! Frag mich alles und lass uns gemeinsam die Tiefen des Wissens erkunden. Was weckt deine Neugier heute?",
    chatCleared: "Chat gelöscht! Bereit für neue Erkundungen. Was möchtest du entdecken?",
    modules: "Module",
    title: "Curiosity Ocean",
    subtitle: "Unendliche Wissens-Engine",
    streaming: "Stream",
    normal: "Normal",
    curious: "Neugierig",
    wild: "Wild",
    chaos: "Chaos",
    genius: "Genie",
    tryAsking: "Versuch zu fragen",
    askAnything: "Frag was du willst...",
    thinking: "Denke nach",
    streamingIndicator: "streaming...",
    exploreFurther: "Weiter erkunden",
    continueWith: "Weiter mit",
    stopButton: "Stopp",
    capture: "Aufnehmen",
    switchCam: "Wechseln",
    close: "Schließen",
  },
  es: {
    welcome: "¡Bienvenido a Curiosity Ocean! Pregúntame lo que sea y exploremos juntos las profundidades del conocimiento. ¿Qué despierta tu curiosidad hoy?",
    chatCleared: "¡Chat borrado! Listo para nuevas exploraciones. ¿Qué quieres descubrir?",
    modules: "Módulos",
    title: "Curiosity Ocean",
    subtitle: "Motor de Conocimiento Infinito",
    streaming: "Stream",
    normal: "Normal",
    curious: "Curioso",
    wild: "Salvaje",
    chaos: "Caos",
    genius: "Genio",
    tryAsking: "Intenta preguntar",
    askAnything: "Pregunta lo que sea...",
    thinking: "Pensando",
    streamingIndicator: "transmitiendo...",
    exploreFurther: "Explorar más",
    continueWith: "Continuar con",
    stopButton: "Parar",
    capture: "Capturar",
    switchCam: "Cambiar",
    close: "Cerrar",
  },
  fr: {
    welcome: "Bienvenue sur Curiosity Ocean! Pose-moi n'importe quelle question et explorons ensemble les profondeurs du savoir. Qu'est-ce qui éveille ta curiosité aujourd'hui?",
    chatCleared: "Chat effacé! Prêt pour de nouvelles explorations. Que veux-tu découvrir?",
    modules: "Modules",
    title: "Curiosity Ocean",
    subtitle: "Moteur de Connaissance Infinie",
    streaming: "Stream",
    normal: "Normal",
    curious: "Curieux",
    wild: "Sauvage",
    chaos: "Chaos",
    genius: "Génie",
    tryAsking: "Essaye de demander",
    askAnything: "Demande n'importe quoi...",
    thinking: "Je réfléchis",
    streamingIndicator: "diffusion...",
    exploreFurther: "Explorer plus",
    continueWith: "Continuer avec",
    stopButton: "Arrêter",
    capture: "Capturer",
    switchCam: "Changer",
    close: "Fermer",
  },
  it: {
    welcome: "Benvenuto su Curiosity Ocean! Chiedimi qualsiasi cosa ed esploriamo insieme le profondità della conoscenza. Cosa suscita la tua curiosità oggi?",
    chatCleared: "Chat cancellata! Pronto per nuove esplorazioni. Cosa vorresti scoprire?",
    modules: "Moduli",
    title: "Curiosity Ocean",
    subtitle: "Motore di Conoscenza Infinita",
    streaming: "Stream",
    normal: "Normale",
    curious: "Curioso",
    wild: "Selvaggio",
    chaos: "Caos",
    genius: "Genio",
    tryAsking: "Prova a chiedere",
    askAnything: "Chiedi qualsiasi cosa...",
    thinking: "Sto pensando",
    streamingIndicator: "streaming...",
    exploreFurther: "Esplora di più",
    continueWith: "Continua con",
    stopButton: "Ferma",
    capture: "Cattura",
    switchCam: "Cambia",
    close: "Chiudi",
  },
  zh: {
    welcome: "欢迎来到Curiosity Ocean！问我任何问题，让我们一起探索知识的深度。今天什么激发了你的好奇心？",
    chatCleared: "聊天已清除！准备好新的探索。你想发现什么？",
    modules: "模块",
    title: "Curiosity Ocean",
    subtitle: "无限知识引擎",
    streaming: "流",
    normal: "普通",
    curious: "好奇",
    wild: "狂野",
    chaos: "混沌",
    genius: "天才",
    tryAsking: "试着问",
    askAnything: "问任何问题...",
    thinking: "思考中",
    streamingIndicator: "流媒体...",
    exploreFurther: "深入探索",
    continueWith: "继续",
    stopButton: "停止",
    capture: "拍摄",
    switchCam: "切换",
    close: "关闭",
  },
  ja: {
    welcome: "Curiosity Oceanへようこそ！何でも聞いてください。一緒に知識の深みを探検しましょう。今日は何があなたの好奇心をかきたてますか？",
    chatCleared: "チャットがクリアされました！新しい探検の準備ができました。何を発見したいですか？",
    modules: "モジュール",
    title: "Curiosity Ocean",
    subtitle: "無限の知識エンジン",
    streaming: "ストリーム",
    normal: "通常",
    curious: "好奇心",
    wild: "ワイルド",
    chaos: "カオス",
    genius: "天才",
    tryAsking: "質問してみてください",
    askAnything: "何でも聞いてください...",
    thinking: "考え中",
    streamingIndicator: "ストリーミング中...",
    exploreFurther: "さらに探る",
    continueWith: "続ける",
    stopButton: "停止",
    capture: "撮影",
    switchCam: "切替",
    close: "閉じる",
  },
  ko: {
    welcome: "Curiosity Ocean에 오신 것을 환영합니다! 무엇이든 물어보세요. 함께 지식의 깊이를 탐험해 봅시다. 오늘 무엇이 당신의 호기심을 자극하나요?",
    chatCleared: "채팅이 삭제되었습니다! 새로운 탐험 준비가 되었습니다. 무엇을 발견하고 싶으신가요?",
    modules: "모듈",
    title: "Curiosity Ocean",
    subtitle: "무한 지식 엔진",
    streaming: "스트림",
    normal: "일반",
    curious: "호기심",
    wild: "와일드",
    chaos: "카오스",
    genius: "천재",
    tryAsking: "질문해 보세요",
    askAnything: "무엇이든 물어보세요...",
    thinking: "생각 중",
    streamingIndicator: "스트리밍...",
    exploreFurther: "더 탐구하기",
    continueWith: "계속하기",
    stopButton: "중지",
    capture: "촬영",
    switchCam: "전환",
    close: "닫기",
  },
};

function detectLanguage(): string {
  if (typeof window === 'undefined') return 'en';
  const browserLang = navigator.language.split('-')[0].toLowerCase();
  return translations[browserLang] ? browserLang : 'en';
}

const SUGGESTED_QUESTIONS: Record<string, string[]> = {
  en: [
    "What is consciousness?",
    "How does the brain process music?",
    "Explain quantum computing simply",
    "How does memory work?",
  ],
  sq: [
    "Çfarë është vetëdija?",
    "Si e përpunon truri muzikën?",
    "Shpjego kompjuterin kuantik thjesht",
    "Si funksionon kujtesa?",
  ],
  de: [
    "Was ist Bewusstsein?",
    "Wie verarbeitet das Gehirn Musik?",
    "Erkläre Quantencomputing einfach",
    "Wie funktioniert das Gedächtnis?",
  ],
  es: [
    "¿Qué es la consciencia?",
    "¿Cómo procesa el cerebro la música?",
    "Explica la computación cuántica simplemente",
    "¿Cómo funciona la memoria?",
  ],
  fr: [
    "Qu'est-ce que la conscience?",
    "Comment le cerveau traite-t-il la musique?",
    "Explique l'informatique quantique simplement",
    "Comment fonctionne la mémoire?",
  ],
  it: [
    "Cos'è la coscienza?",
    "Come elabora il cervello la musica?",
    "Spiega il calcolo quantistico semplicemente",
    "Come funziona la memoria?",
  ],
  zh: [
    "什么是意识？",
    "大脑如何处理音乐？",
    "简单解释量子计算",
    "记忆是如何工作的？",
  ],
  ja: [
    "意識とは何ですか？",
    "脳はどのように音楽を処理しますか？",
    "量子コンピューティングを簡単に説明してください",
    "記憶はどのように機能しますか？",
  ],
  ko: [
    "의식이란 무엇인가요?",
    "뇌는 음악을 어떻게 처리하나요?",
    "양자 컴퓨팅을 간단히 설명해주세요",
    "기억은 어떻게 작동하나요?",
  ],
};

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
  rabbitHoles?: string[];
  nextQuestions?: string[];
}

// ============================================================================
// COMPONENT
// ============================================================================
export default function CuriosityOceanChat() {
  // Clerk data — fetched safely via window.Clerk (no hooks needed)
  const [clerkUser, setClerkUser] = useState<{ userId: string | null; firstName: string | null; username: string | null }>({ userId: null, firstName: null, username: null });

  useEffect(() => {
    // Try immediately, then retry after Clerk loads
    const tryLoad = () => {
      const data = getClerkUser();
      if (data.userId) setClerkUser(data);
    };
    tryLoad();
    const timer = setTimeout(tryLoad, 1500);
    const timer2 = setTimeout(tryLoad, 3000);
    return () => { clearTimeout(timer); clearTimeout(timer2); };
  }, []);

  const userId = clerkUser.userId;
  const user = { firstName: clerkUser.firstName, username: clerkUser.username };
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [useStreaming, setUseStreaming] = useState(true);
  const [curiosityLevel, setCuriosityLevel] = useState<'curious' | 'wild' | 'chaos' | 'genius'>('curious');
  const [language, setLanguage] = useState('en');
  const [isRecording, setIsRecording] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('user');
  const [showAttachMenu, setShowAttachMenu] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const attachMenuRef = useRef<HTMLDivElement>(null);

  const t = translations[language] || translations.en;
  const suggestedQuestions = SUGGESTED_QUESTIONS[language] || SUGGESTED_QUESTIONS.en;

  const getAuthHeaders = useCallback(() => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (userId) headers['X-Clerk-User-Id'] = userId;
    return headers;
  }, [userId]);

  const scrollToBottom = useCallback((instant = false) => {
    messagesEndRef.current?.scrollIntoView({ behavior: instant ? 'instant' : 'smooth' });
  }, []);

  // Scroll on new messages (smooth), but NOT on every streaming chunk
  const prevMsgCountRef = useRef(0);
  useEffect(() => {
    if (messages.length !== prevMsgCountRef.current) {
      prevMsgCountRef.current = messages.length;
      scrollToBottom();
    }
  }, [messages, scrollToBottom]);
  useEffect(() => { setLanguage(detectLanguage()); }, []);

  useEffect(() => {
    const currentT = translations[language] || translations.en;
    setMessages([{ id: 'welcome', type: 'ai', content: currentT.welcome, timestamp: new Date() }]);
  }, [language]);

  // Close attach menu on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (attachMenuRef.current && !attachMenuRef.current.contains(e.target as Node)) {
        setShowAttachMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 120) + 'px';
    }
  }, [inputValue]);

  // ============================================================================
  // 🎤 MICROPHONE - Voice Conversation Pipeline
  // ============================================================================
  const [voiceMode, setVoiceMode] = useState(true); // true = full voice conversation
  
  const toggleRecording = async () => {
    setShowAttachMenu(false);
    if (isRecording) {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        const chunks: BlobPart[] = [];

        mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
        mediaRecorder.onstop = async () => {
          const blob = new Blob(chunks, { type: 'audio/webm' });
          const reader = new FileReader();
          reader.onloadend = async () => {
            const base64 = (reader.result as string).split(',')[1];
            const userMsgId = `user-${Date.now()}`;
            setMessages(prev => [...prev, { id: userMsgId, type: 'user', content: '🎤 Voice message...', timestamp: new Date() }]);
            
            try {
              if (voiceMode) {
                // 🔊 FULL VOICE CONVERSATION: Audio → STT → LLM → TTS → Audio
                const res = await fetch('/api/ocean/voice', {
                  method: 'POST',
                  headers: getAuthHeaders(),
                  body: JSON.stringify({ 
                    audio_base64: base64, 
                    language, 
                    curiosity_level: curiosityLevel,
                    clerk_user_id: userId 
                  })
                });
                
                if (res.ok) {
                  // Get metadata from headers
                  const transcript = res.headers.get('X-Transcript') || '';
                  const responseText = res.headers.get('X-Response-Text') || '';
                  
                  // Update user message with transcript
                  setMessages(prev => prev.map(m => 
                    m.id === userMsgId ? { ...m, content: `🎤 "${transcript}"` } : m
                  ));
                  
                  // Add AI response
                  const aiMsgId = `ai-${Date.now()}`;
                  setMessages(prev => [...prev, { 
                    id: aiMsgId, 
                    type: 'ai', 
                    content: responseText || 'Voice response received', 
                    timestamp: new Date() 
                  }]);
                  
                  // 🔊 Play audio response automatically
                  const audioBlob = await res.blob();
                  const audioUrl = URL.createObjectURL(audioBlob);
                  const audio = new Audio(audioUrl);
                  audioRef.current = audio;
                  setSpeakingMessageId(aiMsgId);
                  
                  audio.onended = () => {
                    setSpeakingMessageId(null);
                    URL.revokeObjectURL(audioUrl);
                    audioRef.current = null;
                  };
                  
                  await audio.play();
                } else {
                  throw new Error('Voice conversation failed');
                }
              } else {
                // 📝 TEXT ONLY: Audio → STT → Text response
                const res = await fetch('/api/ocean/audio', {
                  method: 'POST',
                  headers: getAuthHeaders(),
                  body: JSON.stringify({ audio_base64: base64, language, clerk_user_id: userId })
                });
                const data = await res.json();
                
                // Update user message with transcript
                setMessages(prev => prev.map(m => 
                  m.id === userMsgId ? { ...m, content: `🎤 "${data.transcript || 'Audio'}"` } : m
                ));
                
                // Send transcript to chat
                if (data.transcript) {
                  await sendMessage(data.transcript);
                }
              }
            } catch {
              setMessages(prev => [...prev, { id: `error-${Date.now()}`, type: 'ai', content: '❌ Error processing voice message', timestamp: new Date() }]);
            }
          };
          reader.readAsDataURL(blob);
          stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorderRef.current = mediaRecorder;
        mediaRecorder.start();
        setIsRecording(true);
      } catch {
        // Microphone access denied
      }
    }
  };

  // ============================================================================
  // 📷 CAMERA
  // ============================================================================
  const startCameraStream = async (mode: 'user' | 'environment') => {
    try {
      const video = videoRef.current;
      if (video?.srcObject) (video.srcObject as MediaStream).getTracks().forEach(track => track.stop());
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: mode } } });
      if (videoRef.current) videoRef.current.srcObject = stream;
    } catch {
      setShowCamera(false);
    }
  };

  const toggleCamera = async () => {
    setShowAttachMenu(false);
    if (showCamera) {
      const video = videoRef.current;
      if (video?.srcObject) (video.srcObject as MediaStream).getTracks().forEach(track => track.stop());
      setShowCamera(false);
    } else {
      setShowCamera(true);
      setTimeout(() => startCameraStream(facingMode), 100);
    }
  };

  const switchCamera = async () => {
    const newMode = facingMode === 'user' ? 'environment' : 'user';
    setFacingMode(newMode);
    if (showCamera) await startCameraStream(newMode);
  };

  const capturePhoto = async () => {
    const video = videoRef.current;
    if (!video) return;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d')?.drawImage(video, 0, 0);
    const base64 = canvas.toDataURL('image/jpeg').split(',')[1];

    setMessages(prev => [...prev, { id: `user-${Date.now()}`, type: 'user', content: '📷 Photo captured', timestamp: new Date() }]);

    try {
      const res = await fetch('/api/ocean/vision', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ image_base64: base64, prompt: language === 'sq' ? 'Përshkruaj këtë foto në shqip' : 'Describe this photo', clerk_user_id: userId })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { id: `ai-${Date.now()}`, type: 'ai', content: data.analysis || data.text_extracted || 'Image analyzed', timestamp: new Date() }]);
    } catch {
      setMessages(prev => [...prev, { id: `error-${Date.now()}`, type: 'ai', content: '❌ Error analyzing image', timestamp: new Date() }]);
    }
    toggleCamera();
  };

  // ============================================================================
  // 📄 DOCUMENT
  // ============================================================================
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) return;
    setShowAttachMenu(false);

    const ext = (file.name.split('.').pop() || '').toLowerCase();
    const isBinary = ['pdf', 'doc', 'docx'].includes(ext);

    setMessages(prev => [...prev, { id: `user-${Date.now()}`, type: 'user', content: `📄 ${file.name}`, timestamp: new Date() }]);

    const sendDocument = async (content: string, encoding: string) => {
      try {
        const res = await fetch('/api/ocean/document', {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({ content, encoding, action: 'summarize', doc_type: ext, filename: file.name, clerk_user_id: userId })
        });
        const data = await res.json();
        setMessages(prev => [...prev, { id: `ai-${Date.now()}`, type: 'ai', content: data.analysis || data.summary || 'Document analyzed', timestamp: new Date() }]);
      } catch {
        setMessages(prev => [...prev, { id: `error-${Date.now()}`, type: 'ai', content: '❌ Error processing document', timestamp: new Date() }]);
      }
    };

    if (isBinary) {
      const reader = new FileReader();
      reader.onloadend = async () => { await sendDocument((reader.result as string).split(',')[1], 'base64'); };
      reader.readAsDataURL(file);
    } else {
      const reader = new FileReader();
      reader.onloadend = async () => { await sendDocument(reader.result as string, 'text'); };
      reader.readAsText(file);
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // ============================================================================
  // STREAMING
  // ============================================================================
  const sendStreamingMessage = async (messageText: string) => {
    const aiMessageId = `ai-${Date.now()}`;
    setMessages(prev => [...prev, { id: aiMessageId, type: 'ai', content: '', timestamp: new Date(), isStreaming: true }]);
    setIsStreaming(true);

    try {
      abortControllerRef.current = new AbortController();
      const response = await fetch('/api/ocean/stream', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ message: messageText, language, clerk_user_id: userId, user_name: user?.firstName || user?.username }),
        signal: abortControllerRef.current.signal,
      });
      if (!response.ok) throw new Error('Stream failed');

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';
      let lastScroll = 0;

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          fullContent += decoder.decode(value, { stream: true });
          setMessages(prev => prev.map(msg => msg.id === aiMessageId ? { ...msg, content: fullContent } : msg));
          // Throttle scroll during streaming — max once per 80ms, instant (no smooth animation)
          const now = Date.now();
          if (now - lastScroll > 80) {
            lastScroll = now;
            scrollToBottom(true);
          }
        }
        // Final scroll after stream ends
        scrollToBottom(true);
      }
      setMessages(prev => prev.map(msg => msg.id === aiMessageId ? { ...msg, isStreaming: false } : msg));
    } catch (error) {
      if ((error as Error).name !== 'AbortError') {
        setMessages(prev => prev.map(msg => msg.id === aiMessageId ? { ...msg, content: 'Connection interrupted. Please try again.', isStreaming: false } : msg));
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  };

  // ============================================================================
  // REGULAR MESSAGE
  // ============================================================================
  const sendRegularMessage = async (messageText: string) => {
    try {
      const res = await fetch('/api/ocean', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ question: messageText, curiosityLevel, clerk_user_id: userId, user_name: user?.firstName || user?.username, language }),
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, {
          id: `ai-${Date.now()}`, type: 'ai',
          content: data.response || data.persona_answer || 'No response received',
          timestamp: new Date(), nextQuestions: data.curiosity_threads || [],
        }]);
      } else {
        setMessages(prev => [...prev, { id: `error-${Date.now()}`, type: 'ai', content: 'Service is processing. Please try again.', timestamp: new Date() }]);
      }
    } catch {
      setMessages(prev => [...prev, { id: `error-${Date.now()}`, type: 'ai', content: 'Connection interrupted. Please try again.', timestamp: new Date() }]);
    }
  };

  // ============================================================================
  // SEND / CONTROLS
  // ============================================================================
  const sendMessage = async (question?: string) => {
    const messageText = question || inputValue.trim();
    if (!messageText || isLoading || isStreaming) return;
    setMessages(prev => [...prev, { id: `user-${Date.now()}`, type: 'user', content: messageText, timestamp: new Date() }]);
    setInputValue('');
    setIsLoading(true);
    try {
      if (useStreaming) await sendStreamingMessage(messageText);
      else await sendRegularMessage(messageText);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const stopStreaming = () => { abortControllerRef.current?.abort(); };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  const clearChat = () => {
    setMessages([{ id: 'welcome', type: 'ai', content: t.chatCleared, timestamp: new Date() }]);
    setShowSettings(false);
  };

  // ============================================================================
  // 🔊 TEXT-TO-SPEECH (Server-Side Neural Voice)
  // ============================================================================
  const audioRef = useRef<HTMLAudioElement | null>(null);
  
  const speakMessage = async (messageId: string, text: string) => {
    // If already speaking this message, stop it
    if (speakingMessageId === messageId) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      window.speechSynthesis?.cancel();
      setSpeakingMessageId(null);
      return;
    }

    // Stop any ongoing speech
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    window.speechSynthesis?.cancel();
    
    setSpeakingMessageId(messageId);

    try {
      // Try server-side TTS first (higher quality neural voices)
      const response = await fetch('/api/ocean/tts', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ text, language })
      });

      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audioRef.current = audio;
        
        audio.onended = () => {
          setSpeakingMessageId(null);
          URL.revokeObjectURL(audioUrl);
          audioRef.current = null;
        };
        audio.onerror = () => {
          setSpeakingMessageId(null);
          audioRef.current = null;
          // Fallback to browser TTS
          fallbackBrowserTTS(text);
        };
        
        await audio.play();
        return;
      }
    } catch {
      // Server TTS failed, fallback to browser
    }

    // Fallback: Browser Speech Synthesis
    fallbackBrowserTTS(text);
  };

  const fallbackBrowserTTS = (text: string) => {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      setSpeakingMessageId(null);
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === 'sq' ? 'en-US' : language;
    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => 
      v.name.includes('Google') || v.name.includes('Microsoft') || v.name.includes('Natural')
    ) || voices.find(v => v.lang.startsWith(language)) || voices[0];
    
    if (preferredVoice) utterance.voice = preferredVoice;

    utterance.onend = () => setSpeakingMessageId(null);
    utterance.onerror = () => setSpeakingMessageId(null);

    window.speechSynthesis.speak(utterance);
  };

  // Load voices (they load async)
  useEffect(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.getVoices();
    }
  }, []);

  // ============================================================================
  // RENDER
  // ============================================================================
  return (
    <div className="h-screen flex flex-col bg-[#fafafa]">

      {/* ── Minimal Header ── */}
      <header className="flex-shrink-0 flex items-center justify-between px-4 sm:px-6 h-14 border-b border-gray-200/60 bg-white/80 backdrop-blur-xl z-10">
        <div className="flex items-center gap-3">
          <Link href="/modules" className="p-1.5 -ml-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-400 hover:text-gray-600">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-sm shadow-emerald-500/20">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div className="leading-tight hidden sm:block">
              <h1 className="text-sm font-semibold text-gray-900">{t.title}</h1>
              <p className="text-[11px] text-gray-400 font-normal">{t.subtitle}</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1">
          {/* Language — flag only */}
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="appearance-none bg-transparent border-none text-sm cursor-pointer focus:outline-none px-1"
            title="Language"
          >
            <option value="en">🇬🇧</option>
            <option value="sq">🇦🇱</option>
            <option value="de">🇩🇪</option>
            <option value="es">🇪🇸</option>
            <option value="fr">🇫🇷</option>
            <option value="it">🇮🇹</option>
            <option value="zh">🇨🇳</option>
            <option value="ja">🇯🇵</option>
            <option value="ko">🇰🇷</option>
          </select>

          {/* Settings gear */}
          <div className="relative">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className={`p-2 rounded-lg transition-colors ${showSettings ? 'bg-gray-100 text-gray-700' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'}`}
            >
              <Settings2 className="w-[18px] h-[18px]" />
            </button>

            {/* Settings dropdown */}
            {showSettings && (
              <div className="absolute right-0 top-full mt-2 w-60 bg-white rounded-2xl shadow-2xl shadow-gray-200/60 border border-gray-100 p-4 z-50 space-y-4">
                {/* Streaming */}
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-gray-600">Streaming</span>
                  <button
                    onClick={() => setUseStreaming(!useStreaming)}
                    className={`relative w-11 h-6 rounded-full transition-colors ${useStreaming ? 'bg-emerald-500' : 'bg-gray-200'}`}
                  >
                    <div className={`absolute top-1 w-4 h-4 rounded-full bg-white shadow-sm transition-all ${useStreaming ? 'left-6' : 'left-1'}`} />
                  </button>
                </div>

                <div className="h-px bg-gray-100" />

                {/* Curiosity level */}
                <div>
                  <span className="text-xs font-medium text-gray-600 block mb-2">Curiosity Level</span>
                  <div className="grid grid-cols-2 gap-1.5">
                    {(['curious', 'wild', 'chaos', 'genius'] as const).map(level => (
                      <button
                        key={level}
                        onClick={() => setCuriosityLevel(level)}
                        className={`text-xs px-3 py-2 rounded-xl transition-all capitalize ${
                          curiosityLevel === level
                            ? 'bg-emerald-50 text-emerald-700 font-semibold ring-1 ring-emerald-200'
                            : 'bg-gray-50 text-gray-500 hover:bg-gray-100'
                        }`}
                      >
                        {t[level]}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="h-px bg-gray-100" />

                {/* Clear */}
                <button
                  onClick={clearChat}
                  className="w-full text-xs text-gray-500 hover:text-red-500 hover:bg-red-50 rounded-xl py-2 transition-colors flex items-center justify-center gap-1.5"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Clear conversation
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* ── Messages ── */}
      <main className="flex-1 overflow-y-auto" onClick={() => { setShowSettings(false); setShowAttachMenu(false); }}>
        <div className="max-w-2xl mx-auto px-4 sm:px-6 py-6 space-y-5">
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[88%] sm:max-w-[80%]`}>
                {/* AI label */}
                {message.type === 'ai' && (
                  <div className="flex items-center gap-1.5 mb-1.5 ml-0.5">
                    <div className="w-5 h-5 rounded-md bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
                      <Sparkles className="w-3 h-3 text-white" />
                    </div>
                    <span className="text-[11px] font-medium text-gray-400">Ocean</span>
                    {message.isStreaming && (
                      <span className="text-[10px] text-emerald-500 animate-pulse ml-1">● {t.streamingIndicator}</span>
                    )}
                  </div>
                )}

                {/* Bubble */}
                <div
                  className={`rounded-2xl px-4 py-3 ${
                    message.type === 'user'
                      ? 'bg-emerald-600 text-white rounded-tr-md'
                      : 'bg-white text-gray-800 shadow-sm shadow-gray-100 border border-gray-100 rounded-tl-md'
                  }`}
                >
                  <div className="whitespace-pre-wrap text-[14.5px] leading-relaxed">{message.content}</div>

                  {/* 🔊 Speak Button (AI messages only) */}
                  {message.type === 'ai' && message.content && !message.isStreaming && (
                    <button
                      onClick={() => speakMessage(message.id, message.content)}
                      className={`mt-2 flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg transition-all ${
                        speakingMessageId === message.id
                          ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                          : 'text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 border border-transparent'
                      }`}
                      title={speakingMessageId === message.id ? 'Stop speaking' : 'Listen to response'}
                    >
                      {speakingMessageId === message.id ? (
                        <><VolumeX className="w-3.5 h-3.5" /><span>Stop</span></>
                      ) : (
                        <><Volume2 className="w-3.5 h-3.5" /><span>Listen</span></>
                      )}
                    </button>
                  )}

                  {/* Explore further */}
                  {message.rabbitHoles && message.rabbitHoles.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <p className="text-[11px] text-gray-400 mb-2 uppercase tracking-wider font-medium">{t.exploreFurther}</p>
                      <div className="space-y-0.5">
                        {message.rabbitHoles.map((hole, idx) => (
                          <button key={idx} onClick={() => sendMessage(hole)} className="flex items-center gap-1.5 w-full text-left text-sm text-gray-600 hover:text-emerald-600 hover:bg-emerald-50/50 rounded-lg px-2 py-1.5 transition-colors">
                            <ChevronRight className="w-3 h-3 flex-shrink-0 opacity-40" />
                            <span>{hole}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Next questions */}
                  {message.nextQuestions && message.nextQuestions.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <p className="text-[11px] text-gray-400 mb-2 uppercase tracking-wider font-medium">{t.continueWith}</p>
                      <div className="flex flex-wrap gap-1.5">
                        {message.nextQuestions.map((q, idx) => (
                          <button key={idx} onClick={() => sendMessage(q)} className="text-xs bg-gray-50 hover:bg-emerald-50 text-gray-600 hover:text-emerald-700 rounded-full px-3 py-1.5 transition-all border border-gray-100 hover:border-emerald-200">
                            {q}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Timestamp */}
                <div className={`mt-1 text-[10px] text-gray-300 ${message.type === 'user' ? 'text-right mr-1' : 'ml-1'}`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))}

          {/* Loading */}
          {isLoading && !isStreaming && (
            <div className="flex justify-start">
              <div>
                <div className="flex items-center gap-1.5 mb-1.5 ml-0.5">
                  <div className="w-5 h-5 rounded-md bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
                    <Sparkles className="w-3 h-3 text-white" />
                  </div>
                  <span className="text-[11px] font-medium text-gray-400">Ocean</span>
                </div>
                <div className="bg-white shadow-sm shadow-gray-100 border border-gray-100 rounded-2xl rounded-tl-md px-4 py-4">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                    <span className="text-xs text-gray-400">{t.thinking}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* ── Suggested Questions (welcome state) ── */}
      {messages.length <= 1 && (
        <div className="max-w-2xl mx-auto w-full px-4 sm:px-6 pb-3">
          <p className="text-xs text-gray-400 mb-2.5 font-medium">{t.tryAsking}</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {suggestedQuestions.map((q, idx) => (
              <button
                key={idx}
                onClick={() => sendMessage(q)}
                className="text-left text-sm text-gray-600 bg-white hover:bg-emerald-50 hover:text-emerald-700 rounded-xl px-4 py-3 transition-all border border-gray-100 hover:border-emerald-200 hover:shadow-sm"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ── Camera Overlay (fullscreen modal) ── */}
      {showCamera && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl overflow-hidden shadow-2xl max-w-sm w-full">
            <video ref={videoRef} autoPlay playsInline className="w-full aspect-[4/3] bg-gray-900 object-cover" />
            <div className="flex items-center justify-center gap-4 p-5">
              <button onClick={switchCamera} className="p-3 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors text-gray-600" title={t.switchCam}>
                <RefreshCw className="w-5 h-5" />
              </button>
              <button onClick={capturePhoto} className="p-5 bg-emerald-500 hover:bg-emerald-600 rounded-full transition-all text-white shadow-lg shadow-emerald-500/30 active:scale-95">
                <Camera className="w-6 h-6" />
              </button>
              <button onClick={toggleCamera} className="p-3 bg-gray-100 hover:bg-red-50 rounded-full transition-colors text-gray-600 hover:text-red-500" title={t.close}>
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Input Area ── */}
      <div className="flex-shrink-0 border-t border-gray-200/60 bg-white/80 backdrop-blur-xl">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 py-3">
          {/* Recording indicator */}
          {isRecording && (
            <div className="flex items-center gap-2.5 mb-3 px-4 py-2.5 bg-red-50 border border-red-100 rounded-xl">
              <div className="w-2.5 h-2.5 bg-red-500 rounded-full animate-pulse" />
              <span className="text-xs text-red-600 font-medium flex-1">Recording audio...</span>
              <button onClick={toggleRecording} className="text-xs text-red-500 hover:text-red-700 font-semibold transition-colors px-2 py-1 hover:bg-red-100 rounded-lg">
                {t.stopButton}
              </button>
            </div>
          )}

          <div className="relative flex items-end gap-2 bg-gray-50/80 border border-gray-200 rounded-2xl px-3 py-2 focus-within:border-emerald-300 focus-within:ring-2 focus-within:ring-emerald-500/10 focus-within:bg-white transition-all">
            {/* Attach (+) button */}
            <div className="relative flex-shrink-0 self-end" ref={attachMenuRef}>
              <button
                onClick={(e) => { e.stopPropagation(); setShowAttachMenu(!showAttachMenu); }}
                disabled={isLoading || isStreaming}
                className={`p-2 rounded-xl transition-all ${showAttachMenu ? 'bg-emerald-100 text-emerald-600' : 'hover:bg-gray-200/80 text-gray-400 hover:text-gray-600'}`}
              >
                <Plus className={`w-5 h-5 transition-transform duration-200 ${showAttachMenu ? 'rotate-45' : ''}`} />
              </button>

              {showAttachMenu && (
                <div className="absolute bottom-full left-0 mb-2 bg-white rounded-2xl shadow-2xl shadow-gray-200/50 border border-gray-100 py-2 z-50 min-w-[180px] overflow-hidden">
                  <button
                    onClick={toggleRecording}
                    className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center">
                      <Mic className="w-4 h-4 text-emerald-600" />
                    </div>
                    <span className="font-medium">Voice</span>
                  </button>
                  <button
                    onClick={toggleCamera}
                    className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
                      <Camera className="w-4 h-4 text-blue-600" />
                    </div>
                    <span className="font-medium">Camera</span>
                  </button>
                  <button
                    onClick={() => { setShowAttachMenu(false); fileInputRef.current?.click(); }}
                    className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-8 h-8 rounded-lg bg-purple-50 flex items-center justify-center">
                      <FileText className="w-4 h-4 text-purple-600" />
                    </div>
                    <span className="font-medium">Document</span>
                  </button>
                </div>
              )}
            </div>

            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              className="hidden"
              accept=".txt,.pdf,.doc,.docx,.md,.csv,.json"
            />

            {/* Text area */}
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={t.askAnything}
              rows={1}
              className="flex-1 bg-transparent border-none resize-none text-sm text-gray-900 placeholder-gray-400 focus:outline-none py-2 max-h-[120px] leading-relaxed"
              disabled={isLoading || isStreaming}
            />

            {/* Send / Stop */}
            <div className="flex-shrink-0 self-end">
              {isStreaming ? (
                <button onClick={stopStreaming} className="p-2 bg-red-500 hover:bg-red-600 rounded-xl transition-colors active:scale-95">
                  <Square className="w-4 h-4 text-white" />
                </button>
              ) : (
                <button
                  onClick={() => sendMessage()}
                  disabled={isLoading || !inputValue.trim()}
                  className="p-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-200 disabled:cursor-not-allowed rounded-xl transition-all active:scale-95"
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 text-white animate-spin" />
                  ) : (
                    <Send className="w-4 h-4 text-white" />
                  )}
                </button>
              )}
            </div>
          </div>

          <p className="text-center text-[10px] text-gray-300 mt-2 select-none">Curiosity Ocean by Kloud</p>
        </div>
      </div>
    </div>
  );
}


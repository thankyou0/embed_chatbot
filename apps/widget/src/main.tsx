import { render } from 'preact'
import { App } from './app'
import widgetStyles from './widget.css?inline'
import { widgetStyles as fallbackStyles } from './styles'

// #region agent log
fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.tsx:3',message:'widgetStyles imported',data:{type:typeof widgetStyles,isString:typeof widgetStyles==='string',hasDefault:!!(widgetStyles as any)?.default,contentLength:typeof widgetStyles==='string'?widgetStyles.length:((widgetStyles as any)?.default?.length||0),isUndefined:widgetStyles===undefined,isNull:widgetStyles===null},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
// #endregion

interface ChatbotConfig {
  chatbotId: string;
  apiUrl?: string; // Optional API URL override
  position?: 'bottom-right' | 'bottom-left';
  offsetX?: number;
  offsetY?: number;
  primaryColor?: string;
  headerText?: string;
  welcomeMessage?: string;
  initialSuggestions?: string[];
  avatarUrl?: string | null;
  showBranding?: boolean;
}

interface WidgetConfigResponse {
  primary_color: string;
  header_text: string;
  avatar_url: string | null;
  position: 'bottom-right' | 'bottom-left';
  offset_x: number;
  offset_y: number;
  welcome_message: string | null;
  initial_suggestions: string[];
  show_branding: boolean;
}

declare global {
  interface Window {
    ChatbotWidget: {
      init: (config: ChatbotConfig) => void;
    };
  }
}

const API_BASE_URL = import.meta.env.VITE_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchWidgetConfig(chatbotId: string, apiUrl?: string): Promise<WidgetConfigResponse | null> {
  const baseUrl = apiUrl || API_BASE_URL;
  try {
    // Add cache-busting query param to always get fresh config
    const cacheBuster = `?t=${Date.now()}`;
    const response = await fetch(`${baseUrl}/api/v1/chat/${chatbotId}/config${cacheBuster}`);
    if (response.ok) {
      return await response.json();
    }
    console.warn('Failed to fetch widget config, using defaults');
    return null;
  } catch (error) {
    console.warn('Error fetching widget config, using defaults:', error);
    return null;
  }
}

function injectStyles() {
  // #region agent log
  fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.tsx:58',message:'injectStyles called',data:{widgetStylesType:typeof widgetStyles,widgetStylesExists:widgetStyles!==undefined&&widgetStyles!==null},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
  // #endregion
  
  const styleId = 'chatbot-widget-styles';
  const existingStyle = document.getElementById(styleId);
  
  // #region agent log
  fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.tsx:62',message:'checking existing style',data:{styleId,existingStyleExists:!!existingStyle},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
  // #endregion
  
  if (!existingStyle) {
    const style = document.createElement('style');
    style.id = styleId;
    // In build mode with ?inline, it might be a string or { default: string }
    let cssText = typeof widgetStyles === 'string' ? widgetStyles : (widgetStyles as any)?.default;
    
    // Fallback to styles.ts if inline import failed (production build issue)
    if (!cssText || cssText.length === 0) {
      cssText = fallbackStyles;
    }
    
    // #region agent log
    fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.tsx:66',message:'cssText extracted',data:{cssTextType:typeof cssText,cssTextExists:!!cssText,cssTextLength:cssText?.length||0,cssTextPreview:cssText?.substring(0,100)||'N/A',usedFallback:!widgetStyles||(typeof widgetStyles!=='string'&&!(widgetStyles as any)?.default)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    
    if (cssText && cssText.length > 0) {
      style.textContent = cssText;
      document.head.appendChild(style);
      
      // #region agent log
      fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.tsx:72',message:'style element added to DOM',data:{styleElementId:style.id,styleInHead:!!document.head.querySelector('#'+styleId),styleTextLength:style.textContent?.length||0},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
      // #endregion
      
      console.log('Chatbot widget styles injected');
    } else {
      // #region agent log
      fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.tsx:76',message:'cssText is empty or falsy after fallback',data:{cssText, widgetStyles, fallbackStyles:fallbackStyles?.substring(0,50)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
      
      console.error('Failed to get chatbot widget styles - both inline and fallback failed');
    }
  }
}

async function initChatbotWidget(config: ChatbotConfig) {
  // #region agent log
  fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.tsx:75',message:'initChatbotWidget called',data:{chatbotId:config.chatbotId,apiUrl:config.apiUrl},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
  // #endregion
  
  // Inject styles immediately
  injectStyles();
  
  // #region agent log
  setTimeout(()=>{fetch('http://127.0.0.1:7246/ingest/3c40b17e-07a6-4ce0-b083-a3056da5f5f2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'main.tsx:80',message:'after injectStyles - verify DOM',data:{styleInDOM:!!document.getElementById('chatbot-widget-styles'),headStylesCount:document.head.querySelectorAll('style').length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});},100);
  // #endregion

  let container = document.getElementById('chatbot-widget-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'chatbot-widget-container';
    document.body.appendChild(container);
  }

  // Always fetch config from API to get latest appearance settings
  // This ensures changes in dashboard are reflected immediately on refresh
  const fetchedConfig = await fetchWidgetConfig(config.chatbotId, config.apiUrl);
  
  if (fetchedConfig) {
    // Merge fetched config with provided config (provided config takes precedence for overrides)
    const mergedConfig: ChatbotConfig = {
      ...config,
      position: config.position ?? fetchedConfig.position,
      offsetX: config.offsetX ?? fetchedConfig.offset_x,
      offsetY: config.offsetY ?? fetchedConfig.offset_y,
      primaryColor: config.primaryColor ?? fetchedConfig.primary_color,
      headerText: config.headerText ?? fetchedConfig.header_text,
      welcomeMessage: config.welcomeMessage ?? (fetchedConfig.welcome_message || undefined),
      initialSuggestions: config.initialSuggestions ?? fetchedConfig.initial_suggestions,
      avatarUrl: config.avatarUrl ?? fetchedConfig.avatar_url,
      showBranding: config.showBranding !== undefined ? config.showBranding : fetchedConfig.show_branding,
    };
    render(<App {...mergedConfig} />, container);
    return;
  }

  // Fallback to provided config or defaults if API fetch fails
  render(<App {...config} />, container);
}

// Expose the init function globally
window.ChatbotWidget = {
  init: initChatbotWidget,
};


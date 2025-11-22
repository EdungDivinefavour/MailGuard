// In browser, use relative paths when VITE_API_URL points to internal Docker hostname
// Browsers can't access internal Docker hostnames, so we rely on Vite proxy
// When running locally, use localhost directly
const getApiUrl = () => {
  // If we're in the browser
  if (typeof window !== 'undefined') {
    const envUrl = import.meta.env.VITE_API_URL
    
    // If no VITE_API_URL is set, use relative paths (will go through Vite proxy)
    if (!envUrl) {
      return ''
    }
    
    // If VITE_API_URL is localhost or 127.0.0.1, use it directly
    if (envUrl.includes('localhost') || envUrl.includes('127.0.0.1')) {
      return envUrl
    }
    
    // If VITE_API_URL points to an internal Docker hostname (like mailguard-server),
    // use relative paths so requests go through Vite proxy
    // The Vite proxy is configured to forward to VITE_API_URL
    if (envUrl.includes('mailguard-server') || envUrl.includes('://')) {
      return ''
    }
    
    // Default: use the env URL
    return envUrl
  }
  
  // Server-side (SSR) or build time - use env URL or default
  return import.meta.env.VITE_API_URL || 'http://localhost:5001'
}

export const API_URL = getApiUrl()


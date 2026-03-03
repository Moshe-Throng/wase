/**
 * Telegram Mini App SDK integration.
 * Handles init, theme, and auth data extraction.
 */

export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
}

// Access the global Telegram WebApp object
const tg = (window as any).Telegram?.WebApp;

export function getTelegram() {
  return tg;
}

export function initTelegram() {
  if (tg) {
    tg.ready();
    tg.expand();
  }
}

export function getInitData(): string {
  return tg?.initData || "";
}

export function getTelegramUser(): TelegramUser | null {
  const user = tg?.initDataUnsafe?.user;
  if (!user) return null;
  return {
    id: user.id,
    first_name: user.first_name,
    last_name: user.last_name,
    username: user.username,
    language_code: user.language_code,
  };
}

export function closeMiniApp() {
  tg?.close();
}

export function showAlert(message: string) {
  if (tg) {
    tg.showAlert(message);
  } else {
    alert(message);
  }
}

// Global app state: auth session + language (RTL/LTR).
import React, { createContext, useContext, useEffect, useState } from 'react';
import { I18nManager } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api, loadToken, setToken, User } from './api';
import { Lang } from './i18n';

interface AppState {
  user: User | null;
  lang: Lang;
  ready: boolean;
  needsOnboarding: boolean;
  setNeedsOnboarding: (v: boolean) => void;
  signIn: (token: string, user: User) => Promise<void>;
  signOut: () => Promise<void>;
  setLang: (l: Lang) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const Ctx = createContext<AppState>(null as unknown as AppState);
export const useApp = () => useContext(Ctx);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [lang, setLangState] = useState<Lang>('ar');
  const [ready, setReady] = useState(false);
  const [needsOnboarding, setNeedsOnboarding] = useState(false);

  useEffect(() => {
    (async () => {
      const stored = (await AsyncStorage.getItem('silver_lang')) as Lang | null;
      if (stored) setLangState(stored);
      const tok = await loadToken();
      if (tok) {
        try {
          const me = await api.get<{ user: User; interests: number[] }>('/me');
          setUser(me.user);
          setNeedsOnboarding(me.interests.length === 0);
        } catch {
          await setToken(null);
        }
      }
      setReady(true);
    })();
  }, []);

  const signIn = async (token: string, u: User) => {
    await setToken(token);
    setUser(u);
    try {
      const me = await api.get<{ interests: number[] }>('/me');
      setNeedsOnboarding(me.interests.length === 0);
    } catch {
      setNeedsOnboarding(false);
    }
  };

  const signOut = async () => {
    await setToken(null);
    setUser(null);
  };

  const setLang = async (l: Lang) => {
    setLangState(l);
    await AsyncStorage.setItem('silver_lang', l);
    // Full RTL flip requires an app reload; text alignment updates immediately.
    I18nManager.allowRTL(l === 'ar');
  };

  const refreshUser = async () => {
    try {
      const me = await api.get<{ user: User }>('/me');
      setUser(me.user);
    } catch {
      /* keep current */
    }
  };

  return (
    <Ctx.Provider
      value={{ user, lang, ready, needsOnboarding, setNeedsOnboarding, signIn, signOut, setLang, refreshUser }}
    >
      {children}
    </Ctx.Provider>
  );
}

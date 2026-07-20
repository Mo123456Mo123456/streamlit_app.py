// Login / registration.
import React, { useState } from 'react';
import { Alert, KeyboardAvoidingView, Platform, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { api, User } from '../api';
import { t } from '../i18n';
import { useApp } from '../state';
import { colors } from '../theme';
import { Btn, Card, Input } from '../components/ui';

export default function AuthScreen() {
  const { lang, setLang, signIn } = useApp();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [identifier, setIdentifier] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    setBusy(true);
    try {
      const r =
        mode === 'login'
          ? await api.post<{ token: string; user: User }>('/auth/login', { identifier, password })
          : await api.post<{ token: string; user: User }>('/auth/register', {
              username, email, password, display_name: displayName,
            });
      await signIn(r.token, r.user);
    } catch (e) {
      Alert.alert(t('error_generic', lang), e instanceof Error ? e.message : '');
    } finally {
      setBusy(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      style={styles.wrap}
    >
      <TouchableOpacity
        style={styles.langBtn}
        onPress={() => setLang(lang === 'ar' ? 'en' : 'ar')}
      >
        <Text style={{ color: colors.primary, fontWeight: '700' }}>
          {lang === 'ar' ? 'EN' : 'ع'}
        </Text>
      </TouchableOpacity>

      <View style={styles.logoWrap}>
        <View style={styles.logo}>
          <Text style={styles.logoS}>S</Text>
        </View>
        <Text style={styles.title}>
          Silver <Text style={{ color: colors.primary }}>سيلفر</Text>
        </Text>
        <Text style={styles.tagline}>{t('tagline', lang)}</Text>
      </View>

      <Card>
        <View style={styles.tabs}>
          {(['login', 'register'] as const).map((m) => (
            <TouchableOpacity
              key={m}
              onPress={() => setMode(m)}
              style={[styles.tab, mode === m && styles.tabActive]}
            >
              <Text style={[styles.tabText, mode === m && { color: '#fff' }]}>{t(m, lang)}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {mode === 'login' ? (
          <Input placeholder={t('identifier', lang)} value={identifier}
                 onChangeText={setIdentifier} autoCapitalize="none" />
        ) : (
          <>
            <Input placeholder={t('display_name', lang)} value={displayName}
                   onChangeText={setDisplayName} />
            <Input placeholder={t('username', lang)} value={username}
                   onChangeText={setUsername} autoCapitalize="none" />
            <Input placeholder={t('email', lang)} value={email} onChangeText={setEmail}
                   autoCapitalize="none" keyboardType="email-address" />
          </>
        )}
        <Input placeholder={t('password', lang)} value={password}
               onChangeText={setPassword} secureTextEntry />
        <Btn label={t(mode, lang)} onPress={submit} disabled={busy} />
      </Card>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg, justifyContent: 'center', padding: 20 },
  langBtn: { position: 'absolute', top: 60, right: 24 },
  logoWrap: { alignItems: 'center', marginBottom: 24 },
  logo: {
    width: 72, height: 72, borderRadius: 22, backgroundColor: colors.light,
    alignItems: 'center', justifyContent: 'center', marginBottom: 10,
  },
  logoS: { fontSize: 40, fontWeight: '900', color: colors.primary },
  title: { fontSize: 26, fontWeight: '800', color: colors.text },
  tagline: { color: colors.text2, marginTop: 4, textAlign: 'center' },
  tabs: { flexDirection: 'row', marginBottom: 14, backgroundColor: colors.light, borderRadius: 12 },
  tab: { flex: 1, paddingVertical: 10, alignItems: 'center', borderRadius: 12 },
  tabActive: { backgroundColor: colors.primary },
  tabText: { fontWeight: '700', color: colors.primary },
});

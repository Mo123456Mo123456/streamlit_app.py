// Settings: language, privacy (who can message), logout.
import React, { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { api } from '../api';
import { t } from '../i18n';
import { useApp } from '../state';
import { colors } from '../theme';
import { Btn, Card } from '../components/ui';

const WCM = ['everyone', 'followers', 'friends', 'nobody'] as const;

export default function SettingsScreen() {
  const { lang, setLang, signOut, user } = useApp();
  const [wcm, setWcm] = useState<string>('everyone');

  useEffect(() => {
    api.get<{ settings: { who_can_message: string } | null }>('/me')
      .then((r) => setWcm(r.settings?.who_can_message ?? 'everyone'))
      .catch(() => undefined);
  }, []);

  const saveWcm = async (value: string) => {
    setWcm(value);
    await api.put('/me/settings', { who_can_message: value }).catch(() => undefined);
  };

  const switchLang = async (l: 'ar' | 'en') => {
    await setLang(l);
    await api.put('/me/settings', { language: l }).catch(() => undefined);
  };

  return (
    <ScrollView style={styles.wrap} contentContainerStyle={{ padding: 16, paddingTop: 60 }}>
      <Text style={styles.title}>⚙️ {t('settings', lang)}</Text>
      <Card>
        <Text style={styles.label}>{t('language', lang)}</Text>
        <View style={{ flexDirection: 'row' }}>
          {(['ar', 'en'] as const).map((l) => (
            <TouchableOpacity key={l} onPress={() => switchLang(l)}
              style={[styles.chip, lang === l && styles.chipActive]}>
              <Text style={[styles.chipText, lang === l && { color: '#fff' }]}>
                {l === 'ar' ? 'العربية' : 'English'}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </Card>
      <Card>
        <Text style={styles.label}>{t('who_can_message', lang)}</Text>
        <View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
          {WCM.map((w) => (
            <TouchableOpacity key={w} onPress={() => saveWcm(w)}
              style={[styles.chip, wcm === w && styles.chipActive]}>
              <Text style={[styles.chipText, wcm === w && { color: '#fff' }]}>
                {t(`wcm_${w}`, lang)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </Card>
      <Card>
        <Text style={{ color: colors.text2, marginBottom: 10 }}>
          @{user?.username}
        </Text>
        <Btn kind="danger" label={`🚪 ${t('logout', lang)}`} onPress={signOut} />
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
  title: { fontSize: 22, fontWeight: '800', color: colors.text, marginBottom: 14 },
  label: { fontWeight: '700', color: colors.text, marginBottom: 8 },
  chip: {
    borderWidth: 1, borderColor: colors.border, backgroundColor: colors.card,
    borderRadius: 999, paddingHorizontal: 14, paddingVertical: 8, margin: 3,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  chipText: { color: colors.text, fontWeight: '600' },
});

// First-run: pick interests + city.
import React, { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { api, Category } from '../api';
import { t } from '../i18n';
import { useApp } from '../state';
import { colors } from '../theme';
import { Btn, Input } from '../components/ui';

export default function OnboardingScreen() {
  const { lang, setNeedsOnboarding, refreshUser } = useApp();
  const [cats, setCats] = useState<Category[]>([]);
  const [chosen, setChosen] = useState<Set<number>>(new Set());
  const [city, setCity] = useState('');

  useEffect(() => {
    api.get<Category[]>('/categories').then(setCats).catch(() => undefined);
  }, []);

  const toggle = (id: number) => {
    const next = new Set(chosen);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setChosen(next);
  };

  const submit = async () => {
    await api.put('/me/interests', { category_ids: [...chosen] });
    if (city.trim()) await api.put('/me', { city: city.trim() });
    await refreshUser();
    setNeedsOnboarding(false);
  };

  return (
    <ScrollView style={styles.wrap} contentContainerStyle={{ padding: 20, paddingTop: 70 }}>
      <Text style={styles.title}>{t('pick_interests', lang)}</Text>
      <View style={styles.grid}>
        {cats.map((c) => {
          const active = chosen.has(c.id);
          return (
            <TouchableOpacity
              key={c.id}
              onPress={() => toggle(c.id)}
              style={[styles.chip, active && styles.chipActive]}
            >
              <Text style={[styles.chipText, active && { color: '#fff' }]}>
                {lang === 'ar' ? c.name_ar : c.name_en}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
      <Input placeholder={t('your_city', lang)} value={city} onChangeText={setCity} />
      <Btn label={t('continue_', lang)} onPress={submit} disabled={chosen.size === 0} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
  title: { fontSize: 22, fontWeight: '800', color: colors.text, marginBottom: 16 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', marginBottom: 16 },
  chip: {
    backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1,
    borderRadius: 999, paddingHorizontal: 16, paddingVertical: 9, margin: 4,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  chipText: { color: colors.text, fontWeight: '600' },
});

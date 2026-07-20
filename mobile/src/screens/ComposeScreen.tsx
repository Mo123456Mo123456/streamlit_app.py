// Compose: adaptive post / story / go-live — with smart suggestions.
import React, { useEffect, useState } from 'react';
import { Alert, Image, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { api, Category, uploadFile } from '../api';
import { t } from '../i18n';
import { useApp } from '../state';
import { colors } from '../theme';
import { Btn, Card, Input, Muted } from '../components/ui';

const AUDIENCES = ['circle', 'front', 'interests', 'nearby'] as const;

interface Suggestion {
  section: string | null; category: string | null; keywords: string[]; warnings: string[];
}

export default function ComposeScreen({ navigation, route }: { navigation: any; route: any }) {
  const { lang } = useApp();
  const [mode, setMode] = useState<'post' | 'story' | 'live'>(route.params?.tab ?? 'post');
  const [body, setBody] = useState('');
  const [audiences, setAudiences] = useState<Set<string>>(new Set(['front']));
  const [cats, setCats] = useState<Category[]>([]);
  const [categoryId, setCategoryId] = useState<number | null>(null);
  const [aiGenerated, setAiGenerated] = useState(false);
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [storyAudience, setStoryAudience] = useState<'circle' | 'followers' | 'public'>('circle');
  const [liveTitle, setLiveTitle] = useState('');
  const [suggestion, setSuggestion] = useState<Suggestion | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.get<Category[]>('/categories').then(setCats).catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!body.trim()) { setSuggestion(null); return; }
    const timer = setTimeout(() => {
      api.post<Suggestion>('/assistant/suggest', { text: body }).then((s) => {
        setSuggestion(s);
        if (s.category && categoryId === null) {
          const match = cats.find((c) => c.slug === s.category);
          if (match) setCategoryId(match.id);
        }
      }).catch(() => undefined);
    }, 600);
    return () => clearTimeout(timer);
  }, [body, cats, categoryId]);

  const pickImage = async () => {
    const res = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.All, quality: 0.8,
    });
    if (!res.canceled && res.assets[0]) setImageUri(res.assets[0].uri);
  };

  const toggleAudience = (a: string) => {
    const next = new Set(audiences);
    if (next.has(a)) next.delete(a);
    else next.add(a);
    setAudiences(next);
  };

  const publish = async () => {
    setBusy(true);
    try {
      let mediaPaths: string[] = [];
      if (imageUri) {
        const name = imageUri.split('/').pop() ?? 'photo.jpg';
        const type = name.endsWith('.mp4') ? 'video/mp4' : 'image/jpeg';
        const up = await uploadFile(imageUri, name, type);
        mediaPaths = [up.path];
      }
      if (mode === 'post') {
        await api.post('/posts', {
          body: body.trim(),
          kind: mediaPaths.length ? (mediaPaths[0].endsWith('.mp4') ? 'video' : 'image') : 'text',
          audiences: [...audiences],
          category_id: categoryId,
          ai_generated: aiGenerated,
          media_paths: mediaPaths,
        });
      } else if (mode === 'story') {
        await api.post('/stories', {
          body: body.trim(), audience: storyAudience, media_path: mediaPaths[0] ?? '',
        });
      } else {
        const r = await api.post<{ id: number }>('/live', { title: liveTitle.trim() });
        navigation.navigate('Live', { streamId: r.id });
        setBusy(false);
        return;
      }
      setBody(''); setImageUri(null);
      navigation.navigate('HomeTab');
    } catch (e) {
      Alert.alert(t('error_generic', lang), e instanceof Error ? e.message : '');
    }
    setBusy(false);
  };

  return (
    <ScrollView style={styles.wrap} contentContainerStyle={{ padding: 16, paddingTop: 60 }}>
      <View style={styles.modes}>
        {(['post', 'story', 'live'] as const).map((m) => (
          <TouchableOpacity key={m} onPress={() => setMode(m)}
            style={[styles.mode, mode === m && styles.modeActive]}>
            <Text style={[styles.modeText, mode === m && { color: '#fff' }]}>
              {t(m === 'post' ? 'new_post' : m === 'story' ? 'story' : 'live', lang)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {mode !== 'live' ? (
        <Card>
          <Input
            placeholder={t('post_text', lang)} value={body} onChangeText={setBody}
            multiline style={{ minHeight: 100, textAlignVertical: 'top' }}
          />
          {suggestion && (
            <View style={styles.suggest}>
              <Text style={{ fontWeight: '700', color: colors.primary }}>
                ✨ {t('ai_suggest', lang)}
              </Text>
              {suggestion.section && <Muted>→ {t(`sec_${suggestion.section}`, lang)}</Muted>}
              {suggestion.keywords.length > 0 && <Muted>{suggestion.keywords.join(' · ')}</Muted>}
              {suggestion.warnings.map((w, i) => (
                <Text key={i} style={{ color: '#B45309', fontSize: 12 }}>⚠️ {w}</Text>
              ))}
            </View>
          )}
          <TouchableOpacity onPress={pickImage} style={styles.pick}>
            <Text style={{ color: colors.primary, fontWeight: '600' }}>📷 {t('pick_image', lang)}</Text>
          </TouchableOpacity>
          {imageUri && <Image source={{ uri: imageUri }} style={styles.preview} />}

          {mode === 'post' ? (
            <>
              <Text style={styles.label}>{t('choose_audiences', lang)}</Text>
              <View style={styles.chips}>
                {AUDIENCES.map((a) => (
                  <TouchableOpacity key={a} onPress={() => toggleAudience(a)}
                    style={[styles.chip, audiences.has(a) && styles.chipActive]}>
                    <Text style={[styles.chipText, audiences.has(a) && { color: '#fff' }]}>
                      {t(`sec_${a}`, lang)}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
              <Text style={styles.label}>{t('choose_category', lang)}</Text>
              <View style={styles.chips}>
                {cats.map((c) => (
                  <TouchableOpacity key={c.id}
                    onPress={() => setCategoryId(categoryId === c.id ? null : c.id)}
                    style={[styles.chip, categoryId === c.id && styles.chipActive]}>
                    <Text style={[styles.chipText, categoryId === c.id && { color: '#fff' }]}>
                      {lang === 'ar' ? c.name_ar : c.name_en}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
              <TouchableOpacity onPress={() => setAiGenerated(!aiGenerated)} style={styles.check}>
                <Text style={{ color: aiGenerated ? colors.primary : colors.text2 }}>
                  {aiGenerated ? '☑' : '☐'} {t('mark_ai', lang)}
                </Text>
              </TouchableOpacity>
            </>
          ) : (
            <>
              <Text style={styles.label}>{t('story_audience', lang)}</Text>
              <View style={styles.chips}>
                {(['circle', 'followers', 'public'] as const).map((a) => (
                  <TouchableOpacity key={a} onPress={() => setStoryAudience(a)}
                    style={[styles.chip, storyAudience === a && styles.chipActive]}>
                    <Text style={[styles.chipText, storyAudience === a && { color: '#fff' }]}>
                      {t(a === 'circle' ? 'aud_circle_only' : a === 'followers' ? 'aud_followers' : 'aud_public', lang)}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </>
          )}
          <Btn label={t('publish', lang)} onPress={publish}
               disabled={busy || (!body.trim() && !imageUri)} />
        </Card>
      ) : (
        <Card>
          <Muted>{t('live_note', lang)}</Muted>
          <View style={{ height: 10 }} />
          <Input placeholder={t('live_title', lang)} value={liveTitle} onChangeText={setLiveTitle} />
          <Btn label={`📡 ${t('start_live', lang)}`} onPress={publish}
               disabled={busy || !liveTitle.trim()} />
        </Card>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
  modes: { flexDirection: 'row', marginBottom: 14, backgroundColor: colors.card, borderRadius: 12 },
  mode: { flex: 1, paddingVertical: 10, alignItems: 'center', borderRadius: 12 },
  modeActive: { backgroundColor: colors.primary },
  modeText: { fontWeight: '700', color: colors.text },
  suggest: { backgroundColor: colors.light, borderRadius: 10, padding: 10, marginBottom: 10 },
  pick: { paddingVertical: 8 },
  preview: { width: '100%', height: 180, borderRadius: 12, marginBottom: 10 },
  label: { fontWeight: '700', color: colors.text, marginTop: 6, marginBottom: 6 },
  chips: { flexDirection: 'row', flexWrap: 'wrap', marginBottom: 8 },
  chip: {
    borderWidth: 1, borderColor: colors.border, backgroundColor: colors.card,
    borderRadius: 999, paddingHorizontal: 13, paddingVertical: 7, margin: 3,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  chipText: { color: colors.text, fontSize: 13, fontWeight: '600' },
  check: { paddingVertical: 8 },
});

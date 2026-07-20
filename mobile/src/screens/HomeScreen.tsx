// Home: story bar + the five social sections as swipeable tabs.
import React, { useCallback, useEffect, useState } from 'react';
import {
  Alert, FlatList, RefreshControl, ScrollView, StyleSheet, Text, TouchableOpacity, View,
} from 'react-native';
import { api, Post, Story } from '../api';
import { t } from '../i18n';
import { useApp } from '../state';
import { colors } from '../theme';
import PostCard from '../components/PostCard';
import StoryBar from '../components/StoryBar';
import { Muted } from '../components/ui';

const SECTIONS = ['circle', 'front', 'interests', 'communities', 'nearby'] as const;

export default function HomeScreen({ navigation }: { navigation: any }) {
  const { lang } = useApp();
  const [section, setSection] = useState<(typeof SECTIONS)[number]>('circle');
  const [posts, setPosts] = useState<Post[]>([]);
  const [stories, setStories] = useState<Story[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    setRefreshing(true);
    try {
      const [p, s] = await Promise.all([
        api.get<Post[]>(`/feed/${section}`),
        api.get<Story[]>('/stories'),
      ]);
      setPosts(p);
      setStories(s);
    } catch { /* offline */ }
    setRefreshing(false);
  }, [section]);

  useEffect(() => {
    load();
    const unsub = navigation.addListener('focus', load);
    return unsub;
  }, [load, navigation]);

  const openStories = async (authorId: number) => {
    const group = stories.filter((s) => s.author_id === authorId);
    for (const s of group) api.post(`/stories/${s.id}/view`).catch(() => undefined);
    const first = group[0];
    if (!first) return;
    Alert.alert(
      first.display_name,
      group.map((s) => s.body || '📷').join('\n———\n'),
      [
        { text: t('reply_story', lang), onPress: () => replyStory(authorId, first.id) },
        { text: 'OK' },
      ],
    );
    load();
  };

  const replyStory = async (authorId: number, storyId: number) => {
    try {
      const c = await api.post<{ id: number }>('/conversations', { user_id: authorId });
      navigation.navigate('Chat', { conversationId: c.id, storyId });
    } catch { /* cannot message */ }
  };

  return (
    <View style={styles.wrap}>
      <View style={styles.header}>
        <View style={styles.logo}><Text style={styles.logoS}>S</Text></View>
        <Text style={[styles.title, { flex: 1 }]}>
          Silver <Text style={{ color: colors.primary }}>سيلفر</Text>
        </Text>
        <TouchableOpacity onPress={() => navigation.navigate('Notifications')}
          style={{ marginEnd: 14 }}>
          <Text style={{ fontSize: 20 }}>🔔</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => navigation.navigate('Settings')}>
          <Text style={{ fontSize: 20 }}>⚙️</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={posts}
        keyExtractor={(p) => String(p.id)}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={load} />}
        ListHeaderComponent={
          <View>
            <StoryBar
              stories={stories}
              lang={lang}
              onAdd={() => navigation.navigate('Compose', { tab: 'story' })}
              onOpen={openStories}
            />
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tabs}>
              {SECTIONS.map((s) => (
                <TouchableOpacity
                  key={s}
                  onPress={() => setSection(s)}
                  style={[styles.tab, section === s && styles.tabActive]}
                >
                  <Text style={[styles.tabText, section === s && { color: '#fff' }]}>
                    {t(`sec_${s}`, lang)}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
            {posts.length === 0 && (
              <View style={{ padding: 24, alignItems: 'center' }}>
                <Muted>{t('no_posts', lang)}</Muted>
              </View>
            )}
          </View>
        }
        renderItem={({ item }) => (
          <PostCard
            post={item}
            lang={lang}
            onOpenProfile={(id) => navigation.navigate('Profile', { userId: id })}
          />
        )}
        contentContainerStyle={{ padding: 12 }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
  header: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: colors.card,
    paddingTop: 54, paddingBottom: 10, paddingHorizontal: 16,
  },
  logo: {
    width: 34, height: 34, borderRadius: 10, backgroundColor: colors.light,
    alignItems: 'center', justifyContent: 'center', marginEnd: 8,
  },
  logoS: { fontWeight: '900', fontSize: 20, color: colors.primary },
  title: { fontSize: 20, fontWeight: '800', color: colors.text },
  tabs: { marginBottom: 8 },
  tab: {
    paddingHorizontal: 16, paddingVertical: 8, borderRadius: 999,
    backgroundColor: colors.card, marginEnd: 8,
  },
  tabActive: { backgroundColor: colors.primary },
  tabText: { fontWeight: '700', color: colors.text },
});

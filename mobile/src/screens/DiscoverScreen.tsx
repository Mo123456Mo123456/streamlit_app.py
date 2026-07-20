// Discover: search, live-now, trending, suggested users & communities.
import React, { useCallback, useEffect, useState } from 'react';
import {
  FlatList, RefreshControl, StyleSheet, Text, TouchableOpacity, View,
} from 'react-native';
import { api, Community, Post, Stream, User } from '../api';
import { t } from '../i18n';
import { useApp } from '../state';
import { colors } from '../theme';
import PostCard from '../components/PostCard';
import { Avatar, Btn, Card, Input, Muted } from '../components/ui';

export default function DiscoverScreen({ navigation }: { navigation: any }) {
  const { lang } = useApp();
  const [q, setQ] = useState('');
  const [live, setLive] = useState<Stream[]>([]);
  const [trending, setTrending] = useState<Post[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [communities, setCommunities] = useState<Community[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    setRefreshing(true);
    try {
      if (q.trim()) {
        const r = await api.get<{ users: User[]; posts: Post[]; communities: Community[] }>(
          `/search?q=${encodeURIComponent(q.trim())}`);
        setUsers(r.users); setTrending(r.posts); setCommunities(r.communities); setLive([]);
      } else {
        const [l, tr, su, co] = await Promise.all([
          api.get<Stream[]>('/live'),
          api.get<Post[]>('/feed/trending'),
          api.get<User[]>('/users/suggested'),
          api.get<Community[]>('/communities'),
        ]);
        setLive(l); setTrending(tr); setUsers(su); setCommunities(co);
      }
    } catch { /* offline */ }
    setRefreshing(false);
  }, [q]);

  useEffect(() => {
    const timer = setTimeout(load, q ? 500 : 0);
    return () => clearTimeout(timer);
  }, [load, q]);

  const joinCommunity = async (id: number) => {
    await api.post(`/communities/${id}/join`).catch(() => undefined);
    load();
  };

  return (
    <View style={styles.wrap}>
      <View style={styles.header}>
        <Input placeholder={t('search_ph', lang)} value={q} onChangeText={setQ}
               style={{ marginBottom: 0 }} />
      </View>
      <FlatList
        data={trending}
        keyExtractor={(p) => `post_${p.id}`}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={load} />}
        contentContainerStyle={{ padding: 12 }}
        ListHeaderComponent={
          <View>
            {live.length > 0 && (
              <>
                <Text style={styles.section}>📡 {t('live_now', lang)}</Text>
                {live.map((s) => (
                  <TouchableOpacity key={s.id}
                    onPress={() => navigation.navigate('Live', { streamId: s.id })}>
                    <Card style={{ flexDirection: 'row', alignItems: 'center' }}>
                      <View style={styles.liveBadge}><Text style={styles.liveText}>LIVE</Text></View>
                      <View style={{ flex: 1, marginHorizontal: 10 }}>
                        <Text style={{ fontWeight: '700', color: colors.text }}>{s.title}</Text>
                        <Muted>{s.display_name} · {s.viewer_count} {t('viewers', lang)}</Muted>
                      </View>
                      <Text style={{ color: colors.primary, fontSize: 18 }}>▶</Text>
                    </Card>
                  </TouchableOpacity>
                ))}
              </>
            )}
            {users.length > 0 && (
              <>
                <Text style={styles.section}>👤 {t('suggested_users', lang)}</Text>
                {users.map((u) => (
                  <Card key={u.id} style={{ flexDirection: 'row', alignItems: 'center' }}>
                    <Avatar name={u.display_name} size={40} />
                    <TouchableOpacity style={{ flex: 1, marginHorizontal: 10 }}
                      onPress={() => navigation.navigate('Profile', { userId: u.id })}>
                      <Text style={{ fontWeight: '700', color: colors.text }}>{u.display_name}</Text>
                      <Muted>@{u.username}</Muted>
                    </TouchableOpacity>
                    <Btn small label={t('follow', lang)}
                         onPress={() => api.post(`/users/${u.id}/follow`).catch(() => undefined)} />
                  </Card>
                ))}
              </>
            )}
            {communities.length > 0 && (
              <>
                <Text style={styles.section}>👥 {t('communities', lang)}</Text>
                {communities.map((c) => (
                  <Card key={c.id} style={{ flexDirection: 'row', alignItems: 'center' }}>
                    <View style={{ flex: 1 }}>
                      <Text style={{ fontWeight: '700', color: colors.text }}>{c.name}</Text>
                      <Muted>{c.member_count ?? 0} {t('members', lang)}</Muted>
                    </View>
                    <Btn small label={t('join', lang)} onPress={() => joinCommunity(c.id)} />
                  </Card>
                ))}
              </>
            )}
            {trending.length > 0 && <Text style={styles.section}>🔥 {t('trending', lang)}</Text>}
          </View>
        }
        renderItem={({ item }) => (
          <PostCard post={item} lang={lang}
            onOpenProfile={(id) => navigation.navigate('Profile', { userId: id })} />
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
  header: { backgroundColor: colors.card, paddingTop: 54, paddingBottom: 10, paddingHorizontal: 12 },
  section: { fontWeight: '800', fontSize: 16, color: colors.text, marginVertical: 8 },
  liveBadge: { backgroundColor: colors.live, borderRadius: 6, paddingHorizontal: 8, paddingVertical: 2 },
  liveText: { color: '#fff', fontWeight: '800', fontSize: 11 },
});

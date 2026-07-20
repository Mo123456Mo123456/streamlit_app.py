// Profile: own account or another user's, with follow/message/block.
import React, { useCallback, useEffect, useState } from 'react';
import { Alert, FlatList, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { api, Post, User } from '../api';
import { t } from '../i18n';
import { useApp } from '../state';
import { colors } from '../theme';
import PostCard from '../components/PostCard';
import { Avatar, Btn, Card, Muted } from '../components/ui';

interface FullProfile extends User {
  followers: number;
  following: number;
  is_following: boolean;
  posts: Post[];
}

export default function ProfileScreen({ route, navigation }: { route: any; navigation: any }) {
  const { lang, user } = useApp();
  const userId: number = route.params?.userId ?? user?.id ?? 0;
  const own = userId === user?.id;
  const [profile, setProfile] = useState<FullProfile | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    setRefreshing(true);
    try {
      setProfile(await api.get<FullProfile>(`/users/${userId}`));
    } catch { /* gone */ }
    setRefreshing(false);
  }, [userId]);

  useEffect(() => {
    load();
    const unsub = navigation.addListener('focus', load);
    return unsub;
  }, [load, navigation]);

  if (!profile) return <View style={styles.wrap} />;

  const follow = async () => {
    await api.post(`/users/${userId}/follow`).catch(() => undefined);
    load();
  };

  const message = async () => {
    try {
      const c = await api.post<{ id: number }>('/conversations', { user_id: userId });
      navigation.navigate('Chat', { conversationId: c.id });
    } catch {
      Alert.alert(t('error_generic', lang));
    }
  };

  const block = () => {
    Alert.alert(t('block', lang), profile.display_name, [
      { text: t('block', lang), style: 'destructive',
        onPress: () => api.post(`/users/${userId}/block`).then(() => navigation.goBack()) },
      { text: 'إلغاء' },
    ]);
  };

  return (
    <FlatList
      style={styles.wrap}
      data={profile.posts}
      keyExtractor={(p) => String(p.id)}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={load} />}
      contentContainerStyle={{ padding: 12, paddingTop: 60 }}
      ListHeaderComponent={
        <Card>
          <View style={{ flexDirection: 'row', alignItems: 'center' }}>
            <Avatar name={profile.display_name} size={64} />
            <View style={{ flex: 1, marginHorizontal: 12 }}>
              <Text style={styles.name}>{profile.display_name}</Text>
              <Muted>@{profile.username}{profile.city ? ` · 📍 ${profile.city}` : ''}</Muted>
            </View>
          </View>
          {profile.bio ? <Text style={styles.bio}>{profile.bio}</Text> : null}
          <View style={styles.stats}>
            <Stat n={profile.followers} label={t('followers', lang)} />
            <Stat n={profile.following} label={t('following', lang)} />
            <Stat n={profile.posts.length} label={t('posts', lang)} />
          </View>
          {!own && (
            <View style={{ flexDirection: 'row', marginTop: 10 }}>
              <View style={{ flex: 1, marginEnd: 6 }}>
                <Btn small label={t(profile.is_following ? 'unfollow' : 'follow', lang)}
                     onPress={follow} kind={profile.is_following ? 'ghost' : 'primary'} />
              </View>
              <View style={{ flex: 1, marginEnd: 6 }}>
                <Btn small kind="ghost" label={`✉️ ${t('message_btn', lang)}`} onPress={message} />
              </View>
              <Btn small kind="danger" label="⛔" onPress={block} />
            </View>
          )}
        </Card>
      }
      renderItem={({ item }) => <PostCard post={item} lang={lang} />}
      ListEmptyComponent={
        <View style={{ padding: 24, alignItems: 'center' }}>
          <Muted>{t('no_posts', lang)}</Muted>
        </View>
      }
    />
  );
}

function Stat({ n, label }: { n: number; label: string }) {
  return (
    <View style={{ alignItems: 'center', flex: 1 }}>
      <Text style={{ fontWeight: '800', fontSize: 18, color: colors.text }}>{n}</Text>
      <Muted>{label}</Muted>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
  name: { fontSize: 19, fontWeight: '800', color: colors.text },
  bio: { color: colors.text, marginTop: 10 },
  stats: {
    flexDirection: 'row', marginTop: 12, borderTopWidth: 1,
    borderTopColor: colors.border, paddingTop: 10,
  },
});

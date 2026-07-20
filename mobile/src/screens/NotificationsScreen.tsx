// Notifications list.
import React, { useCallback, useEffect, useState } from 'react';
import { FlatList, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { api, Notification } from '../api';
import { relTime, t } from '../i18n';
import { useApp } from '../state';
import { colors } from '../theme';
import { Btn, Card, Muted } from '../components/ui';

const ICON: Record<string, string> = {
  follow: '👤', like: '💚', comment: '💬', message: '✉️', live: '📡',
  community: '👥', report: '🚩', security: '🔐',
};

export default function NotificationsScreen({ navigation }: { navigation: any }) {
  const { lang } = useApp();
  const [items, setItems] = useState<Notification[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    setRefreshing(true);
    try {
      const r = await api.get<{ items: Notification[] }>('/notifications');
      setItems(r.items);
    } catch { /* offline */ }
    setRefreshing(false);
  }, []);

  useEffect(() => {
    load();
    const unsub = navigation.addListener('focus', load);
    return unsub;
  }, [load, navigation]);

  return (
    <View style={styles.wrap}>
      <View style={styles.header}>
        <Text style={styles.title}>🔔 {t('notifications', lang)}</Text>
        <Btn small kind="ghost" label={t('mark_read', lang)}
          onPress={() => api.post('/notifications/read').then(load)} />
      </View>
      <FlatList
        data={items}
        keyExtractor={(n) => String(n.id)}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={load} />}
        contentContainerStyle={{ padding: 12 }}
        renderItem={({ item }) => (
          <Card style={{ flexDirection: 'row', alignItems: 'center', opacity: item.read ? 0.65 : 1 }}>
            <Text style={{ fontSize: 20, marginEnd: 10 }}>{ICON[item.kind] ?? '🔔'}</Text>
            <View style={{ flex: 1 }}>
              <Text style={{ color: colors.text }}>
                <Text style={{ fontWeight: '700' }}>{item.actor_name ?? ''} </Text>
                {t(`notif_${item.kind}`, lang)}
              </Text>
              <Muted>{relTime(item.created_at, lang)}</Muted>
            </View>
            {!item.read && <View style={styles.dot} />}
          </Card>
        )}
        ListEmptyComponent={
          <View style={{ padding: 24, alignItems: 'center' }}>
            <Muted>{t('no_notifications', lang)}</Muted>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
  header: {
    backgroundColor: colors.card, paddingTop: 54, paddingBottom: 10, paddingHorizontal: 16,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
  },
  title: { fontSize: 20, fontWeight: '800', color: colors.text },
  dot: { width: 10, height: 10, borderRadius: 5, backgroundColor: colors.primary },
});

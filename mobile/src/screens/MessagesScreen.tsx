// Conversation list + message requests.
import React, { useCallback, useEffect, useState } from 'react';
import { FlatList, RefreshControl, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { api, Conversation } from '../api';
import { t } from '../i18n';
import { useApp } from '../state';
import { colors } from '../theme';
import { Avatar, Btn, Card, Muted } from '../components/ui';

export default function MessagesScreen({ navigation }: { navigation: any }) {
  const { lang } = useApp();
  const [convs, setConvs] = useState<Conversation[]>([]);
  const [requests, setRequests] = useState<Conversation[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    setRefreshing(true);
    try {
      const [c, r] = await Promise.all([
        api.get<Conversation[]>('/conversations'),
        api.get<Conversation[]>('/conversations?requests=true'),
      ]);
      setConvs(c); setRequests(r);
    } catch { /* offline */ }
    setRefreshing(false);
  }, []);

  useEffect(() => {
    load();
    const unsub = navigation.addListener('focus', load);
    return unsub;
  }, [load, navigation]);

  const accept = async (id: number) => {
    await api.post(`/conversations/${id}/accept`).catch(() => undefined);
    load();
  };

  return (
    <View style={styles.wrap}>
      <View style={styles.header}>
        <Text style={styles.title}>💬 {t('messages', lang)}</Text>
      </View>
      <FlatList
        data={convs}
        keyExtractor={(c) => String(c.id)}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={load} />}
        contentContainerStyle={{ padding: 12 }}
        ListHeaderComponent={
          requests.length > 0 ? (
            <View>
              <Text style={styles.section}>📥 {t('message_requests', lang)}</Text>
              {requests.map((c) => (
                <Card key={c.id} style={{ flexDirection: 'row', alignItems: 'center' }}>
                  <Avatar name={c.peer?.display_name ?? '?'} size={40} />
                  <View style={{ flex: 1, marginHorizontal: 10 }}>
                    <Text style={{ fontWeight: '700', color: colors.text }}>
                      {c.peer?.display_name}
                    </Text>
                    <Muted>{c.last_body ?? ''}</Muted>
                  </View>
                  <Btn small label={t('accept', lang)} onPress={() => accept(c.id)} />
                </Card>
              ))}
            </View>
          ) : convs.length === 0 ? (
            <View style={{ padding: 24, alignItems: 'center' }}>
              <Muted>{t('no_conversations', lang)}</Muted>
            </View>
          ) : null
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            onPress={() => navigation.navigate('Chat', { conversationId: item.id })}>
            <Card style={{ flexDirection: 'row', alignItems: 'center' }}>
              <Avatar name={item.peer?.display_name ?? '?'} />
              <View style={{ flex: 1, marginHorizontal: 10 }}>
                <Text style={{ fontWeight: '700', color: colors.text }}>
                  {item.peer?.display_name}
                </Text>
                <Muted>{(item.last_body ?? '').slice(0, 50)}</Muted>
              </View>
              {item.unread > 0 && (
                <View style={styles.unread}>
                  <Text style={{ color: '#fff', fontSize: 11, fontWeight: '800' }}>{item.unread}</Text>
                </View>
              )}
            </Card>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
  header: { backgroundColor: colors.card, paddingTop: 54, paddingBottom: 10, paddingHorizontal: 16 },
  title: { fontSize: 20, fontWeight: '800', color: colors.text },
  section: { fontWeight: '800', color: colors.text, marginBottom: 8 },
  unread: {
    backgroundColor: colors.primary, borderRadius: 999, minWidth: 22, height: 22,
    alignItems: 'center', justifyContent: 'center', paddingHorizontal: 6,
  },
});

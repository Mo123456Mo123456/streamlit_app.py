// Live room: chat, guest requests, host controls (polling refresh).
import React, { useCallback, useEffect, useState } from 'react';
import { FlatList, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { api, Stream } from '../api';
import { t } from '../i18n';
import { useApp } from '../state';
import { colors } from '../theme';
import { Btn, Input, Muted } from '../components/ui';

export default function LiveScreen({ route, navigation }: { route: any; navigation: any }) {
  const { lang, user } = useApp();
  const streamId: number = route.params.streamId;
  const [stream, setStream] = useState<Stream | null>(null);
  const [text, setText] = useState('');

  const load = useCallback(async () => {
    try {
      setStream(await api.get<Stream>(`/live/${streamId}`));
    } catch { /* gone */ }
  }, [streamId]);

  useEffect(() => {
    load();
    const timer = setInterval(load, 4000);
    return () => clearInterval(timer);
  }, [load]);

  if (!stream) return <View style={styles.wrap} />;
  const isHost = stream.host_id === user?.id;
  const isLive = stream.status === 'live';

  const send = async () => {
    if (!text.trim()) return;
    const body = text.trim();
    setText('');
    await api.post(`/live/${streamId}/comments`, { body }).catch(() => undefined);
    load();
  };

  const requested = (stream.guests ?? []).filter((g) => g.status === 'requested');
  const approved = (stream.guests ?? []).filter((g) => g.status === 'approved');

  return (
    <View style={styles.wrap}>
      <View style={styles.stage}>
        <View style={styles.liveRow}>
          {isLive ? (
            <View style={styles.liveBadge}><Text style={styles.liveText}>LIVE</Text></View>
          ) : (
            <Text style={{ color: '#fff' }}>📼</Text>
          )}
          <Text style={styles.title} numberOfLines={1}>{stream.title}</Text>
        </View>
        <Text style={styles.host}>
          {stream.display_name} · 👁 {stream.viewer_count} {t('viewers', lang)}
        </Text>
        {approved.length > 0 && (
          <Text style={styles.guests}>🎙 {approved.map((g) => g.display_name).join('، ')}</Text>
        )}
        <Text style={styles.note}>{t('live_note', lang)}</Text>
        {isLive && !isHost && stream.guests_enabled ? (
          <Btn small kind="ghost" label={`🎙 ${t('join_as_guest', lang)}`}
            onPress={() => api.post(`/live/${streamId}/guest-request`).then(load).catch(() => undefined)} />
        ) : null}
        {isLive && isHost && (
          <View style={{ marginTop: 8 }}>
            {requested.map((g) => (
              <View key={g.user_id} style={styles.guestRow}>
                <Text style={{ color: '#fff', flex: 1 }}>{g.display_name}</Text>
                <Btn small label={t('accept', lang)}
                  onPress={() => api.post(`/live/${streamId}/guest-action`,
                    { user_id: g.user_id, status: 'approved' }).then(load)} />
                <View style={{ width: 6 }} />
                <Btn small kind="danger" label={t('reject', lang)}
                  onPress={() => api.post(`/live/${streamId}/guest-action`,
                    { user_id: g.user_id, status: 'rejected' }).then(load)} />
              </View>
            ))}
            <Btn kind="danger" label={`⏹ ${t('end_stream', lang)}`}
              onPress={() => api.post(`/live/${streamId}/end?keep_recording=true`)
                .then(() => navigation.goBack())} />
          </View>
        )}
      </View>

      <FlatList
        data={stream.comments ?? []}
        keyExtractor={(c) => String(c.id)}
        contentContainerStyle={{ padding: 12 }}
        renderItem={({ item }) => (
          <View style={styles.commentRow}>
            {item.pinned ? <Text>📌 </Text> : null}
            <Text style={{ color: colors.text }}>
              <Text style={{ fontWeight: '700' }}>{item.display_name}: </Text>
              {item.body}
            </Text>
          </View>
        )}
        ListEmptyComponent={<Muted>—</Muted>}
      />

      {isLive && stream.comments_enabled ? (
        <View style={styles.inputRow}>
          <Input value={text} onChangeText={setText} placeholder={t('type_message', lang)}
                 style={{ flex: 1, marginBottom: 0 }} onSubmitEditing={send} returnKeyType="send" />
          <TouchableOpacity onPress={send} style={styles.sendBtn}>
            <Text style={{ color: '#fff', fontWeight: '800' }}>➤</Text>
          </TouchableOpacity>
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
  stage: { backgroundColor: '#14232B', padding: 16, paddingTop: 20 },
  liveRow: { flexDirection: 'row', alignItems: 'center' },
  liveBadge: { backgroundColor: colors.live, borderRadius: 6, paddingHorizontal: 8, paddingVertical: 2 },
  liveText: { color: '#fff', fontWeight: '800', fontSize: 11 },
  title: { color: '#fff', fontWeight: '800', fontSize: 17, marginStart: 8, flex: 1 },
  host: { color: '#9FB3BC', marginTop: 6 },
  guests: { color: colors.primary, marginTop: 4 },
  note: { color: '#5E7681', fontSize: 11, marginVertical: 8 },
  guestRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  commentRow: { flexDirection: 'row', marginBottom: 6 },
  inputRow: {
    flexDirection: 'row', alignItems: 'center', padding: 10,
    backgroundColor: colors.card, borderTopWidth: 1, borderTopColor: colors.border,
  },
  sendBtn: {
    backgroundColor: colors.primary, width: 42, height: 42, borderRadius: 21,
    alignItems: 'center', justifyContent: 'center', marginStart: 8,
  },
});

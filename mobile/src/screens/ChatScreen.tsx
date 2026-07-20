// Single conversation — polls for new messages every few seconds.
import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  FlatList, KeyboardAvoidingView, Platform, StyleSheet, Text, TouchableOpacity, View,
} from 'react-native';
import { api, Message } from '../api';
import { t } from '../i18n';
import { useApp } from '../state';
import { colors } from '../theme';
import { Input } from '../components/ui';

export default function ChatScreen({ route }: { route: any }) {
  const { lang, user } = useApp();
  const conversationId: number = route.params.conversationId;
  const replyStoryId: number | undefined = route.params.storyId;
  const [messages, setMessages] = useState<Message[]>([]);
  const [text, setText] = useState('');
  const listRef = useRef<FlatList<Message>>(null);

  const load = useCallback(async () => {
    try {
      setMessages(await api.get<Message[]>(`/conversations/${conversationId}/messages`));
    } catch { /* offline */ }
  }, [conversationId]);

  useEffect(() => {
    load();
    const timer = setInterval(load, 4000);
    return () => clearInterval(timer);
  }, [load]);

  const send = async () => {
    if (!text.trim()) return;
    const body = text.trim();
    setText('');
    try {
      await api.post(`/conversations/${conversationId}/messages`, {
        body, story_id: replyStoryId ?? null,
      });
      await load();
      listRef.current?.scrollToEnd({ animated: true });
    } catch { /* cannot message */ }
  };

  return (
    <KeyboardAvoidingView
      style={styles.wrap}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={90}
    >
      <FlatList
        ref={listRef}
        data={messages}
        keyExtractor={(m) => String(m.id)}
        contentContainerStyle={{ padding: 12 }}
        renderItem={({ item }) => {
          const mine = item.sender_id === user?.id;
          return (
            <View style={[styles.bubble, mine ? styles.mine : styles.theirs]}>
              {item.story_id ? (
                <Text style={styles.storyRef}>↩️ {t('reply_story', lang)}</Text>
              ) : null}
              <Text style={{ color: mine ? '#fff' : colors.text }}>{item.body}</Text>
            </View>
          );
        }}
      />
      <View style={styles.inputRow}>
        <Input
          value={text} onChangeText={setText} placeholder={t('type_message', lang)}
          style={{ flex: 1, marginBottom: 0 }} onSubmitEditing={send} returnKeyType="send"
        />
        <TouchableOpacity onPress={send} style={styles.sendBtn}>
          <Text style={{ color: '#fff', fontWeight: '800' }}>➤</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.bg },
  bubble: { maxWidth: '80%', borderRadius: 16, padding: 10, marginBottom: 8 },
  mine: { backgroundColor: colors.primary, alignSelf: 'flex-end' },
  theirs: { backgroundColor: colors.card, alignSelf: 'flex-start' },
  storyRef: { fontSize: 11, opacity: 0.8, marginBottom: 2, color: colors.light },
  inputRow: {
    flexDirection: 'row', alignItems: 'center', padding: 10,
    backgroundColor: colors.card, borderTopWidth: 1, borderTopColor: colors.border,
  },
  sendBtn: {
    backgroundColor: colors.primary, width: 42, height: 42, borderRadius: 21,
    alignItems: 'center', justifyContent: 'center', marginStart: 8,
  },
});

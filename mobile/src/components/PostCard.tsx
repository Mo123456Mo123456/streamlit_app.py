// Post card with like / comment / save / report actions.
import React, { useState } from 'react';
import { Alert, Image, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { api, mediaUrl, Post } from '../api';
import { Lang, relTime, t } from '../i18n';
import { colors } from '../theme';
import { Avatar, Card, Input, Muted, Tag } from './ui';

const SECTION_KEY: Record<string, string> = {
  circle: 'sec_circle', front: 'sec_front', interests: 'sec_interests',
  communities: 'sec_communities', nearby: 'sec_nearby',
};

interface Comment { id: number; body: string; display_name: string }

export default function PostCard({
  post, lang, onOpenProfile,
}: {
  post: Post; lang: Lang; onOpenProfile?: (userId: number) => void;
}) {
  const [liked, setLiked] = useState(post.liked);
  const [likes, setLikes] = useState(post.likes);
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState<Comment[]>([]);
  const [commentText, setCommentText] = useState('');
  const [commentCount, setCommentCount] = useState(post.comment_count);

  const toggleLike = async () => {
    try {
      const r = await api.post<{ liked: boolean }>(`/posts/${post.id}/like`);
      setLiked(r.liked);
      setLikes((n) => n + (r.liked ? 1 : -1));
    } catch { /* offline */ }
  };

  const openComments = async () => {
    setShowComments((v) => !v);
    if (!showComments) {
      try {
        setComments(await api.get<Comment[]>(`/posts/${post.id}/comments`));
      } catch { /* ignore */ }
    }
  };

  const sendComment = async () => {
    if (!commentText.trim()) return;
    try {
      await api.post(`/posts/${post.id}/comments`, { body: commentText.trim() });
      setComments(await api.get<Comment[]>(`/posts/${post.id}/comments`));
      setCommentCount((n) => n + 1);
      setCommentText('');
    } catch { /* ignore */ }
  };

  const report = () => {
    Alert.alert(t('report', lang), '', [
      { text: t('reason_abuse', lang), onPress: () => sendReport('reason_abuse') },
      { text: t('reason_spam', lang), onPress: () => sendReport('reason_spam') },
      { text: t('reason_misinfo', lang), onPress: () => sendReport('reason_misinfo') },
      { text: t('reason_other', lang), onPress: () => sendReport('reason_other') },
    ]);
  };

  const sendReport = async (reason: string) => {
    try {
      await api.post('/reports', { target_kind: 'post', target_id: post.id, reason });
      Alert.alert(t('report_sent', lang));
    } catch { /* ignore */ }
  };

  return (
    <Card>
      <TouchableOpacity style={styles.header} onPress={() => onOpenProfile?.(post.author_id)}>
        <Avatar name={post.display_name} />
        <View style={{ flex: 1, marginHorizontal: 10 }}>
          <Text style={styles.name}>{post.display_name}</Text>
          <Muted>@{post.username} · {relTime(post.created_at, lang)}</Muted>
        </View>
        <TouchableOpacity onPress={report}>
          <Text style={{ color: colors.text2, fontSize: 18 }}>⋯</Text>
        </TouchableOpacity>
      </TouchableOpacity>

      <View style={styles.tags}>
        {post.audiences.map((a) => (
          <Tag key={a} label={t(SECTION_KEY[a] ?? 'sec_communities', lang)} />
        ))}
        {post.ai_generated ? <Tag label={`🤖 ${t('mark_ai', lang)}`} /> : null}
      </View>

      {post.body ? <Text style={styles.body}>{post.body}</Text> : null}
      {post.media.map((m, i) =>
        m.kind === 'image' ? (
          <Image key={i} source={{ uri: mediaUrl(m.url) }} style={styles.media} resizeMode="cover" />
        ) : (
          <View key={i} style={[styles.media, styles.videoPh]}>
            <Text style={{ color: '#fff', fontSize: 32 }}>▶</Text>
          </View>
        ),
      )}

      <View style={styles.actions}>
        <TouchableOpacity onPress={toggleLike} style={styles.action}>
          <Text style={{ fontSize: 16 }}>{liked ? '💚' : '🤍'} {likes}</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={openComments} style={styles.action}>
          <Text style={{ fontSize: 16 }}>💬 {commentCount}</Text>
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => api.post(`/posts/${post.id}/save`).catch(() => undefined)}
          style={styles.action}
        >
          <Text style={{ fontSize: 16 }}>🔖</Text>
        </TouchableOpacity>
      </View>

      {showComments && (
        <View style={styles.comments}>
          {comments.map((c) => (
            <Text key={c.id} style={styles.comment}>
              <Text style={{ fontWeight: '700' }}>{c.display_name}: </Text>
              {c.body}
            </Text>
          ))}
          <View style={{ flexDirection: 'row', alignItems: 'center' }}>
            <Input
              value={commentText}
              onChangeText={setCommentText}
              placeholder={t('write_comment', lang)}
              style={{ flex: 1, marginBottom: 0 }}
              onSubmitEditing={sendComment}
              returnKeyType="send"
            />
          </View>
        </View>
      )}
    </Card>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: 'row', alignItems: 'center' },
  name: { fontWeight: '700', color: colors.text },
  tags: { flexDirection: 'row', flexWrap: 'wrap', marginTop: 8 },
  body: { color: colors.text, marginTop: 8, lineHeight: 21 },
  media: { width: '100%', height: 220, borderRadius: 12, marginTop: 10 },
  videoPh: { backgroundColor: '#14232B', alignItems: 'center', justifyContent: 'center' },
  actions: { flexDirection: 'row', marginTop: 10 },
  action: { marginEnd: 22 },
  comments: { marginTop: 10, borderTopWidth: 1, borderTopColor: colors.border, paddingTop: 8 },
  comment: { color: colors.text, marginBottom: 4, fontSize: 13 },
});

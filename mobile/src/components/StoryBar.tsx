// Horizontal story strip: add button + rings (tiffany = new, gray = seen).
import React from 'react';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { Story } from '../api';
import { Lang, t } from '../i18n';
import { colors } from '../theme';

export default function StoryBar({
  stories, lang, onAdd, onOpen,
}: {
  stories: Story[]; lang: Lang; onAdd: () => void; onOpen: (authorId: number) => void;
}) {
  const byAuthor = new Map<number, Story[]>();
  for (const s of stories) {
    const list = byAuthor.get(s.author_id) ?? [];
    list.push(s);
    byAuthor.set(s.author_id, list);
  }

  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.bar}>
      <TouchableOpacity style={styles.item} onPress={onAdd}>
        <View style={[styles.ring, styles.ringNew]}>
          <Text style={styles.plus}>＋</Text>
        </View>
        <Text style={styles.label} numberOfLines={1}>{t('add_story', lang)}</Text>
      </TouchableOpacity>
      {[...byAuthor.entries()].map(([authorId, group]) => {
        const seen = group.every((s) => s.seen);
        const first = group[0];
        return (
          <TouchableOpacity key={authorId} style={styles.item} onPress={() => onOpen(authorId)}>
            <View style={[styles.ring, seen ? styles.ringSeen : styles.ringNew]}>
              <Text style={[styles.initial, seen && { color: colors.text2 }]}>
                {first.display_name.charAt(0).toUpperCase()}
              </Text>
            </View>
            <Text style={styles.label} numberOfLines={1}>{first.display_name}</Text>
          </TouchableOpacity>
        );
      })}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  bar: { paddingVertical: 8 },
  item: { alignItems: 'center', width: 72 },
  ring: {
    width: 62, height: 62, borderRadius: 31, borderWidth: 3,
    alignItems: 'center', justifyContent: 'center', backgroundColor: colors.light,
  },
  ringNew: { borderColor: colors.primary },
  ringSeen: { borderColor: '#C9D2D4', backgroundColor: '#F0F3F4' },
  initial: { color: colors.primary, fontWeight: '800', fontSize: 20 },
  plus: { color: colors.primary, fontSize: 26, fontWeight: '700' },
  label: { fontSize: 11, color: colors.text2, marginTop: 4, maxWidth: 68 },
});

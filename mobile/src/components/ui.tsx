// Small shared UI atoms.
import React from 'react';
import {
  ActivityIndicator, StyleSheet, Text, TextInput, TouchableOpacity, View, ViewStyle,
} from 'react-native';
import { colors, radius } from '../theme';

export function Card({ children, style }: { children: React.ReactNode; style?: ViewStyle }) {
  return <View style={[styles.card, style]}>{children}</View>;
}

export function Btn({
  label, onPress, kind = 'primary', small = false, disabled = false,
}: {
  label: string; onPress: () => void; kind?: 'primary' | 'ghost' | 'danger';
  small?: boolean; disabled?: boolean;
}) {
  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled}
      style={[
        styles.btn,
        small && styles.btnSmall,
        kind === 'ghost' && styles.btnGhost,
        kind === 'danger' && styles.btnDanger,
        disabled && { opacity: 0.5 },
      ]}
    >
      <Text style={[styles.btnText, kind === 'ghost' && { color: colors.primary }]}>{label}</Text>
    </TouchableOpacity>
  );
}

export function Input(props: React.ComponentProps<typeof TextInput>) {
  return (
    <TextInput
      placeholderTextColor={colors.text2}
      {...props}
      style={[styles.input, props.style]}
    />
  );
}

export function Avatar({ name, size = 44 }: { name: string; size?: number }) {
  return (
    <View style={[styles.avatar, { width: size, height: size, borderRadius: size / 2 }]}>
      <Text style={[styles.avatarText, { fontSize: size * 0.4 }]}>
        {(name || '?').trim().charAt(0).toUpperCase()}
      </Text>
    </View>
  );
}

export function Tag({ label }: { label: string }) {
  return (
    <View style={styles.tag}>
      <Text style={styles.tagText}>{label}</Text>
    </View>
  );
}

export function Loading() {
  return (
    <View style={{ padding: 32, alignItems: 'center' }}>
      <ActivityIndicator color={colors.primary} size="large" />
    </View>
  );
}

export function Muted({ children }: { children: React.ReactNode }) {
  return <Text style={{ color: colors.text2, fontSize: 12 }}>{children}</Text>;
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderRadius: radius.card,
    padding: 14,
    marginBottom: 10,
    shadowColor: colors.text,
    shadowOpacity: 0.05,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 1 },
    elevation: 1,
  },
  btn: {
    backgroundColor: colors.primary,
    borderRadius: radius.button,
    paddingVertical: 12,
    paddingHorizontal: 18,
    alignItems: 'center',
  },
  btnSmall: { paddingVertical: 7, paddingHorizontal: 12 },
  btnGhost: {
    backgroundColor: colors.light,
  },
  btnDanger: { backgroundColor: colors.live },
  btnText: { color: '#fff', fontWeight: '700' },
  input: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: radius.button,
    paddingVertical: 10,
    paddingHorizontal: 14,
    color: colors.text,
    marginBottom: 10,
  },
  avatar: {
    backgroundColor: colors.light,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: { color: colors.primary, fontWeight: '800' },
  tag: {
    backgroundColor: colors.light,
    borderRadius: radius.pill,
    paddingHorizontal: 10,
    paddingVertical: 2,
    marginEnd: 6,
  },
  tagText: { color: colors.primary, fontSize: 11, fontWeight: '600' },
});

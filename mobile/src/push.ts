// Expo push notification registration — fully best-effort:
// failures (simulator, permissions denied, Expo Go limits) never break the app.
import { Platform } from 'react-native';
import * as Device from 'expo-device';
import * as Notifications from 'expo-notifications';
import { registerDevice } from './api';

export async function registerForPush(): Promise<void> {
  try {
    if (!Device.isDevice) return; // emulators can't receive push

    const { status: existing } = await Notifications.getPermissionsAsync();
    let status = existing;
    if (existing !== 'granted') {
      status = (await Notifications.requestPermissionsAsync()).status;
    }
    if (status !== 'granted') return;

    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('default', {
        name: 'Silver',
        importance: Notifications.AndroidImportance.DEFAULT,
        lightColor: '#0ABAB5',
      });
    }
    const token = (await Notifications.getExpoPushTokenAsync()).data;
    await registerDevice(token, Platform.OS);
  } catch {
    /* push is an enhancement, never a blocker */
  }
}

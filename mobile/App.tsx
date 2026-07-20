// Silver mobile — navigation shell.
import React from 'react';
import { Text, View } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';
import { AppProvider, useApp } from './src/state';
import { t } from './src/i18n';
import { colors } from './src/theme';
import AuthScreen from './src/screens/AuthScreen';
import OnboardingScreen from './src/screens/OnboardingScreen';
import HomeScreen from './src/screens/HomeScreen';
import ComposeScreen from './src/screens/ComposeScreen';
import DiscoverScreen from './src/screens/DiscoverScreen';
import MessagesScreen from './src/screens/MessagesScreen';
import ChatScreen from './src/screens/ChatScreen';
import LiveScreen from './src/screens/LiveScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import NotificationsScreen from './src/screens/NotificationsScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import { Loading } from './src/components/ui';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

function Tabs() {
  const { lang } = useApp();
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.text2,
        tabBarStyle: { backgroundColor: colors.card, borderTopColor: colors.border },
        tabBarIcon: ({ focused }) => {
          const icons: Record<string, string> = {
            HomeTab: '🏠', DiscoverTab: '🔍', ComposeTab: '＋',
            MessagesTab: '✉️', ProfileTab: '👤',
          };
          const isCompose = route.name === 'ComposeTab';
          return (
            <View
              style={
                isCompose
                  ? {
                      backgroundColor: colors.primary, width: 46, height: 46,
                      borderRadius: 23, alignItems: 'center', justifyContent: 'center',
                      marginBottom: 14,
                    }
                  : undefined
              }
            >
              <Text style={{
                fontSize: isCompose ? 26 : 20,
                color: isCompose ? '#fff' : undefined,
                opacity: focused || isCompose ? 1 : 0.55,
              }}>
                {icons[route.name]}
              </Text>
            </View>
          );
        },
      })}
    >
      <Tab.Screen name="HomeTab" component={HomeScreen} options={{ title: t('home', lang) }} />
      <Tab.Screen name="DiscoverTab" component={DiscoverScreen} options={{ title: t('discover', lang) }} />
      <Tab.Screen name="ComposeTab" component={ComposeScreen} options={{ title: '' }} />
      <Tab.Screen name="MessagesTab" component={MessagesScreen} options={{ title: t('messages', lang) }} />
      <Tab.Screen name="ProfileTab" component={ProfileScreen} options={{ title: t('profile', lang) }} />
    </Tab.Navigator>
  );
}

function Root() {
  const { user, ready, needsOnboarding, lang } = useApp();
  if (!ready) return <Loading />;
  if (!user) return <AuthScreen />;
  if (needsOnboarding) return <OnboardingScreen />;
  return (
    <Stack.Navigator>
      <Stack.Screen name="Main" component={Tabs} options={{ headerShown: false }} />
      <Stack.Screen name="Chat" component={ChatScreen}
        options={{ title: t('messages', lang), headerTintColor: colors.text }} />
      <Stack.Screen name="Live" component={LiveScreen}
        options={{ title: t('live', lang), headerTintColor: colors.text }} />
      <Stack.Screen name="Profile" component={ProfileScreen}
        options={{ title: t('profile', lang), headerTintColor: colors.text }} />
      <Stack.Screen name="Compose" component={ComposeScreen}
        options={{ title: t('create', lang), headerTintColor: colors.text }} />
      <Stack.Screen name="Notifications" component={NotificationsScreen}
        options={{ title: t('notifications', lang), headerTintColor: colors.text }} />
      <Stack.Screen name="Settings" component={SettingsScreen}
        options={{ title: t('settings', lang), headerTintColor: colors.text }} />
    </Stack.Navigator>
  );
}

export default function App() {
  return (
    <AppProvider>
      <NavigationContainer>
        <StatusBar style="dark" />
        <Root />
      </NavigationContainer>
    </AppProvider>
  );
}

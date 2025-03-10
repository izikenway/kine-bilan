import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Provider as PaperProvider, DefaultTheme, ActivityIndicator } from 'react-native-paper';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';

// Écrans fictifs pour la démonstration
// Dans une implémentation complète, ces écrans seraient importés de fichiers séparés
import LoginScreen from './screens/LoginScreen';
import DashboardScreen from './screens/DashboardScreen';
import PatientsScreen from './screens/PatientsScreen';
import AppointmentsScreen from './screens/AppointmentsScreen';
import ProfileScreen from './screens/ProfileScreen';

// Thème de l'application
const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#3f51b5',
    accent: '#f50057',
  },
};

// Client React Query pour la gestion des API
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Navigateurs
const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Contexte d'authentification
const AuthContext = React.createContext();

// Navigation principale avec onglets
const TabNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Dashboard') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Patients') {
            iconName = focused ? 'people' : 'people-outline';
          } else if (route.name === 'Appointments') {
            iconName = focused ? 'calendar' : 'calendar-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: 'gray',
        headerShown: true,
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen} 
        options={{ title: 'Tableau de bord' }}
      />
      <Tab.Screen 
        name="Patients" 
        component={PatientsScreen} 
        options={{ title: 'Patients' }}
      />
      <Tab.Screen 
        name="Appointments" 
        component={AppointmentsScreen} 
        options={{ title: 'Rendez-vous' }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen} 
        options={{ title: 'Profil' }}
      />
    </Tab.Navigator>
  );
};

export default function App() {
  const [state, dispatch] = React.useReducer(
    (prevState, action) => {
      switch (action.type) {
        case 'RESTORE_TOKEN':
          return {
            ...prevState,
            userToken: action.token,
            isLoading: false,
          };
        case 'SIGN_IN':
          return {
            ...prevState,
            isSignout: false,
            userToken: action.token,
          };
        case 'SIGN_OUT':
          return {
            ...prevState,
            isSignout: true,
            userToken: null,
          };
      }
    },
    {
      isLoading: true,
      isSignout: false,
      userToken: null,
    }
  );

  // Effet pour vérifier si l'utilisateur est déjà connecté
  useEffect(() => {
    const bootstrapAsync = async () => {
      let userToken = null;

      try {
        userToken = await SecureStore.getItemAsync('userToken');
      } catch (e) {
        console.log('Échec de restauration du token:', e);
      }

      dispatch({ type: 'RESTORE_TOKEN', token: userToken });
    };

    bootstrapAsync();
  }, []);

  // Actions d'authentification exposées via le contexte
  const authContext = React.useMemo(
    () => ({
      signIn: async (data) => {
        // Dans une implémentation réelle, envoyer une requête API d'authentification
        // Simulons un token pour la démonstration
        const token = 'dummy-auth-token';
        
        try {
          await SecureStore.setItemAsync('userToken', token);
        } catch (e) {
          console.log('Échec de sauvegarde du token:', e);
        }
        
        dispatch({ type: 'SIGN_IN', token });
      },
      signOut: async () => {
        try {
          await SecureStore.deleteItemAsync('userToken');
        } catch (e) {
          console.log('Échec de suppression du token:', e);
        }
        
        dispatch({ type: 'SIGN_OUT' });
      },
    }),
    []
  );

  // Afficher un indicateur de chargement pendant la restauration du token
  if (state.isLoading) {
    return (
      <SafeAreaProvider>
        <PaperProvider theme={theme}>
          <ActivityIndicator size="large" color={theme.colors.primary} style={{ flex: 1 }} />
        </PaperProvider>
      </SafeAreaProvider>
    );
  }

  return (
    <AuthContext.Provider value={authContext}>
      <QueryClientProvider client={queryClient}>
        <SafeAreaProvider>
          <PaperProvider theme={theme}>
            <NavigationContainer>
              <Stack.Navigator>
                {state.userToken == null ? (
                  // Routes non authentifiées
                  <Stack.Screen 
                    name="Login" 
                    component={LoginScreen} 
                    options={{ 
                      title: 'Connexion',
                      animationTypeForReplace: state.isSignout ? 'pop' : 'push',
                      headerShown: false,
                    }} 
                  />
                ) : (
                  // Routes authentifiées
                  <Stack.Screen 
                    name="Main" 
                    component={TabNavigator} 
                    options={{ headerShown: false }} 
                  />
                )}
              </Stack.Navigator>
            </NavigationContainer>
            <StatusBar style="auto" />
          </PaperProvider>
        </SafeAreaProvider>
      </QueryClientProvider>
    </AuthContext.Provider>
  );
}

// Exporter le contexte d'authentification pour y accéder depuis les écrans
export { AuthContext };
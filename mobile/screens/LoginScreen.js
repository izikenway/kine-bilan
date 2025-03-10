import React, { useState, useContext } from 'react';
import {
  View,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Image,
  ScrollView,
} from 'react-native';
import {
  TextInput,
  Button,
  Text,
  Headline,
  HelperText,
  Surface,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AuthContext } from '../App';

const LoginScreen = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [loading, setLoading] = useState(false);
  const [secureTextEntry, setSecureTextEntry] = useState(true);

  const { signIn } = useContext(AuthContext);

  const validateEmail = (email) => {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
  };

  const handleLogin = async () => {
    // Réinitialiser les erreurs
    setEmailError('');
    setPasswordError('');
    
    // Valider l'email
    if (!email) {
      setEmailError('L\'email est requis');
      return;
    } else if (!validateEmail(email)) {
      setEmailError('Format d\'email invalide');
      return;
    }
    
    // Valider le mot de passe
    if (!password) {
      setPasswordError('Le mot de passe est requis');
      return;
    }
    
    try {
      setLoading(true);

      // Dans une implémentation réelle, vous feriez un appel API ici
      // Pour cette démo, nous simulons une connexion réussie
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Appeler la fonction de connexion du contexte d'authentification
      signIn({ email, password });
    } catch (error) {
      console.error('Erreur de connexion:', error);
      setPasswordError('Identifiants incorrects');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardAvoidingView}
      >
        <ScrollView 
          contentContainerStyle={styles.scrollView}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.logoContainer}>
            <Image
              source={require('../assets/icon.png')}
              style={styles.logo}
              resizeMode="contain"
            />
            <Headline style={styles.appName}>KinéBilan</Headline>
          </View>

          <Surface style={styles.formContainer}>
            <Text style={styles.title}>Connexion</Text>
            
            <TextInput
              label="Email"
              value={email}
              onChangeText={setEmail}
              mode="outlined"
              autoCapitalize="none"
              keyboardType="email-address"
              error={!!emailError}
              style={styles.input}
            />
            {emailError ? <HelperText type="error">{emailError}</HelperText> : null}
            
            <TextInput
              label="Mot de passe"
              value={password}
              onChangeText={setPassword}
              mode="outlined"
              secureTextEntry={secureTextEntry}
              error={!!passwordError}
              style={styles.input}
              right={
                <TextInput.Icon
                  icon={secureTextEntry ? 'eye' : 'eye-off'}
                  onPress={() => setSecureTextEntry(!secureTextEntry)}
                />
              }
            />
            {passwordError ? <HelperText type="error">{passwordError}</HelperText> : null}
            
            <Button
              mode="contained"
              onPress={handleLogin}
              loading={loading}
              disabled={loading}
              style={styles.button}
            >
              Se connecter
            </Button>
            
            <Text style={styles.helpText}>
              Si vous avez oublié votre mot de passe, veuillez contacter l'administrateur.
            </Text>
          </Surface>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  scrollView: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  logo: {
    width: 100,
    height: 100,
    marginBottom: 10,
  },
  appName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#3f51b5',
  },
  formContainer: {
    padding: 20,
    borderRadius: 10,
    elevation: 4,
  },
  title: {
    fontSize: 24,
    fontWeight: '500',
    marginBottom: 20,
    textAlign: 'center',
  },
  input: {
    marginBottom: 10,
  },
  button: {
    marginTop: 10,
    paddingVertical: 8,
  },
  helpText: {
    marginTop: 20,
    textAlign: 'center',
    fontSize: 14,
    color: '#757575',
  },
});

export default LoginScreen;
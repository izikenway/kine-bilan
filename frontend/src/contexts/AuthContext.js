import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';
import jwt_decode from 'jwt-decode';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';

// Création du contexte d'authentification
const AuthContext = createContext();

// Hook personnalisé pour utiliser le contexte d'authentification
export const useAuth = () => {
  return useContext(AuthContext);
};

// Fournisseur du contexte d'authentification
const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  // Effet pour vérifier et mettre à jour l'utilisateur au chargement
  useEffect(() => {
    const loadUser = async () => {
      if (token) {
        try {
          // Vérification si le token est expiré
          const decodedToken = jwt_decode(token);
          const currentTime = Date.now() / 1000;

          if (decodedToken.exp < currentTime) {
            // Token expiré, déconnexion
            logout();
            return;
          }

          // Configuration de l'en-tête d'autorisation pour toutes les requêtes
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

          // Récupération des informations de l'utilisateur
          const response = await axios.get('/api/auth/me');
          setCurrentUser(response.data);
        } catch (error) {
          console.error('Erreur lors du chargement de l\'utilisateur:', error);
          localStorage.removeItem('token');
          setToken(null);
          setCurrentUser(null);
        }
      }
      setLoading(false);
    };

    loadUser();
  }, [token]);

  // Fonction de connexion
  const login = async (email, password) => {
    try {
      const response = await axios.post('/api/auth/login', { email, password });
      const { access_token, user } = response.data;

      // Enregistrement du token et configuration d'axios
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      setToken(access_token);
      setCurrentUser(user);

      enqueueSnackbar('Connexion réussie', { variant: 'success' });
      return true;
    } catch (error) {
      console.error('Erreur de connexion:', error);
      const message = error.response?.data?.message || 'Erreur de connexion';
      enqueueSnackbar(message, { variant: 'error' });
      return false;
    }
  };

  // Fonction de déconnexion
  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setToken(null);
    setCurrentUser(null);
    navigate('/login');
    enqueueSnackbar('Vous avez été déconnecté', { variant: 'info' });
  };

  // Valeurs exposées par le contexte
  const value = {
    currentUser,
    loading,
    isAuthenticated: !!currentUser,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;
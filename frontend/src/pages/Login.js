import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box } from '@mui/material';
import LoginForm from '../components/auth/LoginForm';
import { useAuth } from '../contexts/AuthContext';

/**
 * Page de connexion
 */
const Login = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Redirection vers le tableau de bord si l'utilisateur est déjà connecté
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        bgcolor: '#f5f5f5',
      }}
    >
      <LoginForm />
    </Box>
  );
};

export default Login;
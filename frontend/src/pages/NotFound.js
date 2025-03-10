import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Box, Button, Typography, Container } from '@mui/material';
import { Home as HomeIcon } from '@mui/icons-material';

/**
 * Page 404 - Non trouvée
 */
const NotFound = () => {
  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          textAlign: 'center',
          py: 5,
        }}
      >
        <Typography variant="h1" color="primary" sx={{ fontSize: '6rem', fontWeight: 700, mb: 2 }}>
          404
        </Typography>
        
        <Typography variant="h4" gutterBottom>
          Page non trouvée
        </Typography>
        
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 500 }}>
          La page que vous recherchez n'existe pas ou a été déplacée.
          Veuillez vérifier l'URL ou retourner à la page d'accueil.
        </Typography>
        
        <Button
          component={RouterLink}
          to="/dashboard"
          variant="contained"
          color="primary"
          startIcon={<HomeIcon />}
          size="large"
        >
          Retour à l'accueil
        </Button>
      </Box>
    </Container>
  );
};

export default NotFound;
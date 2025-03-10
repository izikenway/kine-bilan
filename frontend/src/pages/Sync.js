import React, { useState } from 'react';
import { useMutation } from 'react-query';
import axios from 'axios';
import {
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Grid,
  TextField,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  Sync as SyncIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  NewReleases as NewReleasesIcon,
  Update as UpdateIcon,
  Person as PersonIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';

/**
 * Page de synchronisation avec Doctolib
 */
const Sync = () => {
  // États locaux
  const [days, setDays] = useState(30);
  const [results, setResults] = useState(null);

  // Mutation pour la synchronisation
  const { mutate, isLoading, error, isSuccess } = useMutation(
    async () => {
      const response = await axios.post('/api/sync/doctolib', { days });
      return response.data;
    },
    {
      onSuccess: (data) => {
        setResults(data.results);
      },
    }
  );

  // Démarrer la synchronisation
  const handleSync = () => {
    setResults(null);
    mutate();
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Synchronisation Doctolib
      </Typography>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Configuration de la synchronisation
        </Typography>
        
        <Typography variant="body2" color="text.secondary" paragraph>
          Cette page vous permet de synchroniser manuellement les rendez-vous depuis Doctolib.
          La synchronisation automatique est configurée pour s'exécuter périodiquement.
        </Typography>
        
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={4}>
            <TextField
              label="Nombre de jours à synchroniser"
              type="number"
              fullWidth
              value={days}
              onChange={(e) => setDays(parseInt(e.target.value) || 30)}
              inputProps={{ min: 1, max: 365 }}
              helperText="Période future à synchroniser (1-365 jours)"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Button
              variant="contained"
              color="primary"
              startIcon={isLoading ? <CircularProgress size={20} /> : <SyncIcon />}
              onClick={handleSync}
              disabled={isLoading}
              fullWidth
              sx={{ py: 1.5 }}
            >
              {isLoading ? 'Synchronisation en cours...' : 'Démarrer la synchronisation'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Affichage des résultats */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Erreur lors de la synchronisation : {error.message}
        </Alert>
      )}

      {isSuccess && results && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Résultats de la synchronisation
            </Typography>
            
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={6} md={3}>
                <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="body2" color="text.secondary">Total des rendez-vous</Typography>
                  <Typography variant="h4">{results.total_appointments || 0}</Typography>
                </Card>
              </Grid>
              
              <Grid item xs={6} md={3}>
                <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="body2" color="text.secondary">Nouveaux rendez-vous</Typography>
                  <Typography variant="h4" color="primary">{results.new_appointments || 0}</Typography>
                </Card>
              </Grid>
              
              <Grid item xs={6} md={3}>
                <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="body2" color="text.secondary">Nouveaux patients</Typography>
                  <Typography variant="h4" color="secondary">{results.new_patients || 0}</Typography>
                </Card>
              </Grid>
              
              <Grid item xs={6} md={3}>
                <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="body2" color="text.secondary">Rendez-vous annulés</Typography>
                  <Typography variant="h4" color="error">{results.cancelled_appointments || 0}</Typography>
                </Card>
              </Grid>
            </Grid>
            
            {results.errors && results.errors.length > 0 && (
              <>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle1" color="error" gutterBottom>
                  Erreurs rencontrées
                </Typography>
                <List dense>
                  {results.errors.map((error, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <ErrorIcon color="error" />
                      </ListItemIcon>
                      <ListItemText primary={error} />
                    </ListItem>
                  ))}
                </List>
              </>
            )}
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="body2" color="text.secondary">
              Synchronisation terminée avec succès. Les données ont été mises à jour.
            </Typography>
            
            <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
              <Chip 
                icon={<NewReleasesIcon />} 
                label={`${results.new_appointments || 0} nouveaux rendez-vous`} 
                color="primary" 
                variant="outlined" 
              />
              <Chip 
                icon={<UpdateIcon />} 
                label={`${results.updated_appointments || 0} rendez-vous mis à jour`} 
                color="info" 
                variant="outlined" 
              />
              <Chip 
                icon={<PersonIcon />} 
                label={`${results.new_patients || 0} nouveaux patients`} 
                color="secondary" 
                variant="outlined" 
              />
              <Chip 
                icon={<CancelIcon />} 
                label={`${results.cancelled_appointments || 0} rendez-vous annulés`} 
                color="error" 
                variant="outlined" 
              />
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Informations sur la synchronisation automatique */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Synchronisation automatique
        </Typography>
        
        <Typography variant="body2" paragraph>
          La synchronisation automatique est configurée pour s'exécuter toutes les heures.
          Vous pouvez modifier cette fréquence dans les paramètres de l'application.
        </Typography>
        
        <Alert severity="info">
          <Typography variant="body2">
            Les séances de kinésithérapie sans bilan depuis plus de 60 jours seront automatiquement
            détectées et pourront être annulées selon vos paramètres.
          </Typography>
        </Alert>
      </Paper>
    </Box>
  );
};

export default Sync;
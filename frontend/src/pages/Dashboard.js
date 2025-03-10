import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import {
  Box,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  CardHeader,
} from '@mui/material';
import {
  People as PeopleIcon,
  CalendarToday as CalendarIcon,
  Warning as WarningIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';

/**
 * Page de tableau de bord
 */
const Dashboard = () => {
  // Récupération des données du tableau de bord
  const { data, isLoading, error } = useQuery('dashboardData', async () => {
    const response = await axios.get('/api/reports/dashboard');
    return response.data;
  });

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Erreur lors du chargement des données : {error.message}
      </Alert>
    );
  }

  // Statistiques à afficher dans le tableau de bord
  const stats = [
    {
      title: 'Patients',
      value: data?.total_patients || 0,
      icon: <PeopleIcon fontSize="large" color="primary" />,
      description: 'Nombre total de patients',
    },
    {
      title: 'Patients nécessitant un bilan',
      value: data?.patients_needing_bilan || 0,
      icon: <WarningIcon fontSize="large" color="error" />,
      description: 'Patients devant effectuer un bilan',
    },
    {
      title: "Rendez-vous aujourd'hui",
      value: data?.today_appointments || 0,
      icon: <CalendarIcon fontSize="large" color="secondary" />,
      description: "Nombre de rendez-vous pour aujourd'hui",
    },
    {
      title: 'Notifications en attente',
      value: data?.pending_notifications || 0,
      icon: <NotificationsIcon fontSize="large" color="info" />,
      description: "Notifications à envoyer",
    },
  ];

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom component="div" sx={{ mb: 4 }}>
        Tableau de bord
      </Typography>

      {/* Statistiques principales */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Paper
              elevation={2}
              sx={{
                p: 2,
                display: 'flex',
                flexDirection: 'column',
                height: 140,
                borderRadius: 2,
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <Box sx={{ position: 'absolute', top: 10, right: 10 }}>
                {stat.icon}
              </Box>
              <Typography variant="h6" component="div" sx={{ mb: 1 }}>
                {stat.title}
              </Typography>
              <Typography variant="h3" component="div" sx={{ mt: 'auto' }}>
                {stat.value}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {stat.description}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Rendez-vous programmés cette semaine */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 2 }}>
            <CardHeader title="Rendez-vous cette semaine" />
            <CardContent>
              <Typography variant="h3" component="div" sx={{ mb: 2 }}>
                {data?.week_appointments || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Nombre total de rendez-vous programmés pour cette semaine
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Bilans programmés */}
        <Grid item xs={12} md={6}>
          <Card sx={{ borderRadius: 2 }}>
            <CardHeader title="Bilans programmés" />
            <CardContent>
              <Typography variant="h3" component="div" sx={{ mb: 2 }}>
                {data?.upcoming_bilans || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Nombre de bilans programmés à venir
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
import React, { useState } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  FormControlLabel,
  Switch,
  Divider,
  Grid,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

/**
 * Page de gestion des patients
 */
const Patients = () => {
  // États locaux
  const [searchTerm, setSearchTerm] = useState('');
  const [showNeedsBilan, setShowNeedsBilan] = useState(false);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  // Récupération des données de patients
  const { data, isLoading, error, refetch } = useQuery(
    ['patients', page, pageSize, searchTerm, showNeedsBilan],
    async () => {
      const params = {
        page: page + 1, // Les pages commencent à 1 pour l'API
        per_page: pageSize,
        search: searchTerm,
      };

      if (showNeedsBilan) {
        params.needs_bilan = 'true';
      }

      const response = await axios.get('/api/patients', { params });
      return response.data;
    },
    {
      keepPreviousData: true,
    }
  );

  // Définition des colonnes de la grille de données
  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'last_name', headerName: 'Nom', width: 150 },
    { field: 'first_name', headerName: 'Prénom', width: 150 },
    { field: 'email', headerName: 'Email', width: 220 },
    { field: 'phone', headerName: 'Téléphone', width: 150 },
    {
      field: 'last_bilan_date',
      headerName: 'Dernier bilan',
      width: 150,
      renderCell: (params) => {
        if (!params.value) {
          return (
            <Chip
              label="Aucun"
              size="small"
              color="warning"
              icon={<WarningIcon />}
            />
          );
        }
        return format(new Date(params.value), 'dd/MM/yyyy', { locale: fr });
      },
    },
    {
      field: 'needs_bilan',
      headerName: 'Besoin de bilan',
      width: 150,
      valueGetter: (params) => {
        if (!params.row.last_bilan_date) return true;
        const lastBilanDate = new Date(params.row.last_bilan_date);
        const today = new Date();
        const daysSinceLastBilan = Math.floor(
          (today - lastBilanDate) / (1000 * 60 * 60 * 24)
        );
        return daysSinceLastBilan >= 60;
      },
      renderCell: (params) => {
        return params.value ? (
          <Chip
            label="Oui"
            size="small"
            color="error"
            icon={<WarningIcon />}
          />
        ) : (
          <Chip label="Non" size="small" color="success" />
        );
      },
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 150,
      sortable: false,
      renderCell: (params) => (
        <Box>
          <Tooltip title="Modifier">
            <IconButton size="small" onClick={() => handleEdit(params.row)}>
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Supprimer">
            <IconButton size="small" onClick={() => handleDelete(params.row.id)}>
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  // Handlers (à implémenter)
  const handleEdit = (patient) => {
    console.log('Éditer le patient:', patient);
    // Ouvrir un dialogue d'édition
  };

  const handleDelete = (id) => {
    console.log('Supprimer le patient avec ID:', id);
    // Afficher une confirmation avant suppression
  };

  const handleAddPatient = () => {
    console.log('Ajouter un nouveau patient');
    // Ouvrir un dialogue de création
  };

  // Pour les besoins de cet exemple, nous simulons un composant
  // sans implémenter complètement les fonctionnalités CRUD
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Gestion des patients
      </Typography>

      {/* Barre d'outils */}
      <Paper sx={{ mb: 3, p: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Rechercher un patient"
              variant="outlined"
              size="small"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon color="action" sx={{ mr: 1 }} />,
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControlLabel
              control={
                <Switch
                  checked={showNeedsBilan}
                  onChange={(e) => setShowNeedsBilan(e.target.checked)}
                  color="primary"
                />
              }
              label="Besoin de bilan uniquement"
            />
          </Grid>
          <Grid item xs={12} md={3} sx={{ textAlign: 'right' }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleAddPatient}
              sx={{ mr: 1 }}
            >
              Nouveau patient
            </Button>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={() => refetch()}
            >
              Actualiser
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Affichage d'erreur */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Erreur lors du chargement des patients : {error.message}
        </Alert>
      )}

      {/* Tableau des patients */}
      <Paper sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={data?.patients || []}
          columns={columns}
          pagination
          page={page}
          pageSize={pageSize}
          rowsPerPageOptions={[5, 10, 25, 50]}
          rowCount={data?.total || 0}
          paginationMode="server"
          onPageChange={(newPage) => setPage(newPage)}
          onPageSizeChange={(newPageSize) => setPageSize(newPageSize)}
          loading={isLoading}
          disableSelectionOnClick
          sx={{
            '& .MuiDataGrid-cell:hover': {
              color: 'primary.main',
            },
          }}
        />
      </Paper>
    </Box>
  );
};

export default Patients;
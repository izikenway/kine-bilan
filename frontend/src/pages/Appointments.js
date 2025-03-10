import React, { useState } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  Chip,
  IconButton,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';
import { DataGrid } from '@mui/x-data-grid';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Event as EventIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';

/**
 * Page de gestion des rendez-vous
 */
const Appointments = () => {
  // États locaux
  const [dateFrom, setDateFrom] = useState(null);
  const [dateTo, setDateTo] = useState(null);
  const [status, setStatus] = useState('');
  const [isBilan, setIsBilan] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  // Construction des paramètres de requête
  const buildQueryParams = () => {
    const params = {
      page: page + 1, // API commence à 1
      per_page: pageSize,
    };

    if (dateFrom) {
      params.date_from = format(dateFrom, 'yyyy-MM-dd');
    }

    if (dateTo) {
      params.date_to = format(dateTo, 'yyyy-MM-dd');
    }

    if (status) {
      params.status = status;
    }

    if (isBilan !== '') {
      params.is_bilan = isBilan;
    }

    return params;
  };

  // Récupération des rendez-vous
  const { data, isLoading, error, refetch } = useQuery(
    ['appointments', page, pageSize, dateFrom, dateTo, status, isBilan],
    async () => {
      const params = buildQueryParams();
      const response = await axios.get('/api/appointments', { params });
      return response.data;
    },
    {
      keepPreviousData: true,
    }
  );

  // Définition des colonnes pour la grille de données
  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    {
      field: 'datetime',
      headerName: 'Date et heure',
      width: 180,
      valueGetter: (params) => new Date(params.row.datetime),
      renderCell: (params) => {
        return format(new Date(params.value), 'dd/MM/yyyy HH:mm', { locale: fr });
      },
    },
    {
      field: 'patient',
      headerName: 'Patient',
      width: 200,
      valueGetter: (params) => params.row.patient?.name || '',
    },
    {
      field: 'duration',
      headerName: 'Durée (min)',
      width: 120,
    },
    {
      field: 'status',
      headerName: 'Statut',
      width: 150,
      renderCell: (params) => {
        let color = 'default';
        let icon = null;

        switch (params.value) {
          case 'scheduled':
            color = 'primary';
            icon = <EventIcon />;
            break;
          case 'completed':
            color = 'success';
            icon = <CheckIcon />;
            break;
          case 'cancelled':
            color = 'error';
            icon = <CloseIcon />;
            break;
          case 'missed':
            color = 'warning';
            icon = <WarningIcon />;
            break;
          default:
            break;
        }

        const labels = {
          scheduled: 'Programmé',
          completed: 'Terminé',
          cancelled: 'Annulé',
          missed: 'Manqué',
        };

        return (
          <Chip
            label={labels[params.value] || params.value}
            size="small"
            color={color}
            icon={icon}
          />
        );
      },
    },
    {
      field: 'is_bilan',
      headerName: 'Type',
      width: 120,
      renderCell: (params) => {
        return params.value ? (
          <Chip label="Bilan" size="small" color="secondary" />
        ) : (
          <Chip label="Séance" size="small" color="default" />
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
  const handleEdit = (appointment) => {
    console.log('Éditer le rendez-vous:', appointment);
    // Ouvrir un dialogue d'édition
  };

  const handleDelete = (id) => {
    console.log('Supprimer le rendez-vous avec ID:', id);
    // Afficher une confirmation avant suppression
  };

  const handleAddAppointment = () => {
    console.log('Ajouter un nouveau rendez-vous');
    // Ouvrir un dialogue de création
  };

  // Pour les besoins de cet exemple, nous simulons un composant
  // sans implémenter complètement les fonctionnalités CRUD
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Gestion des rendez-vous
      </Typography>

      {/* Barre d'outils avec filtres */}
      <Paper sx={{ mb: 3, p: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={3}>
            <LocalizationProvider dateAdapter={AdapterDateFns} locale={fr}>
              <DatePicker
                label="Date de début"
                value={dateFrom}
                onChange={setDateFrom}
                renderInput={(params) => <TextField {...params} fullWidth size="small" />}
              />
            </LocalizationProvider>
          </Grid>
          <Grid item xs={12} md={3}>
            <LocalizationProvider dateAdapter={AdapterDateFns} locale={fr}>
              <DatePicker
                label="Date de fin"
                value={dateTo}
                onChange={setDateTo}
                renderInput={(params) => <TextField {...params} fullWidth size="small" />}
              />
            </LocalizationProvider>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Statut</InputLabel>
              <Select value={status} label="Statut" onChange={(e) => setStatus(e.target.value)}>
                <MenuItem value="">Tous</MenuItem>
                <MenuItem value="scheduled">Programmé</MenuItem>
                <MenuItem value="completed">Terminé</MenuItem>
                <MenuItem value="cancelled">Annulé</MenuItem>
                <MenuItem value="missed">Manqué</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Type</InputLabel>
              <Select value={isBilan} label="Type" onChange={(e) => setIsBilan(e.target.value)}>
                <MenuItem value="">Tous</MenuItem>
                <MenuItem value="true">Bilan</MenuItem>
                <MenuItem value="false">Séance</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2} sx={{ textAlign: 'right' }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleAddAppointment}
              sx={{ mr: 1 }}
            >
              Nouveau
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
          Erreur lors du chargement des rendez-vous : {error.message}
        </Alert>
      )}

      {/* Tableau des rendez-vous */}
      <Paper sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={data?.appointments || []}
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

export default Appointments;
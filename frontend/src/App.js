import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';

// Composant de protection des routes
import ProtectedRoute from './routes/ProtectedRoute';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

// Chargement paresseux pour les autres pages (optimisation des performances)
const Patients = React.lazy(() => import('./pages/Patients'));
const Appointments = React.lazy(() => import('./pages/Appointments'));
const Reports = React.lazy(() => import('./pages/Reports'));
const Sync = React.lazy(() => import('./pages/Sync'));
const Notifications = React.lazy(() => import('./pages/Notifications'));
const Settings = React.lazy(() => import('./pages/Settings'));
const NotFound = React.lazy(() => import('./pages/NotFound'));

/**
 * Composant d'affichage de chargement pour les composants en lazy loading
 */
const LazyLoadingComponent = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
    Chargement...
  </div>
);

/**
 * Composant principal de l'application
 * Gère le routage et la protection des routes
 */
const App = () => {
  // Configuration des routes de l'application
  return (
    <React.Suspense fallback={<LazyLoadingComponent />}>
      <Routes>
        {/* Routes publiques */}
        <Route path="/login" element={<Login />} />
        
        {/* Redirection de la page d'accueil vers le tableau de bord ou la page de connexion */}
        <Route path="/" element={<Navigate replace to="/dashboard" />} />
        
        {/* Routes protégées (nécessite authentification) */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/patients" element={<Patients />} />
          <Route path="/appointments" element={<Appointments />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/sync" element={<Sync />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
        
        {/* Page 404 pour les routes non trouvées */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </React.Suspense>
  );
};

export default App;
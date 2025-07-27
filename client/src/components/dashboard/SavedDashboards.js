/**
 * Saved Dashboards Component
 * Displays list of saved dashboards and allows loading them
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
  Tooltip,
  Menu,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  MoreVert as MoreIcon,
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
  Schedule as TimeIcon
} from '@mui/icons-material';
import ApiService from '../../services/api';

const SavedDashboards = ({ onLoadDashboard, onRefresh }) => {
  const [dashboards, setDashboards] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedDashboard, setSelectedDashboard] = useState(null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [editingDashboard, setEditingDashboard] = useState(null);
  const [editName, setEditName] = useState('');

  // Load saved dashboards
  const loadDashboards = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await ApiService.listDashboards('anonymous');
      
      if (response.status === 'success') {
        setDashboards(response.dashboards || []);
      } else {
        setError('Failed to load dashboards');
      }
    } catch (err) {
      console.error('Error loading dashboards:', err);
      setError('Failed to load dashboards');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboards();
  }, []);

  // Handle dashboard selection
  const handleLoadDashboard = async (dashboard) => {
    try {
      setLoading(true);
      
      const response = await ApiService.loadDashboard(dashboard.id, 'anonymous');
      
      if (response.status === 'success' && response.dashboard) {
        if (onLoadDashboard) {
          onLoadDashboard(response.dashboard);
        }
      } else {
        setError('Failed to load dashboard');
      }
    } catch (err) {
      console.error('Error loading dashboard:', err);
      setError('Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  // Handle dashboard deletion
  const handleDeleteDashboard = async () => {
    if (!selectedDashboard) return;
    
    try {
      setLoading(true);
      
      // Call the delete API
      const response = await ApiService.deleteDashboard(selectedDashboard.id, 'anonymous');
      
      if (response.status === 'success') {
        // Remove from the list
        setDashboards(prev => prev.filter(d => d.id !== selectedDashboard.id));
        setShowDeleteDialog(false);
        setSelectedDashboard(null);
        
        // Trigger refresh if callback provided
        if (onRefresh) {
          onRefresh();
        }
      } else {
        setError('Failed to delete dashboard');
      }
    } catch (err) {
      console.error('Error deleting dashboard:', err);
      setError('Failed to delete dashboard');
    } finally {
      setLoading(false);
    }
  };

  // Handle edit dashboard name
  const handleEditDashboard = async () => {
    if (!editingDashboard || !editName.trim()) return;
    
    try {
      setLoading(true);
      
      // Update the dashboard name in the list
      setDashboards(prev => prev.map(d => 
        d.id === editingDashboard.id 
          ? { ...d, name: editName.trim() }
          : d
      ));
      
      setEditingDashboard(null);
      setEditName('');
      
      // Trigger refresh if callback provided
      if (onRefresh) {
        onRefresh();
      }
    } catch (err) {
      console.error('Error editing dashboard:', err);
      setError('Failed to edit dashboard');
    } finally {
      setLoading(false);
    }
  };

  // Format date
  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Unknown date';
    }
  };

  // Handle menu actions
  const handleMenuClick = (event, dashboard) => {
    setAnchorEl(event.currentTarget);
    setSelectedDashboard(dashboard);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedDashboard(null);
  };

  const handleEditClick = () => {
    setEditingDashboard(selectedDashboard);
    setEditName(selectedDashboard.name);
    handleMenuClose();
  };

  const handleDeleteClick = () => {
    setShowDeleteDialog(true);
    handleMenuClose();
  };

  if (loading && dashboards.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mb: 3 
      }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 600, color: '#092f57' }}>
            Saved Dashboards
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Load your previously saved custom dashboards
          </Typography>
        </Box>
        
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadDashboards}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Dashboards List */}
      {dashboards.length === 0 ? (
        <Card sx={{ p: 4, textAlign: 'center', bgcolor: '#f8fafc' }}>
          <DashboardIcon sx={{ fontSize: 64, color: '#9ca3af', mb: 2 }} />
          <Typography variant="h6" color="textSecondary" gutterBottom>
            No saved dashboards
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Create and save a custom dashboard to see it here
          </Typography>
        </Card>
      ) : (
        <Grid container spacing={2}>
          {dashboards.map((dashboard) => (
            <Grid item xs={12} sm={6} md={4} key={dashboard.id}>
              <Card 
                sx={{ 
                  height: '100%',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: 3
                  }
                }}
                onClick={() => handleLoadDashboard(dashboard)}
              >
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <DashboardIcon sx={{ color: '#3b82f6', fontSize: 20 }} />
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleMenuClick(e, dashboard);
                      }}
                    >
                      <MoreIcon fontSize="small" />
                    </IconButton>
                  </Box>
                  
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 1, color: '#1f2937' }}>
                    {dashboard.name}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Chip 
                      label={`${dashboard.chart_count || 0} charts`}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', color: 'text.secondary' }}>
                    <TimeIcon sx={{ fontSize: 16, mr: 0.5 }} />
                    <Typography variant="caption">
                      {formatDate(dashboard.created_at)}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleEditClick}>
          <EditIcon sx={{ mr: 1 }} fontSize="small" />
          Edit Name
        </MenuItem>
        <MenuItem onClick={handleDeleteClick} sx={{ color: 'error.main' }}>
          <DeleteIcon sx={{ mr: 1 }} fontSize="small" />
          Delete
        </MenuItem>
      </Menu>

      {/* Edit Dialog */}
      <Dialog open={Boolean(editingDashboard)} onClose={() => setEditingDashboard(null)}>
        <DialogTitle>Edit Dashboard Name</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Dashboard Name"
            fullWidth
            variant="outlined"
            value={editName}
            onChange={(e) => setEditName(e.target.value)}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditingDashboard(null)}>Cancel</Button>
          <Button onClick={handleEditDashboard} variant="contained" disabled={!editName.trim()}>
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onClose={() => setShowDeleteDialog(false)}>
        <DialogTitle>Delete Dashboard</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{selectedDashboard?.name}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDeleteDialog(false)}>Cancel</Button>
          <Button onClick={handleDeleteDashboard} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SavedDashboards; 
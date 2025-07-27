/**
 * Cache Manager Component
 * Provides cache status and management functionality
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Alert
} from '@mui/material';
import StorageIcon from '@mui/icons-material/Storage';
import DeleteIcon from '@mui/icons-material/Delete';
import RefreshIcon from '@mui/icons-material/Refresh';
import InfoIcon from '@mui/icons-material/Info';

import dashboardCache from '../../services/dashboardCache';

const CacheManager = ({ open, onClose }) => {
  const [cacheStats, setCacheStats] = useState({});
  const [cacheEntries, setCacheEntries] = useState([]);

  const updateCacheInfo = () => {
    const stats = dashboardCache.getStats();
    setCacheStats(stats);
    
    // Get cache entries (this would need to be exposed by the cache service)
    // For now, we'll show basic stats
    setCacheEntries([]);
  };

  useEffect(() => {
    if (open) {
      updateCacheInfo();
    }
  }, [open]);

  const handleClearAllCache = () => {
    dashboardCache.clearAll();
    updateCacheInfo();
  };

  const handleClearExpired = () => {
    // This would need to be implemented in the cache service
    updateCacheInfo();
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <StorageIcon color="primary" />
        Cache Manager
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              Cache helps improve performance by storing frequently accessed data. 
              Data is automatically refreshed every 5 minutes.
            </Typography>
          </Alert>
          
          {/* Cache Statistics */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cache Statistics
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Chip 
                  label={`${cacheStats.size || 0} / ${cacheStats.maxSize || 50} entries`}
                  color="primary"
                  variant="outlined"
                />
                <Chip 
                  label={`${Math.round((cacheStats.size || 0) / (cacheStats.maxSize || 50) * 100)}% used`}
                  color="info"
                  variant="outlined"
                />
                <Chip 
                  label={`${Math.round((cacheStats.expiryTime || 300000) / 60000)} min expiry`}
                  color="secondary"
                  variant="outlined"
                />
              </Box>
            </CardContent>
          </Card>

          {/* Cache Actions */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cache Actions
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={updateCacheInfo}
                  size="small"
                >
                  Refresh Stats
                </Button>
                <Button
                  variant="outlined"
                  color="warning"
                  startIcon={<DeleteIcon />}
                  onClick={handleClearExpired}
                  size="small"
                >
                  Clear Expired
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={handleClearAllCache}
                  size="small"
                >
                  Clear All Cache
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>

        {/* Cache Entries List */}
        {cacheEntries.length > 0 ? (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cached Entries
              </Typography>
              <List dense>
                {cacheEntries.map((entry, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemText
                        primary={entry.key}
                        secondary={`Cached at ${formatTime(entry.timestamp)}`}
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          onClick={() => {/* Handle delete specific entry */}}
                          size="small"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                    {index < cacheEntries.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cached Entries
              </Typography>
              <Typography variant="body2" color="text.secondary">
                No cache entries to display. Cache entries will appear here as you navigate between dashboards.
              </Typography>
            </CardContent>
          </Card>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CacheManager; 
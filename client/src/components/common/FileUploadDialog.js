/**
 * File Upload Dialog Component
 * Reusable file upload dialog that can be triggered from header
 */

import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  LinearProgress,
  IconButton
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { uploadAndAnalyzeFile } from '../../services/api';

const FileUploadDialog = ({ open, onClose }) => {
  const navigate = useNavigate();
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState('');
  const [error, setError] = useState(null);

  // Handle file drop
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, []);

  // Handle drag over
  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  // Handle drag leave
  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  // Handle file input change
  const handleFileInputChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  // Handle file upload
  const handleFileUpload = async (file) => {
    if (!file) return;

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.xlsx') && !file.name.toLowerCase().endsWith('.xls')) {
      setError('Please upload only Excel files (.xlsx or .xls)');
      return;
    }

    setIsUploading(true);
    setUploadedFileName(file.name);
    setError(null);

    try {
      // Clear any previous dashboard state
      localStorage.removeItem('availableDashboards');
      
      const result = await uploadAndAnalyzeFile(file);
      
      console.log('📤 File upload result (dialog):', result);
      console.log('📤 File type detected (dialog):', result.file_type);
      console.log('📤 Available dashboards (dialog):', result.available_dashboards);
      
      // Close dialog and redirect to dashboard with the analysis results
      onClose();
      navigate('/dashboard', { 
        state: { 
          fileAnalysis: result,
          availableDashboards: result.available_dashboards 
        } 
      });
    } catch (err) {
      setError(err.message || 'Failed to upload and analyze file');
      setIsUploading(false);
      setUploadedFileName('');
    }
  };

  // Reset state when dialog closes
  const handleClose = () => {
    if (!isUploading) {
      setError(null);
      setUploadedFileName('');
      setIsDragOver(false);
      onClose();
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          bgcolor: '#f8fafc'
        }
      }}
    >
      <DialogTitle sx={{ 
        bgcolor: '#092f57', 
        color: 'white',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          Upload New Data File
        </Typography>
        <IconButton
          onClick={handleClose}
          disabled={isUploading}
          sx={{ color: 'white' }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            style={{ width: '100%' }}
          >
            <Paper
              elevation={0}
              sx={{
                border: `2px dashed ${isDragOver ? '#092f57' : '#ccc'}`,
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                bgcolor: isDragOver ? '#f8fafc' : 'transparent',
                transition: 'all 0.3s ease',
                cursor: isUploading ? 'default' : 'pointer',
                minHeight: 200,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                position: 'relative',
                '&:hover': {
                  borderColor: isUploading ? undefined : '#092f57',
                  bgcolor: isUploading ? undefined : '#f8fafc'
                }
              }}
              onDrop={isUploading ? undefined : handleDrop}
              onDragOver={isUploading ? undefined : handleDragOver}
              onDragLeave={isUploading ? undefined : handleDragLeave}
              onClick={isUploading ? undefined : () => document.getElementById('dialog-file-input').click()}
            >
              {!isUploading ? (
                <>
                  <UploadIcon sx={{ fontSize: 48, color: '#092f57', mb: 2 }} />
                  <Typography variant="h6" gutterBottom sx={{ color: '#092f57', fontWeight: 600 }}>
                    Drag and drop an Excel file here, or click to select
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Supported formats: .xlsx, .xls
                  </Typography>
                </>
              ) : (
                <Box sx={{ width: '100%' }}>
                  <CircularProgress 
                    size={48} 
                    sx={{ color: '#092f57', mb: 3 }} 
                  />
                  <Typography 
                    variant="h6" 
                    gutterBottom 
                    sx={{ color: '#092f57', fontWeight: 600, mb: 1 }}
                  >
                    Uploading File
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Your file is being uploaded to the server...
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    This should only take a few seconds.
                  </Typography>
                  
                  {uploadedFileName && (
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: '#666', 
                        mb: 3,
                        fontWeight: 500,
                        bgcolor: '#f5f5f5',
                        p: 1,
                        borderRadius: 1,
                        display: 'inline-block'
                      }}
                    >
                      {uploadedFileName}
                    </Typography>
                  )}
                  
                  <Box sx={{ width: '100%', mt: 2 }}>
                    <LinearProgress 
                      sx={{ 
                        height: 6, 
                        borderRadius: 3,
                        bgcolor: '#e0e0e0',
                        '& .MuiLinearProgress-bar': {
                          bgcolor: '#092f57'
                        }
                      }} 
                    />
                  </Box>
                </Box>
              )}
              
              <input
                id="dialog-file-input"
                type="file"
                accept=".xlsx,.xls"
                style={{ display: 'none' }}
                onChange={handleFileInputChange}
              />
            </Paper>

            {/* Error State */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <Alert severity="error" sx={{ mt: 3 }}>
                    {error}
                  </Alert>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 0 }}>
        <Button 
          onClick={handleClose} 
          disabled={isUploading}
          sx={{ 
            color: '#666',
            '&:hover': {
              bgcolor: '#f5f5f5'
            }
          }}
        >
          Cancel
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default FileUploadDialog; 
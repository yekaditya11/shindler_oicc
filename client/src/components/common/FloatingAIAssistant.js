import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Box,
  Typography,
  useTheme,
  useMediaQuery
} from '@mui/material';

const FloatingAIAssistant = ({ 
  isActive, 
  onToggle, 
  isLoading = false,
  hasNewInsights = false 
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [isHovered, setIsHovered] = useState(false);
  
  const handleClick = () => {
    onToggle();
  };

  // Simple hover and active animations for the GIF
  const gifVariants = {
    idle: {
      scale: 1,
      filter: "brightness(1)",
      transition: {
        duration: 0.3,
        ease: "easeInOut"
      }
    },
    hover: {
      scale: 1.1,
      filter: "brightness(1.2)",
      transition: {
        duration: 0.3,
        ease: "easeInOut"
      }
    },
    active: {
      scale: 1.15,
      filter: "brightness(1.3)",
      transition: {
        duration: 0.3,
        ease: "easeInOut"
      }
    },
    loading: {
      scale: [1, 1.1, 1],
      filter: ["brightness(1)", "brightness(1.4)", "brightness(1)"],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  // Notification ring animation for new insights
  const notificationVariants = {
    hidden: {
      scale: 0.8,
      opacity: 0
    },
    visible: {
      scale: [0.8, 1.2, 0.8],
      opacity: [0, 0.8, 0],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  return (
    <>
      {/* Main GIF-based AI assistant */}
      <motion.div
        className="floating-ai-assistant"
        style={{
          position: 'relative',
          cursor: 'pointer',
          border: 'none',
          outline: 'none',
          background: 'transparent',
          boxShadow: 'none',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
        onClick={handleClick}
        onHoverStart={() => setIsHovered(true)}
        onHoverEnd={() => setIsHovered(false)}
        title={isActive ? "Close AI Assistant" : "Open AI Assistant"}
        animate={{
          y: [0, -4, 0],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        {/* Main GIF image */}
        <motion.img
          src="/ai-insights-icon.gif"
          alt="AI Insights Assistant"
          style={{
            width: isMobile ? 42 : 48,
            height: isMobile ? 42 : 48,
            borderRadius: '50%',
            cursor: 'pointer',
            border: 'none',
            outline: 'none',
            boxSizing: 'border-box',
            objectFit: 'cover',
            WebkitTapHighlightColor: 'transparent',
            userSelect: 'none',
          }}
          initial="idle"
          animate={isLoading ? "loading" : isActive ? "active" : isHovered ? "hover" : "idle"}
          variants={gifVariants}
        />

        {/* Pulsing notification ring for new insights */}
        <AnimatePresence>
          {hasNewInsights && !isActive && (
            <motion.div
              style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                width: isMobile ? 52 : 58,
                height: isMobile ? 52 : 58,
                borderRadius: '50%',
                border: '2px solid rgba(96, 165, 250, 0.6)',
                transform: 'translate(-50%, -50%)',
                pointerEvents: 'none',
              }}
              initial="hidden"
              animate="visible"
              exit="hidden"
              variants={notificationVariants}
            />
          )}
        </AnimatePresence>

        {/* Loading overlay when processing */}
        <AnimatePresence>
          {isLoading && (
            <motion.div
              style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                width: isMobile ? 42 : 48,
                height: isMobile ? 42 : 48,
                borderRadius: '50%',
                background: 'rgba(59, 130, 246, 0.3)',
                transform: 'translate(-50%, -50%)',
                pointerEvents: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <motion.div
                style={{
                  width: 18,
                  height: 18,
                  border: '2px solid rgba(255, 255, 255, 0.3)',
                  borderTop: '2px solid rgba(255, 255, 255, 0.8)',
                  borderRadius: '50%',
                }}
                animate={{ rotate: 360 }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  ease: "linear"
                }}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </>
  );
};

export default FloatingAIAssistant;

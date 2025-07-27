import React from 'react';
import {
  useTheme,
  useMediaQuery
} from '@mui/material';

const FloatingAIAssistant = ({ 
  isActive, 
  onToggle
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const handleClick = () => {
    onToggle();
  };

  return (
    <div
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
      title={isActive ? "Close AI Assistant" : "Open AI Assistant"}
    >
      {/* Simple static GIF image */}
      <img
        src="/ai-insights-icon.gif"
        alt="AI Insights Assistant"
        style={{
          width: isMobile ? 60 : 72,
          height: isMobile ? 60 : 72,
          borderRadius: '50%',
          cursor: 'pointer',
          border: 'none !important',
          outline: 'none !important',
          boxSizing: 'border-box',
          objectFit: 'cover',
          WebkitTapHighlightColor: 'transparent',
          userSelect: 'none',
          backgroundColor: 'white',
          boxShadow: 'none !important',
          padding: '0',
          margin: '0',
          display: 'block',
        }}
      />
    </div>
  );
};

export default FloatingAIAssistant;

/**
 * Style selector component - FD-inspired professional controls
 */
import { useEffect } from 'react';
import { useAtom, useAtomValue } from 'jotai';
import { Box, ToggleButton, ToggleButtonGroup, Typography, Chip } from '@mui/material';
import PaletteIcon from '@mui/icons-material/Palette';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { stylePreferenceAtom, sessionIdAtom } from '../state/atoms';
import { setStylePreference, getStylePreference } from '../api/client';
import type { ChartStyle } from '../types';

const STYLE_INFO = {
  fd: {
    label: 'FD',
    fullName: 'Financieele Dagblad',
    colors: {
      primary: '#379596',
      background: '#ffeadb',
      content: '#191919',
    },
  },
  bnr: {
    label: 'BNR',
    fullName: 'BNR Nieuwsradio',
    colors: {
      primary: '#ffd200',
      background: '#fff',
      content: '#000',
    },
  },
};

export default function StyleSelector() {
  const [style, setStyle] = useAtom(stylePreferenceAtom);
  const sessionId = useAtomValue(sessionIdAtom);

  useEffect(() => {
    const loadPreference = async () => {
      try {
        const backendStyle = await getStylePreference(sessionId);
        if (backendStyle !== style) {
          setStyle(backendStyle);
        }
      } catch (err) {
        console.error('Failed to load style preference:', err);
      }
    };
    loadPreference();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  const handleChange = async (_: React.MouseEvent<HTMLElement>, newStyle: ChartStyle | null) => {
    if (newStyle && newStyle !== style) {
      setStyle(newStyle);
      try {
        await setStylePreference(sessionId, newStyle);
      } catch (err) {
        console.error('Failed to save style preference:', err);
      }
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <PaletteIcon sx={{ fontSize: 20, color: 'primary.main' }} />
        <Typography variant="subtitle2" fontWeight={600}>
          Chart Style
        </Typography>
        <Chip
          label="Persistent"
          size="small"
          sx={{
            height: 20,
            fontSize: '0.7rem',
            bgcolor: 'rgba(55, 149, 150, 0.1)',
            color: 'primary.main',
          }}
        />
      </Box>

      <ToggleButtonGroup
        value={style}
        exclusive
        onChange={handleChange}
        aria-label="chart style"
        fullWidth
        sx={{
          '& .MuiToggleButton-root': {
            textTransform: 'none',
            border: '1px solid #e0e0e0',
            '&.Mui-selected': {
              bgcolor: 'primary.main',
              color: '#ffffff',
              '&:hover': {
                bgcolor: 'primary.dark',
              },
            },
          },
        }}
      >
        {Object.entries(STYLE_INFO).map(([key, info]) => (
          <ToggleButton key={key} value={key} aria-label={info.fullName}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                py: 0.5,
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Typography variant="body2" fontWeight={600}>
                    {info.label}
                  </Typography>
                  {style === key && <CheckCircleIcon sx={{ fontSize: 16, opacity: 0.9 }} />}
                </Box>
                <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
                  <Box
                    sx={{
                      width: 14,
                      height: 14,
                      borderRadius: '2px',
                      bgcolor: info.colors.primary,
                      border:
                        style === key
                          ? '1.5px solid rgba(255,255,255,0.8)'
                          : '1px solid rgba(0,0,0,0.1)',
                    }}
                  />
                  <Box
                    sx={{
                      width: 14,
                      height: 14,
                      borderRadius: '2px',
                      bgcolor: info.colors.background,
                      border:
                        style === key
                          ? '1.5px solid rgba(255,255,255,0.8)'
                          : '1px solid rgba(0,0,0,0.1)',
                    }}
                  />
                </Box>
              </Box>
            </Box>
          </ToggleButton>
        ))}
      </ToggleButtonGroup>

      <Box
        sx={{
          mt: 2,
          p: 1.5,
          bgcolor: STYLE_INFO[style].colors.background,
          borderRadius: 1,
          border: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Typography
          variant="caption"
          sx={{
            color: STYLE_INFO[style].colors.content,
            display: 'block',
            fontWeight: 500,
          }}
        >
          <strong>{STYLE_INFO[style].fullName}</strong> — Charts use this color scheme
        </Typography>
      </Box>
    </Box>
  );
}

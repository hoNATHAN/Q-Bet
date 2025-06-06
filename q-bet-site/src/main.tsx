import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import { AppRouter } from './routes/AppRouter.tsx';

// TODO: add the theme here?
//
// background light: #fbf7f4
// background dark: #121111
// light primary: #39a77f
// dark primary: #26c289

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppRouter />
  </StrictMode>
);

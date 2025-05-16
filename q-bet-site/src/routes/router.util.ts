import { createRouter } from '@tanstack/react-router';
import { rootRoute } from './__root';
import {
  aboutRoute,
  analyticsRoute,
  docsRoute,
  financesRoute,
  gymnasiumRoute,
  homeRoute,
  profileRoute,
  settingsRoute,
} from './routes';

const routeTree = rootRoute.addChildren([
  homeRoute,
  financesRoute,
  analyticsRoute,
  settingsRoute,
  gymnasiumRoute,
  docsRoute,
  aboutRoute,
  profileRoute,
]);

export const router = createRouter({ routeTree, defaultPreload: 'intent' });

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

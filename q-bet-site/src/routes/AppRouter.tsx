import { RouterProvider } from '@tanstack/react-router';
import { router } from './router.util';

export const AppRouter = () => {
  return <RouterProvider router={router} />;
};

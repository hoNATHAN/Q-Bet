import { RouterProvider } from '@tanstack/react-router'
import App from '@/App'
import { router } from './router.util'

export const AppRouter = () => {
  return (
    <>
      <RouterProvider router={router} />
      <App />
    </>
  )
}

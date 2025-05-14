import { Router, RouterProvider } from '@tanstack/react-router'
import { rootRoute } from './__root'
import App from '@/App'
import { homeRoute, profileRoute } from './routes'

const routeTree = rootRoute.addChildren([homeRoute, profileRoute])
const router = new Router({ routeTree, defaultPreload: 'intent' })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

export const AppRouter = () => {
  return (
    <>
      <RouterProvider router={router} />
      <App />
    </>
  )
}

import { Router, RouterProvider } from '@tanstack/react-router'
import { rootRoute } from './__root'
import App from '@/App'
import {
  aboutRoute,
  analyticsRoute,
  docsRoute,
  financesRoute,
  gymnasiumRoute,
  homeRoute,
  profileRoute,
  settingsRoute,
} from './routes'

const routeTree = rootRoute.addChildren([
  homeRoute,
  financesRoute,
  analyticsRoute,
  settingsRoute,
  gymnasiumRoute,
  docsRoute,
  aboutRoute,
  profileRoute,
])
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

import { createRoute, createRootRoute } from '@tanstack/react-router'
import { rootRoute } from './__root'
import { Home } from 'lucide-react'
import { Finances } from '@/pages/finances'
import { Analytics } from '@/pages/analytics'

export const redirectRoute = createRootRoute({
  component: () => <div>Home</div>,
})

export const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/home',
  component: () => (
    <div>
      <Home />
    </div>
  ),
})

export const financesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/finances',
  component: () => (
    <div>
      <Finances />
    </div>
  ),
})

export const analyticsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/analytics',
  component: () => (
    <div>
      <Analytics />
    </div>
  ),
})

export const profileRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/profile',
  component: () => <div>Profile</div>,
})

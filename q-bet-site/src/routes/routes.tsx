import { createRoute } from '@tanstack/react-router'
import { rootRoute } from './__root'
import {
  About,
  Analytics,
  Docs,
  Finances,
  Gymnasium,
  Home,
  Profile,
  Settings,
} from '@/pages'

// =================
//  Side Bar Routes
// =================

export const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/home',
  component: () => <Home />,
})

export const financesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/finances',
  component: () => <Finances />,
})

export const analyticsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/analytics',
  component: () => <Analytics />,
})

export const settingsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/settings',
  component: () => <Settings />,
})

// =================
//  Top Bar Routes
// =================

export const gymnasiumRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/gymnasium',
  component: () => <Gymnasium />,
})
export const docsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/docs',
  component: () => <Docs />,
})
export const aboutRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/about',
  component: () => <About />,
})

export const profileRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/profile',
  component: () => <Profile />,
})

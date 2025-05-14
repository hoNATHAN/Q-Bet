import { createRoute } from '@tanstack/react-router'
import { rootRoute } from './__root'

export const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: () => <div>Home</div>,
})

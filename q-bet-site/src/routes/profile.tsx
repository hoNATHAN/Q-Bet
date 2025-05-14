import { Route } from '@tanstack/react-router'
import { rootRoute } from './__root'

export const profileRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/profile',
  component: () => <div>Posts</div>,
})

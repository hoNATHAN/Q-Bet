import './App.css'
import { AppSidebar } from './components/app-sidebar'
import { ThemeProvider } from './components/theme-provider'
import { TopNavBar } from './components/top-nav-bar'
import { SidebarProvider, SidebarTrigger } from './components/ui/sidebar'
import { Home } from './pages/Home'

function App() {
  return (
    <>
      <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
        <SidebarProvider>
          <AppSidebar />
          <TopNavBar />
          {/* <Home /> */}
        </SidebarProvider>
      </ThemeProvider>
    </>
  )
}

export default App

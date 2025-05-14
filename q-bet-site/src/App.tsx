import './App.css'
import { AppSidebar } from './components/app-sidebar'
import { ThemeProvider } from './components/theme-provider'
import { TopNavBar } from './components/top-nav-bar'
import { SidebarProvider } from './components/ui/sidebar'

function App() {
  return (
    <>
      <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
        <SidebarProvider>
          <AppSidebar />
          <TopNavBar />
        </SidebarProvider>
      </ThemeProvider>
    </>
  )
}

export default App

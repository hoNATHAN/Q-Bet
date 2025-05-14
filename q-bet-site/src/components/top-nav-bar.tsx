import { useTheme } from './theme-provider'
import {
  Menubar,
  MenubarContent,
  MenubarItem,
  MenubarMenu,
  MenubarSeparator,
  MenubarSub,
  MenubarSubContent,
  MenubarSubTrigger,
  MenubarTrigger,
} from '@/components/ui/menubar'
import { SidebarTrigger } from './ui/sidebar'
import { Button } from './ui/button'
import {
  BookMarked,
  Github,
  Lightbulb,
  Pencil,
  School,
  User,
} from 'lucide-react'
import { IconAvatar } from './ui/avataricon'
import { router } from '@/routes/router.util'

export const TopNavBar = () => {
  const { theme, setTheme } = useTheme()

  const onGymnasiumClick = () => {
    router.navigate({ to: '/gymnasium' })
  }

  const onLogoClick = () => {
    router.navigate({ to: '/about' })
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-50">
      <Menubar className="rounded-none">
        <MenubarMenu>
          <SidebarTrigger />
        </MenubarMenu>
        <MenubarMenu>
          <MenubarTrigger onClick={onLogoClick}>
            <div className="h-5 flex flex-row gap-1 font-">
              <img src="/public/logo-only.png" alt="logo" />
              Q-BET
            </div>
          </MenubarTrigger>
        </MenubarMenu>
        <MenubarMenu>
          <MenubarTrigger onClick={onGymnasiumClick}>Gymnasium</MenubarTrigger>
        </MenubarMenu>
        <MenubarMenu>
          <MenubarTrigger>Docs</MenubarTrigger>
          <MenubarContent>
            <MenubarItem>
              <a
                className="flex flex-row gap-2 items-center"
                href="https://github.com/hoNATHAN/Q-Bet"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Github />
                GitHub
              </a>
            </MenubarItem>
            <MenubarItem className="flex flex-row">
              <a
                className="flex flex-row gap-2 items-center"
                href="https://github.com/hoNATHAN/Q-Bet"
                target="_blank"
                rel="noopener noreferrer"
              >
                <BookMarked />
                Research Paper
              </a>
            </MenubarItem>
            <MenubarItem className="flex flex-row">
              <a
                className="flex flex-row gap-2 items-center"
                href="https://github.com/hoNATHAN/Q-Bet"
                target="_blank"
                rel="noopener noreferrer"
              >
                <School />
                Course Information
              </a>
            </MenubarItem>
            <MenubarItem className="flex flex-row">
              <a
                className="flex flex-row gap-2 items-center"
                href="https://github.com/hoNATHAN/Q-Bet"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Pencil />
                References
              </a>
            </MenubarItem>
          </MenubarContent>
        </MenubarMenu>
        <MenubarMenu>
          <MenubarTrigger>Profile</MenubarTrigger>
          <MenubarContent>
            <MenubarItem>
              <IconAvatar icon={User} size="sm" />
              Current User
            </MenubarItem>
            <MenubarSeparator />
            <MenubarSub>
              <MenubarSubTrigger>Export</MenubarSubTrigger>
              <MenubarSubContent>
                <MenubarItem>Export All</MenubarItem>
                <MenubarItem>Export Finances</MenubarItem>
                <MenubarItem>Export Analytics</MenubarItem>
                <MenubarItem>Export Model</MenubarItem>
              </MenubarSubContent>
            </MenubarSub>
            <MenubarSeparator />
            <MenubarItem>Log In</MenubarItem>
            <MenubarItem>Sign Out</MenubarItem>
          </MenubarContent>
        </MenubarMenu>
        <MenubarMenu>
          <Button
            className="bg-inherit text-inherit"
            size="sm"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          >
            <Lightbulb />
          </Button>
        </MenubarMenu>
      </Menubar>
    </div>
  )
}

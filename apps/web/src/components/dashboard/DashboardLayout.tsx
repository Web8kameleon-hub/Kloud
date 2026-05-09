'use client';

import { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  SidebarProvider,
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarTrigger,
  SidebarInset,
} from '@/components/ui/sidebar';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  LayoutDashboard,
  Database,
  BarChart3,
  Settings,
  Download,
  Bell,
  LogOut,
  User,
  ChevronUp,
  Zap,
  Activity,
  Layers,
  Shield,
} from 'lucide-react';

interface DashboardLayoutProps {
  children: ReactNode;
  variant?: 'user' | 'admin';
  user?: {
    name: string;
    email: string;
    avatar?: string;
    role?: string;
  };
  onLogout?: () => void;
}

const userNavItems = [
  {
    group: 'Main',
    items: [
      { title: 'Overview', icon: LayoutDashboard, href: '/dashboard', badge: null },
      { title: 'Data Sources', icon: Database, href: '/dashboard?tab=sources', badge: null },
      { title: 'Metrics', icon: BarChart3, href: '/dashboard?tab=metrics', badge: null },
      { title: 'Export', icon: Download, href: '/dashboard?tab=export', badge: null },
    ],
  },
  {
    group: 'Modules',
    items: [
      { title: 'Curiosity Ocean', icon: Zap, href: '/modules/curiosity-ocean', badge: 'New' },
      { title: 'EEG Analysis', icon: Activity, href: '/modules/eeg-analysis', badge: null },
      { title: 'Neural Synthesizer', icon: Layers, href: '/modules/neural-synthesizer', badge: null },
    ],
  },
];

const adminNavItems = [
  {
    group: 'Infrastructure',
    items: [
      { title: 'System Overview', icon: LayoutDashboard, href: '/admin', badge: null },
      { title: 'ASI Trinity', icon: Zap, href: '/admin?section=asi', badge: 'Live' },
      { title: 'Tech Stack', icon: Layers, href: '/admin?section=tech', badge: null },
      { title: 'Modules', icon: Database, href: '/admin?section=modules', badge: null },
    ],
  },
  {
    group: 'Management',
    items: [
      { title: 'Users', icon: User, href: '/admin/users', badge: null },
      { title: 'Security', icon: Shield, href: '/admin/security', badge: null },
      { title: 'Settings', icon: Settings, href: '/admin/settings', badge: null },
    ],
  },
];

export function DashboardLayout({ 
  children, 
  variant = 'user', 
  user,
  onLogout 
}: DashboardLayoutProps) {
  const pathname = usePathname();
  const navItems = variant === 'admin' ? adminNavItems : userNavItems;
  
  const defaultUser = {
    name: variant === 'admin' ? 'Administrator' : 'User',
    email: variant === 'admin' ? 'admin@kloud.com' : 'user@kloud.com',
    role: variant === 'admin' ? 'Admin' : 'User',
  };

  const currentUser = user || defaultUser;

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-gradient-to-br from-neutral-950 via-neutral-900 to-neutral-950">
        <Sidebar className="border-r border-neutral-800">
          <SidebarHeader className="border-b border-neutral-800 px-4 py-4">
            <Link href="/" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gray-300 to-white flex items-center justify-center shadow-lg">
                <span className="text-xl">🧠</span>
              </div>
              <div>
                <h1 className="font-bold text-lg text-white">Kloud</h1>
                <p className="text-xs text-neutral-400">
                  {variant === 'admin' ? 'Admin Panel' : 'Dashboard'}
                </p>
              </div>
            </Link>
          </SidebarHeader>

          <SidebarContent className="px-2 py-4">
            {navItems.map((group) => (
              <SidebarGroup key={group.group}>
                <SidebarGroupLabel className="text-neutral-500 uppercase text-xs font-semibold tracking-wider px-3 mb-2">
                  {group.group}
                </SidebarGroupLabel>
                <SidebarGroupContent>
                  <SidebarMenu>
                    {group.items.map((item) => {
                      const isActive = pathname === item.href || (pathname?.startsWith(item.href + '/') ?? false);
                      return (
                        <SidebarMenuItem key={item.title}>
                          <SidebarMenuButton
                            asChild
                            isActive={isActive}
                            className={`
                              w-full justify-start gap-3 px-3 py-2.5 rounded-lg transition-all
                              ${isActive 
                                ? 'bg-white/10 text-white border border-white/20' 
                                : 'text-neutral-400 hover:text-white hover:bg-neutral-800/50'
                              }
                            `}
                          >
                            <Link href={item.href}>
                              <item.icon className="w-5 h-5" />
                              <span className="flex-1">{item.title}</span>
                              {item.badge && (
                                <Badge 
                                  variant="secondary" 
                                  className="bg-white/20 text-white text-xs"
                                >
                                  {item.badge}
                                </Badge>
                              )}
                            </Link>
                          </SidebarMenuButton>
                        </SidebarMenuItem>
                      );
                    })}
                  </SidebarMenu>
                </SidebarGroupContent>
              </SidebarGroup>
            ))}
          </SidebarContent>

          <SidebarFooter className="border-t border-neutral-800 p-4">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-3 w-full p-2 rounded-lg hover:bg-neutral-800/50 transition-colors">
                  <Avatar className="w-9 h-9">
                    <AvatarImage src={'avatar' in currentUser ? currentUser.avatar : undefined} />
                    <AvatarFallback className="bg-gradient-to-br from-gray-400 to-white text-black text-sm">
                      {currentUser.name.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 text-left">
                    <p className="text-sm font-medium text-white">{currentUser.name}</p>
                    <p className="text-xs text-neutral-400">{currentUser.role}</p>
                  </div>
                  <ChevronUp className="w-4 h-4 text-neutral-400" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56 bg-neutral-900 border-neutral-700">
                <DropdownMenuLabel className="text-neutral-400">My Account</DropdownMenuLabel>
                <DropdownMenuSeparator className="bg-neutral-700" />
                <DropdownMenuItem className="text-slate-300 hover:text-white hover:bg-neutral-800">
                  <User className="w-4 h-4 mr-2" />
                  Profile
                </DropdownMenuItem>
                <DropdownMenuItem className="text-slate-300 hover:text-white hover:bg-neutral-800">
                  <Settings className="w-4 h-4 mr-2" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuItem className="text-slate-300 hover:text-white hover:bg-neutral-800">
                  <Bell className="w-4 h-4 mr-2" />
                  Notifications
                </DropdownMenuItem>
                <DropdownMenuSeparator className="bg-neutral-700" />
                <DropdownMenuItem 
                  className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                  onClick={onLogout}
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  {variant === 'admin' ? 'Logout' : 'Sign Out'}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarFooter>
        </Sidebar>

        <SidebarInset className="flex-1">
          {/* Top Bar */}
          <header className="sticky top-0 z-40 flex items-center gap-4 border-b border-neutral-800 bg-neutral-900/50 backdrop-blur-xl px-6 py-4">
            <SidebarTrigger className="text-neutral-400 hover:text-white" />
            <Separator orientation="vertical" className="h-6 bg-neutral-700" />
            <div className="flex-1" />
            
            {/* Status Indicator */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-green-500/20 text-green-400 text-sm">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              <span className="hidden sm:inline">
                {variant === 'admin' ? 'Systems Online' : 'Connected'}
              </span>
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 p-6">
            {children}
          </main>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}

export default DashboardLayout;


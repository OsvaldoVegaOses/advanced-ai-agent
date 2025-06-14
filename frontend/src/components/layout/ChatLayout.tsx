'use client';

import { useState, useEffect } from 'react';
import { useAppStore } from '../../store/useAppStore';
import Sidebar from './Sidebar';
import NotificationContainer from '../ui/NotificationContainer';
import { Bars3Icon } from '@heroicons/react/24/outline';

interface ChatLayoutProps {
  children: React.ReactNode;
}

export default function ChatLayout({ children }: ChatLayoutProps) {
  const { ui, toggleSidebar } = useAppStore();
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <div className="h-full flex bg-secondary-50">
      {/* Sidebar */}
      <div
        className={`
          ${ui.sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          ${isMobile ? 'fixed inset-y-0 left-0 z-50 w-80' : 'relative w-80'}
          transition-transform duration-300 ease-in-out
        `}
      >
        <Sidebar />
      </div>

      {/* Overlay para móvil */}
      {isMobile && ui.sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={toggleSidebar}
        />
      )}

      {/* Contenido principal */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header móvil */}
        {isMobile && !ui.sidebarOpen && (
          <div className="bg-white border-b border-secondary-200 px-4 py-3 flex items-center">
            <button
              onClick={toggleSidebar}
              className="p-2 rounded-lg hover:bg-secondary-100 transition-colors"
            >
              <Bars3Icon className="w-5 h-5 text-secondary-600" />
            </button>
            <h1 className="ml-3 text-lg font-semibold text-secondary-900">
              Advanced AI Agent
            </h1>
          </div>
        )}

        {/* Contenido */}
        <main className="flex-1 overflow-hidden">
          {children}
        </main>
      </div>

      {/* Notificaciones */}
      <NotificationContainer />
    </div>
  );
}
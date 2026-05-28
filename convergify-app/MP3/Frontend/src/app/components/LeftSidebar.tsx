import { useState } from 'react';
import { FileText, Briefcase, BarChart3, Activity, ChevronLeft, ChevronRight, Moon, Sun } from 'lucide-react';
import { useTheme } from '@/app/contexts/ThemeContext';

interface LeftSidebarProps {
  activeTab: 'resume' | 'jobs' | 'analysis';
  onTabChange: (tab: 'resume' | 'jobs' | 'analysis') => void;
  isExpanded: boolean;
  onToggleExpanded: (expanded: boolean) => void;
}

export function LeftSidebar({ activeTab, onTabChange, isExpanded, onToggleExpanded }: LeftSidebarProps) {
  const { theme, toggleTheme } = useTheme();

  const tabs = [
    { id: 'resume' as const, label: 'Resume', icon: FileText },
    { id: 'jobs' as const, label: 'Jobs', icon: Briefcase },
    { id: 'analysis' as const, label: 'Analysis', icon: BarChart3 },
  ];

  return (
    <div
      className={`fixed left-0 top-0 h-screen flex flex-col bg-white dark:bg-gray-900 text-gray-900 dark:text-white border-r border-gray-200 dark:border-gray-700 transition-all duration-300 z-10 ${
        isExpanded ? 'w-60' : 'w-20'
      }`}
    >
      {/* Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
        {isExpanded && (
          <h2 className="text-sm font-semibold text-gray-900 dark:text-white">Navigation</h2>
        )}
        <button
          onClick={() => onToggleExpanded(!isExpanded)}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
        >
          {isExpanded ? (
            <ChevronLeft className="w-4 h-4 text-gray-600 dark:text-gray-400" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-600 dark:text-gray-400" />
          )}
        </button>
      </div>

      {/* Navigation Tabs */}
      <nav className="flex-1 p-3 overflow-y-auto">
        <div className="space-y-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all ${
                  isActive
                    ? 'bg-blue-600 dark:bg-blue-600 text-white'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white'
                }`}
                title={!isExpanded ? tab.label : undefined}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {isExpanded && (
                  <span className="text-sm font-medium">{tab.label}</span>
                )}
              </button>
            );
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-3 flex-shrink-0">
        {/* Dark Mode Toggle */}
        <button
          onClick={toggleTheme}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
          title={!isExpanded ? (theme === 'light' ? 'Dark Mode' : 'Light Mode') : undefined}
        >
          {theme === 'light' ? (
            <Moon className="w-5 h-5 flex-shrink-0" />
          ) : (
            <Sun className="w-5 h-5 flex-shrink-0" />
          )}
          {isExpanded && (
            <span className="text-sm font-medium">
              {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
            </span>
          )}
        </button>

        {/* Version Info */}
        {isExpanded && (
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">Career Management OS</p>
            <p className="text-xs text-gray-400 dark:text-gray-500">v1.0.0</p>
          </div>
        )}
      </div>
    </div>
  );
}
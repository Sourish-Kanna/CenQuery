"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { LogOut, Sparkles, User, Moon, Sun } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useTheme } from "@/components/theme/ThemeProvider";

export default function Navbar() {
  const router = useRouter();
  const [username, setUsername] = useState<string | null>(null);
  const { theme, toggleTheme } = useTheme();

  useEffect(() => {
    // Get user info from localStorage
    const userStr = localStorage.getItem("cenquery_user");
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        setUsername(user.username);
      } catch (e) {
        console.error("Failed to parse user data:", e);
      }
    }
  }, []);

  const handleLogout = () => {
    // Clear session
    localStorage.removeItem("cenquery_user");
    // Redirect to login
    router.push("/login");
  };

  return (
    <header className="w-full h-16 border-b bg-white/80 dark:bg-gray-900/80 backdrop-blur-md flex items-center justify-between px-6 shadow-sm sticky top-0 z-50 transition-colors">
      <div className="flex items-center gap-3">
        <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg shadow-md">
          <Sparkles className="text-white" size={20} />
        </div>
        <div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            CenQuery
          </h1>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Indian Census Query System
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Dark Mode Toggle */}
        <Button
          variant="outline"
          size="sm"
          onClick={toggleTheme}
          className="flex gap-2 dark:border-gray-700 dark:hover:bg-gray-800 transition-colors"
          aria-label="Toggle dark mode"
        >
          {theme === "dark" ? (
            <>
              <Sun size={16} />
              <span className="hidden sm:inline">Light</span>
            </>
          ) : (
            <>
              <Moon size={16} />
              <span className="hidden sm:inline">Dark</span>
            </>
          )}
        </Button>

        {username && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 dark:bg-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-800">
            <User size={16} className="text-blue-600 dark:text-blue-400" />
            <span className="text-sm font-medium text-blue-900 dark:text-blue-200">{username}</span>
          </div>
        )}
        
        <Button 
          variant="outline" 
          size="sm" 
          className="flex gap-2 hover:bg-red-50 hover:text-red-600 hover:border-red-300 dark:hover:bg-red-900/20 dark:hover:text-red-400 dark:border-gray-700 transition-colors"
          onClick={handleLogout}
        >
          <LogOut size={16} />
          <span className="hidden sm:inline">Logout</span>
        </Button>
      </div>
    </header>
  );
}

"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { LogOut, Sparkles, User } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function Navbar() {
  const router = useRouter();
  const [username, setUsername] = useState<string | null>(null);

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
    <header className="w-full h-16 border-b bg-white/80 backdrop-blur-md flex items-center justify-between px-6 shadow-sm sticky top-0 z-50">
      <div className="flex items-center gap-3">
        <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg shadow-md">
          <Sparkles className="text-white" size={20} />
        </div>
        <div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            CenQuery
          </h1>
          <p className="text-xs text-gray-500">
            Indian Census Query System
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {username && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 rounded-lg border border-blue-200">
            <User size={16} className="text-blue-600" />
            <span className="text-sm font-medium text-blue-900">{username}</span>
          </div>
        )}
        <Button 
          variant="outline" 
          size="sm" 
          className="flex gap-2 hover:bg-red-50 hover:text-red-600 hover:border-red-300 transition-colors"
          onClick={handleLogout}
        >
          <LogOut size={16} />
          Logout
        </Button>
      </div>
    </header>
  );
}

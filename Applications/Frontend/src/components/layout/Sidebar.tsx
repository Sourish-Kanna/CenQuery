"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Database, Search, BarChart3, Info, Menu, X } from "lucide-react";
import clsx from "clsx";
import { useState } from "react";

export default function Sidebar() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);

  const navItems = [
    { name: "Dashboard", href: "/dashboard", icon: BarChart3, color: "blue" },
    { name: "Query", href: "/query", icon: Search, color: "purple" },
    { name: "Schema", href: "/schema", icon: Database, color: "green" },
    { name: "About", href: "/about", icon: Info, color: "orange" },
  ];

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden fixed bottom-4 right-4 z-50 bg-gradient-to-br from-blue-600 to-purple-600 text-white p-4 rounded-full shadow-2xl hover:shadow-3xl transition-all"
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-40 backdrop-blur-sm"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={clsx(
          "w-64 border-r border-gray-200 dark:border-gray-700 min-h-screen p-4 bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 transition-all duration-300 z-40",
          "md:relative md:translate-x-0",
          isOpen ? "fixed translate-x-0" : "fixed -translate-x-full"
        )}
      >
        <p className="text-xs text-gray-500 dark:text-gray-400 mb-4 uppercase tracking-wide font-semibold">
          Main Menu
        </p>

        <nav className="flex flex-col gap-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setIsOpen(false)}
                className={clsx(
                  "flex items-center gap-3 px-4 py-3 rounded-xl text-sm transition-all duration-200",
                  isActive
                    ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg"
                    : "text-gray-700 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-700 hover:shadow-md"
                )}
              >
                <Icon size={20} />
                <span className="font-medium">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
    </>
  );
}

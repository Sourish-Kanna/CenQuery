"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Database, Search, BarChart3, Info } from "lucide-react";
import clsx from "clsx";

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Dashboard", href: "/dashboard", icon: BarChart3 },
    { name: "Query", href: "/query", icon: Search },
    { name: "Schema", href: "/schema", icon: Database },
    { name: "About", href: "/about", icon: Info },
  ];

  return (
    <aside className="w-64 border-r min-h-screen p-4 bg-gray-50">
      <p className="text-xs text-gray-400 mb-3 uppercase tracking-wide">
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
              className={clsx(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                isActive
                  ? "bg-blue-100 text-blue-700 font-medium"
                  : "text-gray-700 hover:bg-gray-200"
              )}
            >
              <Icon size={18} />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

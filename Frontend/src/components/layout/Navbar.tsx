"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { LogOut } from "lucide-react";

export default function Navbar() {
  return (
    <header className="w-full h-14 border-b flex items-center justify-between px-6 bg-white">
      <div>
        <h1 className="text-xl font-semibold text-blue-700">
          CenQuery
        </h1>
        <p className="text-xs text-gray-500">
          Indian Census Query System
        </p>
      </div>

      <Link href="/login">
        <Button variant="outline" size="sm" className="flex gap-2">
          <LogOut size={16} />
          Logout
        </Button>
      </Link>
    </header>
  );
}

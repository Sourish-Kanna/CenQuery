"use client";

import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";
import QueryPanel from "@/components/query/QueryPanel";
import Footer from "@/components/layout/Footer";
import AuthGuard from "@/components/auth/AuthGuard";

export default function QueryPage() {
  return (
    <AuthGuard>
      <div className="flex flex-col h-screen">
        <Navbar />

        <div className="flex flex-1 overflow-hidden">
          <Sidebar />

          <main className="flex-1 p-6 bg-gradient-to-br from-gray-50 to-blue-50 overflow-y-auto">
            <div className="max-w-7xl mx-auto">
              <div className="mb-6">
                <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Query Census Data
                </h2>
                <p className="text-gray-600">
                  Ask questions in natural language and get instant insights
                </p>
              </div>

              <div className="bg-white/80 backdrop-blur-sm p-8 rounded-xl shadow-lg border border-gray-200">
                <QueryPanel />
              </div>
            </div>
          </main>
        </div>
        <Footer />
      </div>
    </AuthGuard>
  );
}

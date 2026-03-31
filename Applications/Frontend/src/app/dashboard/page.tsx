"use client";

import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";
import Footer from "@/components/layout/Footer";
import AuthGuard from "@/components/auth/AuthGuard";
import { Database, Layers, Cpu, BarChart3, Activity, TrendingUp } from "lucide-react";

export default function DashboardPage() {
  return (
    <AuthGuard>
      <div className="flex flex-col h-screen bg-white dark:bg-gray-900">
        <Navbar />

        <div className="flex flex-1 overflow-hidden">
          <Sidebar />

          <main className="flex-1 p-6 bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 overflow-y-auto">
            <div className="max-w-7xl mx-auto">
              <div className="mb-8">
                <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  System Dashboard
                </h2>
                <p className="text-gray-600 dark:text-gray-300">
                  Overview of CenQuery system and capabilities
                </p>
              </div>

              {/* Top Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-xl shadow-lg text-white hover:shadow-2xl transition-all hover:-translate-y-1">
                  <div className="flex items-center justify-between mb-4">
                    <Database className="text-white/80" size={32} />
                    <Activity className="text-white/60" size={20} />
                  </div>
                  <p className="text-blue-100 text-sm mb-1">Total Tables</p>
                  <p className="text-3xl font-bold">37</p>
                </div>

                <div className="bg-gradient-to-br from-green-500 to-green-600 p-6 rounded-xl shadow-lg text-white hover:shadow-2xl transition-all hover:-translate-y-1">
                  <div className="flex items-center justify-between mb-4">
                    <Layers className="text-white/80" size={32} />
                    <TrendingUp className="text-white/60" size={20} />
                  </div>
                  <p className="text-green-100 text-sm mb-1">Data Domains</p>
                  <p className="text-lg font-semibold">Population, Education, Agriculture</p>
                </div>

                <div className="bg-gradient-to-br from-purple-500 to-purple-600 p-6 rounded-xl shadow-lg text-white hover:shadow-2xl transition-all hover:-translate-y-1">
                  <div className="flex items-center justify-between mb-4">
                    <Cpu className="text-white/80" size={32} />
                    <span className="text-white/60 text-xs bg-white/20 px-2 py-1 rounded">AI</span>
                  </div>
                  <p className="text-purple-100 text-sm mb-1">AI Model</p>
                  <p className="text-sm font-semibold">Llama-3 SQLCoder-8B (LoRA)</p>
                </div>

                <div className="bg-gradient-to-br from-orange-500 to-orange-600 p-6 rounded-xl shadow-lg text-white hover:shadow-2xl transition-all hover:-translate-y-1">
                  <div className="flex items-center justify-between mb-4">
                    <BarChart3 className="text-white/80" size={32} />
                    <span className="text-white/60 text-xs bg-white/20 px-2 py-1 rounded">NLP</span>
                  </div>
                  <p className="text-orange-100 text-sm mb-1">Query Mode</p>
                  <p className="text-sm font-semibold">Natural Language Processing</p>
                </div>
              </div>

              {/* Info Section */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm p-8 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="flex items-start gap-4 mb-6">
                  <div className="bg-gradient-to-br from-blue-500 to-purple-500 p-3 rounded-lg">
                    <Database className="text-white" size={28} />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold mb-2 text-gray-800 dark:text-gray-100">
                      About CenQuery
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Intelligent Census Data Query System
                    </p>
                  </div>
                </div>
                
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-4">
                  CenQuery is a natural language interface designed to help users
                  query Indian Census data without writing SQL. It uses a
                  domain-adapted language model to convert user questions into
                  structured database queries and presents the results in tabular
                  and visual formats.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                  <div className="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-lg border border-blue-100 dark:border-blue-800">
                    <h4 className="font-semibold text-blue-900 dark:text-blue-200 mb-2">🎯 Accuracy</h4>
                    <p className="text-sm text-blue-700 dark:text-blue-300">Fine-tuned on 650+ census-specific queries</p>
                  </div>
                  <div className="bg-purple-50 dark:bg-purple-900/30 p-4 rounded-lg border border-purple-100 dark:border-purple-800">
                    <h4 className="font-semibold text-purple-900 dark:text-purple-200 mb-2">⚡ Speed</h4>
                    <p className="text-sm text-purple-700 dark:text-purple-300">Optimized inference with 8-bit quantization</p>
                  </div>
                  <div className="bg-green-50 dark:bg-green-900/30 p-4 rounded-lg border border-green-100 dark:border-green-800">
                    <h4 className="font-semibold text-green-900 dark:text-green-200 mb-2">🔒 Privacy</h4>
                    <p className="text-sm text-green-700 dark:text-green-300">Fully offline, no data leaves your system</p>
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
        <Footer />
      </div>
    </AuthGuard>
  );
}

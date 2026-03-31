"use client";

import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";
import Footer from "@/components/layout/Footer";
import AuthGuard from "@/components/auth/AuthGuard";
import { Code, Database, Zap, Users, Award, Target } from "lucide-react";

export default function AboutPage() {
  return (
    <AuthGuard>
      <div className="flex flex-col h-screen">
        <Navbar />

        <div className="flex flex-1 overflow-hidden">
          <Sidebar />

          <main className="flex-1 p-6 bg-gradient-to-br from-gray-50 to-blue-50 overflow-y-auto">
            <div className="max-w-4xl mx-auto">
              <div className="mb-8">
                <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  About CenQuery
                </h2>
                <p className="text-gray-600">
                  Democratizing access to Indian Census data through AI
                </p>
              </div>

              <div className="bg-white/80 backdrop-blur-sm p-8 rounded-xl shadow-lg border border-gray-200 leading-relaxed space-y-6">
                <div className="flex items-start gap-4">
                  <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-3 rounded-lg flex-shrink-0">
                    <Target className="text-white" size={24} />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-800 mb-2">Mission</h3>
                    <p className="text-gray-700">
                      CenQuery is an intelligent query system designed to simplify
                      access to Indian Census data for non-technical users. Instead of
                      writing complex SQL queries, users can ask questions in natural
                      language.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="bg-gradient-to-br from-purple-500 to-purple-600 p-3 rounded-lg flex-shrink-0">
                    <Zap className="text-white" size={24} />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-800 mb-2">How It Works</h3>
                    <p className="text-gray-700">
                      The system converts user questions into structured database
                      queries using a fine-tuned large language model and retrieves
                      relevant census information from a normalized relational
                      database.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="bg-gradient-to-br from-green-500 to-green-600 p-3 rounded-lg flex-shrink-0">
                    <Users className="text-white" size={24} />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-800 mb-2">Who Benefits</h3>
                    <p className="text-gray-700">
                      CenQuery aims to support policymakers, researchers, and students
                      by enabling fast and intuitive exploration of demographic,
                      educational, employment, and health-related census statistics.
                    </p>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl border border-blue-100">
                  <div className="flex items-center gap-3 mb-4">
                    <Code className="text-blue-600" size={24} />
                    <h3 className="text-lg font-bold text-gray-800">Technologies Used</h3>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                      <span className="text-gray-700">Next.js 14</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-purple-600 rounded-full"></span>
                      <span className="text-gray-700">Tailwind CSS</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-green-600 rounded-full"></span>
                      <span className="text-gray-700">MySQL Database</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-orange-600 rounded-full"></span>
                      <span className="text-gray-700">FastAPI Backend</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-pink-600 rounded-full"></span>
                      <span className="text-gray-700">Llama-3 SQLCoder</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-indigo-600 rounded-full"></span>
                      <span className="text-gray-700">LoRA Fine-tuning</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-4 bg-gradient-to-r from-orange-50 to-yellow-50 p-6 rounded-xl border border-orange-100">
                  <div className="bg-gradient-to-br from-orange-500 to-orange-600 p-3 rounded-lg flex-shrink-0">
                    <Award className="text-white" size={24} />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-800 mb-2">Academic Project</h3>
                    <p className="text-gray-700">
                      This is a Final Year Major Project developed by the Department of Computer Science. 
                      The project demonstrates the practical application of Natural Language Processing, 
                      Machine Learning, and Database Systems in solving real-world data accessibility challenges.
                    </p>
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

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles, Database, Cpu, BarChart } from "lucide-react";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900">
      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center text-center px-6 py-24 relative overflow-hidden">
        {/* Decorative Elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 dark:bg-blue-600 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-3xl opacity-30 animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-200 dark:bg-purple-600 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-3xl opacity-30 animate-pulse delay-1000"></div>
        </div>

        <div className="relative z-10">
          <div className="inline-flex items-center gap-2 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 px-4 py-2 rounded-full text-sm font-medium mb-6 animate-bounce">
            <Sparkles size={16} />
            AI-Powered Census Insights
          </div>
          
          <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-6">
            CenQuery
          </h1>
          
          <p className="text-2xl text-gray-700 dark:text-gray-200 mb-4 max-w-3xl font-medium">
            A Natural Language Interface for Querying Indian Census Data
          </p>
          
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-10 max-w-2xl">
            Transform complex data queries into simple conversations. 
            Powered by advanced AI and designed for everyone.
          </p>
          
          <Link href="/login">
            <Button className="text-lg px-8 py-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-xl hover:shadow-2xl transition-all duration-300 group">
              Access System
              <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" size={20} />
            </Button>
          </Link>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-6 max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-800 dark:text-gray-100 mb-4">
            How It Works
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Three simple steps to unlock census insights
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 dark:border-gray-700 hover:-translate-y-2">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 w-14 h-14 rounded-xl flex items-center justify-center mb-6 shadow-lg">
              <span className="text-white text-2xl font-bold">1</span>
            </div>
            <h3 className="font-bold text-xl mb-3 text-gray-800 dark:text-gray-100">Ask in English</h3>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
              Simply type your question in plain English. No SQL knowledge required. 
              Example: &quot;Show literacy rate of districts in Maharashtra&quot;
            </p>
          </div>
          
          <div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 dark:border-gray-700 hover:-translate-y-2">
            <div className="bg-gradient-to-br from-purple-500 to-purple-600 w-14 h-14 rounded-xl flex items-center justify-center mb-6 shadow-lg">
              <Cpu className="text-white" size={28} />
            </div>
            <h3 className="font-bold text-xl mb-3 text-gray-800 dark:text-gray-100">AI Generates SQL</h3>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
              Our advanced AI model converts your question into an optimized SQL query 
              that runs against the census database.
            </p>
          </div>
          
          <div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 dark:border-gray-700 hover:-translate-y-2">
            <div className="bg-gradient-to-br from-pink-500 to-pink-600 w-14 h-14 rounded-xl flex items-center justify-center mb-6 shadow-lg">
              <BarChart className="text-white" size={28} />
            </div>
            <h3 className="font-bold text-xl mb-3 text-gray-800 dark:text-gray-100">Data is Visualized</h3>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
              Results are presented as interactive tables and beautiful charts 
              with multiple visualization options for easy analysis.
            </p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-6 bg-gradient-to-br from-gray-50 to-white dark:from-gray-800 dark:to-gray-900">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-800 dark:text-gray-100 mb-4">
              Key Features
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Everything you need for census data exploration
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 border-2 border-blue-200 dark:border-blue-800 p-6 rounded-xl hover:border-blue-400 dark:hover:border-blue-600 transition-all duration-300 hover:shadow-lg">
              <div className="flex items-start gap-4">
                <div className="bg-blue-100 dark:bg-blue-900/50 p-3 rounded-lg">
                  <Database className="text-blue-600 dark:text-blue-400" size={24} />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-2 text-gray-800 dark:text-gray-100">Natural Language to SQL</h3>
                  <p className="text-gray-600 dark:text-gray-300">Query databases using everyday language without any technical knowledge</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 border-2 border-purple-200 dark:border-purple-800 p-6 rounded-xl hover:border-purple-400 dark:hover:border-purple-600 transition-all duration-300 hover:shadow-lg">
              <div className="flex items-start gap-4">
                <div className="bg-purple-100 dark:bg-purple-900/50 p-3 rounded-lg">
                  <Sparkles className="text-purple-600 dark:text-purple-400" size={24} />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-2 text-gray-800 dark:text-gray-100">Indian Census Optimized</h3>
                  <p className="text-gray-600 dark:text-gray-300">Specifically designed and trained for Indian Census data domains</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 border-2 border-green-200 dark:border-green-800 p-6 rounded-xl hover:border-green-400 dark:hover:border-green-600 transition-all duration-300 hover:shadow-lg">
              <div className="flex items-start gap-4">
                <div className="bg-green-100 dark:bg-green-900/50 p-3 rounded-lg">
                  <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-2 text-gray-800 dark:text-gray-100">Secure & Offline</h3>
                  <p className="text-gray-600 dark:text-gray-300">Run entirely on your infrastructure with no external data transmission</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 border-2 border-orange-200 dark:border-orange-800 p-6 rounded-xl hover:border-orange-400 dark:hover:border-orange-600 transition-all duration-300 hover:shadow-lg">
              <div className="flex items-start gap-4">
                <div className="bg-orange-100 dark:bg-orange-900/50 p-3 rounded-lg">
                  <BarChart className="text-orange-600 dark:text-orange-400" size={24} />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-2 text-gray-800 dark:text-gray-100">Interactive Visualizations</h3>
                  <p className="text-gray-600 dark:text-gray-300">Multiple chart types, sortable tables, and data export capabilities</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center text-gray-600 dark:text-gray-400 py-12 bg-gray-50 dark:bg-gray-900">
        <p className="text-lg font-medium mb-2">
          CenQuery - Final Year Major Project
        </p>
        <p className="text-sm">
          Department of Computer Science
        </p>
      </footer>
    </main>
  );
}

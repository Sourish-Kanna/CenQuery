import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles, Database, Cpu, BarChart } from "lucide-react";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center text-center px-6 py-24 relative overflow-hidden">
        {/* Decorative Elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse delay-1000"></div>
        </div>

        <div className="relative z-10">
          <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-medium mb-6 animate-bounce">
            <Sparkles size={16} />
            AI-Powered Census Insights
          </div>
          
          <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-6">
            CenQuery
          </h1>
          
          <p className="text-2xl text-gray-700 mb-4 max-w-3xl font-medium">
            A Natural Language Interface for Querying Indian Census Data
          </p>
          
          <p className="text-lg text-gray-600 mb-10 max-w-2xl">
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
          <h2 className="text-4xl font-bold text-gray-800 mb-4">
            How It Works
          </h2>
          <p className="text-lg text-gray-600">
            Three simple steps to unlock census insights
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 hover:-translate-y-2">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 w-14 h-14 rounded-xl flex items-center justify-center mb-6 shadow-lg">
              <span className="text-white text-2xl font-bold">1</span>
            </div>
            <h3 className="font-bold text-xl mb-3 text-gray-800">Ask in English</h3>
            <p className="text-gray-600 leading-relaxed">
              Simply type your question in plain English. No SQL knowledge required. 
              Example: &quot;Show literacy rate of districts in Maharashtra&quot;
            </p>
          </div>
          
          <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 hover:-translate-y-2">
            <div className="bg-gradient-to-br from-purple-500 to-purple-600 w-14 h-14 rounded-xl flex items-center justify-center mb-6 shadow-lg">
              <Cpu className="text-white" size={28} />
            </div>
            <h3 className="font-bold text-xl mb-3 text-gray-800">AI Generates SQL</h3>
            <p className="text-gray-600 leading-relaxed">
              Our advanced AI model converts your question into an optimized SQL query 
              that runs against the census database.
            </p>
          </div>
          
          <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 hover:-translate-y-2">
            <div className="bg-gradient-to-br from-pink-500 to-pink-600 w-14 h-14 rounded-xl flex items-center justify-center mb-6 shadow-lg">
              <BarChart className="text-white" size={28} />
            </div>
            <h3 className="font-bold text-xl mb-3 text-gray-800">Data is Visualized</h3>
            <p className="text-gray-600 leading-relaxed">
              Results are presented as interactive tables and beautiful charts 
              with multiple visualization options for easy analysis.
            </p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-6 bg-gradient-to-br from-gray-50 to-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-800 mb-4">
              Key Features
            </h2>
            <p className="text-lg text-gray-600">
              Everything you need for census data exploration
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white border-2 border-blue-200 p-6 rounded-xl hover:border-blue-400 transition-all duration-300 hover:shadow-lg">
              <div className="flex items-start gap-4">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <Database className="text-blue-600" size={24} />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-2 text-gray-800">Natural Language to SQL</h3>
                  <p className="text-gray-600">Query databases using everyday language without any technical knowledge</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white border-2 border-purple-200 p-6 rounded-xl hover:border-purple-400 transition-all duration-300 hover:shadow-lg">
              <div className="flex items-start gap-4">
                <div className="bg-purple-100 p-3 rounded-lg">
                  <Sparkles className="text-purple-600" size={24} />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-2 text-gray-800">Indian Census Optimized</h3>
                  <p className="text-gray-600">Specifically designed and trained for Indian Census data domains</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white border-2 border-green-200 p-6 rounded-xl hover:border-green-400 transition-all duration-300 hover:shadow-lg">
              <div className="flex items-start gap-4">
                <div className="bg-green-100 p-3 rounded-lg">
                  <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-2 text-gray-800">Secure & Offline</h3>
                  <p className="text-gray-600">Run entirely on your infrastructure with no external data transmission</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white border-2 border-orange-200 p-6 rounded-xl hover:border-orange-400 transition-all duration-300 hover:shadow-lg">
              <div className="flex items-start gap-4">
                <div className="bg-orange-100 p-3 rounded-lg">
                  <BarChart className="text-orange-600" size={24} />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-2 text-gray-800">Interactive Visualizations</h3>
                  <p className="text-gray-600">Multiple chart types, sortable tables, and data export capabilities</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center text-gray-600 py-12 bg-gray-50">
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

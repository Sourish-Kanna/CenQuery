import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";
import Footer from "@/components/layout/Footer";
import { Database, Layers, Cpu, BarChart3 } from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="flex flex-col h-screen">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-6 bg-gray-50">
          <h2 className="text-2xl font-semibold mb-6">
            System Dashboard
          </h2>

          {/* Top Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-4 rounded-lg shadow flex items-center gap-4">
              <Database className="text-blue-600" />
              <div>
                <p className="text-sm text-gray-500">Total Tables</p>
                <p className="text-xl font-semibold">12</p>
              </div>
            </div>

            <div className="bg-white p-4 rounded-lg shadow flex items-center gap-4">
              <Layers className="text-green-600" />
              <div>
                <p className="text-sm text-gray-500">Domains</p>
                <p className="text-sm">Population, Education, Health</p>
              </div>
            </div>

            <div className="bg-white p-4 rounded-lg shadow flex items-center gap-4">
              <Cpu className="text-purple-600" />
              <div>
                <p className="text-sm text-gray-500">AI Model</p>
                <p className="text-sm">Llama-3 SQLCoder (LoRA)</p>
              </div>
            </div>

            <div className="bg-white p-4 rounded-lg shadow flex items-center gap-4">
              <BarChart3 className="text-orange-600" />
              <div>
                <p className="text-sm text-gray-500">Query Mode</p>
                <p className="text-sm">Natural Language</p>
              </div>
            </div>
          </div>

          {/* Info Section */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-2">
              About CenQuery
            </h3>
            <p className="text-gray-600 leading-relaxed">
              CenQuery is a natural language interface designed to help users
              query Indian Census data without writing SQL. It uses a
              domain-adapted language model to convert user questions into
              structured database queries and presents the results in tabular
              and visual formats.
            </p>
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
}

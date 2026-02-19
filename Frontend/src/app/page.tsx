import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center text-center px-6 py-24 bg-white">
        <h1 className="text-4xl font-bold text-blue-700 mb-4">
          CenQuery
        </h1>
        <p className="text-xl text-gray-600 mb-6 max-w-2xl">
          A Natural Language Interface for Querying Indian Census Data
        </p>
        <Link href="/login">
          <Button className="text-lg px-6 py-3">
            Access System
          </Button>
        </Link>
      </section>

      {/* How It Works */}
      <section className="py-16 px-6 max-w-5xl mx-auto">
        <h2 className="text-2xl font-semibold text-center mb-10">
          How It Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-semibold mb-2">1. Ask in English</h3>
            <p className="text-gray-600">
              Users type questions like “Show literacy rate of districts in Maharashtra”.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-semibold mb-2">2. AI Generates SQL</h3>
            <p className="text-gray-600">
              The system converts the question into an optimized SQL query.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-semibold mb-2">3. Data is Visualized</h3>
            <p className="text-gray-600">
              Results are shown as tables and charts for easy analysis.
            </p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-6 bg-white">
        <h2 className="text-2xl font-semibold text-center mb-10">
          Key Features
        </h2>
        <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border p-4 rounded">
            ✔ Natural language to SQL conversion
          </div>
          <div className="border p-4 rounded">
            ✔ Designed for Indian Census data
          </div>
          <div className="border p-4 rounded">
            ✔ Secure and offline architecture
          </div>
          <div className="border p-4 rounded">
            ✔ Interactive data visualization
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center text-gray-500 py-6">
        <p>
          CenQuery - Final Year Major Project
        </p>
        <p>
          Department of Computer Science
        </p>
      </footer>
    </main>
  );
}

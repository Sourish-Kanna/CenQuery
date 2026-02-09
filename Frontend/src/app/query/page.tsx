import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";
import QueryPanel from "@/components/query/QueryPanel";
import Footer from "@/components/layout/Footer";

export default function QueryPage() {
  return (
    <div className="flex flex-col h-screen">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-6 bg-gray-50">
          <h2 className="text-2xl font-semibold mb-4">Query Census Data</h2>

          <div className="bg-white p-6 rounded-lg shadow-sm">
            <QueryPanel />
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
}

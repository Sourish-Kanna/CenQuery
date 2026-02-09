import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";
import Footer from "@/components/layout/Footer";

const schema = [
  {
    name: "Population",
    tables: ["state_population", "district_population", "age_distribution"],
  },
  {
    name: "Education",
    tables: ["literacy_rate", "school_attendance"],
  },
  {
    name: "Health",
    tables: ["mortality_rate", "disability_data"],
  },
  {
    name: "Employment",
    tables: ["main_workers", "marginal_workers"],
  },
];

export default function SchemaPage() {
  return (
    <div className="flex flex-col h-screen">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-6 bg-gray-50">
          <h2 className="text-2xl font-semibold mb-6">
            Database Schema
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {schema.map((group) => (
              <div
                key={group.name}
                className="bg-white p-4 rounded-lg shadow"
              >
                <h3 className="font-semibold mb-3 text-blue-700">
                  {group.name}
                </h3>
                <ul className="list-disc ml-5 text-gray-700">
                  {group.tables.map((table) => (
                    <li key={table}>{table}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
}

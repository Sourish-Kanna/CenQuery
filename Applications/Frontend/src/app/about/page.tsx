import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";
import Footer from "@/components/layout/Footer";

export default function AboutPage() {
  return (
    <div className="flex flex-col h-screen">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-6 bg-gray-50">
          <h2 className="text-2xl font-semibold mb-4">
            About CenQuery
          </h2>

          <div className="bg-white p-6 rounded-lg shadow leading-relaxed space-y-4">
            <p>
              CenQuery is an intelligent query system designed to simplify
              access to Indian Census data for non-technical users. Instead of
              writing complex SQL queries, users can ask questions in natural
              language.
            </p>

            <p>
              The system converts user questions into structured database
              queries using a fine-tuned large language model and retrieves
              relevant census information from a normalized relational
              database.
            </p>

            <p>
              CenQuery aims to support policymakers, researchers, and students
              by enabling fast and intuitive exploration of demographic,
              educational, employment, and health-related census statistics.
            </p>

            <p className="font-medium">
              Technologies Used: Next.js, Tailwind CSS, MySQL, and a
              domain-adapted Large Language Model.
            </p>
          </div>
        </main>
      </div>
      <Footer />
    </div>
    
  );
}

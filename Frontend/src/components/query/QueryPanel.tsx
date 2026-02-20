"use client";

import { Button } from "@/components/ui/button";
import { useState } from "react";
import { Copy, Loader2, Trash2, AlertCircle } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

// 1. Define your Backend URL
const API_BASE_URL = "http://localhost:8000";

const exampleQuestions = [
  "Show literacy rate of districts in Maharashtra",
  "Compare male and female population in Tamil Nadu",
  "List top 5 districts by population",
];

export default function QueryPanel() {
  const [question, setQuestion] = useState("");
  const [sql, setSql] = useState("");
  const [results, setResults] = useState<any[]>([]); // Dynamic results from DB
  const [showResult, setShowResult] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!question) return;

    setLoading(true);
    setShowResult(false);
    setError(null);
    setSql("");

    try {
      // STEP 1: Generate SQL from Natural Language
      const genResponse = await fetch(`${API_BASE_URL}/generate-select-sql`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!genResponse.ok) throw new Error("Failed to generate SQL query.");
      const genData = await genResponse.json();
      const generatedSql = genData.sql_query;
      setSql(generatedSql);

      // STEP 2: Execute the generated SQL
      const execResponse = await fetch(`${API_BASE_URL}/execute-sql`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          sql_query: generatedSql,
          question: question 
        }),
      });

      if (!execResponse.ok) throw new Error("Database execution failed.");
      const execData = await execResponse.json();

      if (execData.status === "error") {
        throw new Error(execData.result || "An error occurred during execution.");
      }

      // STEP 3: Update State with real data
      setResults(execData.result);
      setShowResult(true);

    } catch (err: any) {
      console.error("Integration Error:", err);
      setError(err.message || "Something went wrong connection to the server.");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setQuestion("");
    setSql("");
    setResults([]);
    setShowResult(false);
    setError(null);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(sql);
  };

  // Helper to get keys for table headers and chart axis
  const resultKeys = results.length > 0 ? Object.keys(results[0]) : [];
  const dataKeyX = resultKeys[0]; // Usually the name/district
  const dataKeyY = resultKeys[1]; // Usually the value/count

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto p-4">
      {/* Example questions */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Example Questions
        </label>
        <select
          className="border rounded p-2 w-full bg-white"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        >
          <option value="">Select an example...</option>
          {exampleQuestions.map((q) => (
            <option key={q} value={q}>
              {q}
            </option>
          ))}
        </select>
      </div>

      {/* Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Ask a question about Indian Census
        </label>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g., Which district has the highest female literacy in Kerala?"
          className="w-full h-28 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
        />
      </div>

      {/* Buttons */}
      <div className="flex gap-3">
        <Button onClick={handleGenerate} disabled={loading || !question}>
          {loading ? (
            <>
              <Loader2 className="animate-spin mr-2" size={16} />
              Processing...
            </>
          ) : (
            "Generate & Run"
          )}
        </Button>

        <Button variant="outline" onClick={handleClear}>
          <Trash2 size={16} className="mr-1" />
          Clear
        </Button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex items-center gap-2 p-4 text-red-700 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle size={18} />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* SQL Output */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <label className="block text-sm font-medium text-gray-700">
            Generated SQL
          </label>
          {sql && (
            <button
              onClick={handleCopy}
              className="flex items-center gap-1 text-sm text-blue-600 hover:underline"
            >
              <Copy size={14} /> Copy
            </button>
          )}
        </div>
        <pre className="bg-slate-900 text-slate-100 p-4 rounded-lg text-xs font-mono overflow-x-auto min-h-[50px]">
          {sql || "-- SQL query will be generated here..."}
        </pre>
      </div>

      {/* Results Section */}
      {showResult && results.length > 0 ? (
        <div className="space-y-8 animate-in fade-in duration-500">
          {/* Table */}
          <div className="overflow-hidden border border-gray-200 rounded-lg shadow-sm">
            <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
              <span className="text-sm font-semibold text-gray-700">Data Table</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-gray-100 text-gray-600 uppercase text-xs">
                  <tr>
                    {resultKeys.map((key) => (
                      <th key={key} className="px-4 py-3 font-medium border-b capitalize">
                        {key.replace(/_/g, " ")}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {results.map((row, i) => (
                    <tr key={i} className="hover:bg-gray-50 transition-colors">
                      {resultKeys.map((key) => (
                        <td key={key} className="px-4 py-3 text-gray-700">
                          {row[key]?.toLocaleString() ?? "-"}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Chart */}
          <div className="border rounded-lg p-6 shadow-sm bg-white">
            <label className="block text-sm font-semibold text-gray-700 mb-4 capitalize">
              Visualizing: {dataKeyY?.replace(/_/g, " ")} by {dataKeyX?.replace(/_/g, " ")}
            </label>
            <div className="w-full h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={results}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis 
                    dataKey={dataKeyX} 
                    fontSize={12} 
                    tickMargin={10}
                  />
                  <YAxis fontSize={12} />
                  <Tooltip 
                    cursor={{fill: '#f3f4f6'}}
                    contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
                  />
                  <Bar dataKey={dataKeyY} fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      ) : showResult && results.length === 0 ? (
        <div className="p-8 text-center border rounded-lg bg-gray-50 text-gray-500">
          No data found for this query.
        </div>
      ) : (
        <div className="border border-dashed rounded-lg p-10 text-center text-gray-400 bg-gray-50">
          <p className="text-sm">Submit a question to visualize census data.</p>
        </div>
      )}
    </div>
  );
}
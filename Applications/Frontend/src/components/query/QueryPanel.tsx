"use client";

import { Button } from "@/components/ui/button";
import { useState } from "react";
import { Copy, Loader2, Trash2, AlertCircle, Download, TrendingUp, PieChart as PieChartIcon, BarChart3 } from "lucide-react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from "recharts";

// 1. Define your Backend URL
// const API_BASE_URL = "http://localhost:8000";
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
console.log("Using API Base URL:", API_BASE_URL);

const exampleQuestions = [
  "What all states are there in India?",
  "How many people in Punjab are seeking work?",
  // "What all crops were sowed?",
  "How many males and females are there in Tamil Nadu?",
  "Give me top 5 states by population in india?",
  // "What was the area sown for Rice in 2024-25?",
  "How much Muslim population is there in Kerala?",
  "What is the total population of India?",
];

export default function QueryPanel() {
  const [question, setQuestion] = useState("");
  const [sql, setSql] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [showResult, setShowResult] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chartType, setChartType] = useState<"bar" | "line" | "pie">("bar");
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");

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
        body: JSON.stringify({ question: question }),
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
    setChartType("bar");
    setSortColumn(null);
    setSortDirection("asc");
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(sql);
  };

  const handleExportCSV = () => {
    if (results.length === 0) return;

    const keys = Object.keys(results[0]);
    const csvContent = [
      keys.join(","),
      ...results.map(row => keys.map(key => JSON.stringify(row[key] ?? "")).join(","))
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "query_results.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportJSON = () => {
    if (results.length === 0) return;

    const jsonContent = JSON.stringify(results, null, 2);
    const blob = new Blob([jsonContent], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "query_results.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortColumn(column);
      setSortDirection("asc");
    }
  };

  const getSortedResults = () => {
    if (!sortColumn) return results;

    return [...results].sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];

      if (aVal === bVal) return 0;
      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;

      const comparison = aVal < bVal ? -1 : 1;
      return sortDirection === "asc" ? comparison : -comparison;
    });
  };

  // Helper to get keys for table headers and chart axis
  const resultKeys = results.length > 0 ? Object.keys(results[0]) : [];
  const dataKeyX = resultKeys[0]; // Usually the name/district
  const dataKeyY = resultKeys[1]; // Usually the value/count

  // Chart colors
  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#ef4444', '#06b6d4', '#6366f1'];

  // Render chart based on type
  // const renderChart = () => {
  //   const sortedData = getSortedResults();

  //   switch (chartType) {
  //     case "bar":
  //       return (
  //         <ResponsiveContainer width="100%" height="100%">
  //           <BarChart data={sortedData}>
  //             <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
  //             <XAxis 
  //               dataKey={dataKeyX} 
  //               fontSize={12} 
  //               tickMargin={10}
  //               stroke="#6b7280"
  //             />
  //             <YAxis fontSize={12} stroke="#6b7280" />
  //             <Tooltip 
  //               cursor={{fill: '#f3f4f6'}}
  //               contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', background: 'white'}}
  //             />
  //             <Legend />
  //             <Bar dataKey={dataKeyY} fill="#3b82f6" radius={[8, 8, 0, 0]} />
  //           </BarChart>
  //         </ResponsiveContainer>
  //       );

  //     case "line":
  //       return (
  //         <ResponsiveContainer width="100%" height="100%">
  //           <LineChart data={sortedData}>
  //             <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
  //             <XAxis 
  //               dataKey={dataKeyX} 
  //               fontSize={12} 
  //               tickMargin={10}
  //               stroke="#6b7280"
  //             />
  //             <YAxis fontSize={12} stroke="#6b7280" />
  //             <Tooltip 
  //               contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', background: 'white'}}
  //             />
  //             <Legend />
  //             <Line 
  //               type="monotone" 
  //               dataKey={dataKeyY} 
  //               stroke="#8b5cf6" 
  //               strokeWidth={3}
  //               dot={{ fill: '#8b5cf6', r: 5 }}
  //               activeDot={{ r: 7 }}
  //             />
  //           </LineChart>
  //         </ResponsiveContainer>
  //       );

  //     case "pie":
  //       return (
  //         <ResponsiveContainer width="100%" height="100%">
  //           <PieChart>
  //             <Pie
  //               data={sortedData}
  //               dataKey={dataKeyY}
  //               nameKey={dataKeyX}
  //               cx="50%"
  //               cy="50%"
  //               outerRadius={120}
  //               label={(entry) => entry[dataKeyX]}
  //               labelLine={true}
  //             >
  //               {sortedData.map((entry, index) => (
  //                 <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
  //               ))}
  //             </Pie>
  //             <Tooltip 
  //               contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', background: 'white'}}
  //             />
  //             <Legend />
  //           </PieChart>
  //         </ResponsiveContainer>
  //       );
  //   }
  // };

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto p-4">
      {/* Example questions */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Example Questions
        </label>
        <select
          className="border rounded p-2 w-full bg-white dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
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
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Ask a question about Indian Census
        </label>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g., how many males and females are there in Tamil Nadu?"
          className="w-full h-28 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm bg-white dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400"
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
        <div className="flex items-center gap-2 p-4 text-red-700 dark:text-red-400 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
          <AlertCircle size={18} />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* SQL Output */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Generated SQL
          </label>
          {sql && (
            <button
              onClick={handleCopy}
              className="flex items-center gap-1 text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              <Copy size={14} /> Copy
            </button>
          )}
        </div>
        <pre className="bg-slate-900 dark:bg-gray-950 text-slate-100 dark:text-gray-100 p-4 rounded-lg text-xs font-mono overflow-x-auto min-h-[50px] border border-slate-700 dark:border-gray-800">
          {sql || "-- SQL query will be generated here..."}
        </pre>
      </div>

      {/* Results Section */}
      {showResult && results.length > 0 ? (
        <div className="space-y-6 animate-in fade-in duration-500">
          {/* Export Buttons */}
          <div className="flex gap-3 flex-wrap">
            <Button onClick={handleExportCSV} variant="outline" size="sm" className="flex gap-2">
              <Download size={16} />
              Export CSV
            </Button>
            <Button onClick={handleExportJSON} variant="outline" size="sm" className="flex gap-2">
              <Download size={16} />
              Export JSON
            </Button>
          </div>

          {/* Table */}
          <div className="overflow-hidden border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg bg-white dark:bg-gray-800">
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/30 dark:to-purple-900/30 px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-2">
                <BarChart3 className="text-blue-600 dark:text-blue-400" size={20} />
                <span className="text-base font-semibold text-gray-800 dark:text-gray-200">Query Results</span>
                <span className="ml-auto text-sm text-gray-600 dark:text-gray-400">{results.length} rows</span>
              </div>
            </div>
            <div className="overflow-x-auto max-h-96">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 dark:bg-gray-700 sticky top-0 z-10">
                  <tr>
                    {resultKeys.map((key) => (
                      <th
                        key={key}
                        className="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider border-b dark:border-gray-600 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                        onClick={() => handleSort(key)}
                      >
                        <div className="flex items-center gap-1">
                          {key.replace(/_/g, " ")}
                          {sortColumn === key && (
                            <span className="text-blue-600 dark:text-blue-400">
                              {sortDirection === "asc" ? "↑" : "↓"}
                            </span>
                          )}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                  {getSortedResults().map((row, i) => (
                    <tr key={i} className="hover:bg-blue-50/50 dark:hover:bg-blue-900/20 transition-colors">
                      {resultKeys.map((key) => (
                        <td key={key} className="px-6 py-4 text-gray-700 dark:text-gray-300 whitespace-nowrap">
                          {row[key]?.toLocaleString() ?? "-"}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Chart Section */}
          {/* <div className="border rounded-xl p-6 shadow-lg bg-white dark:bg-gray-800 dark:border-gray-700">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2">
                  <TrendingUp className="text-blue-600 dark:text-blue-400" size={20} />
                  Data Visualization
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 capitalize">
                  {dataKeyY?.replace(/_/g, " ")} by {dataKeyX?.replace(/_/g, " ")}
                </p>
              </div>
              
              
              <div className="flex gap-2 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg">
                <button
                  onClick={() => setChartType("bar")}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${
                    chartType === "bar"
                      ? "bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm"
                      : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100"
                  }`}
                >
                  <BarChart3 size={16} />
                  Bar
                </button>
                <button
                  onClick={() => setChartType("line")}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${
                    chartType === "line"
                      ? "bg-white dark:bg-gray-600 text-purple-600 dark:text-purple-400 shadow-sm"
                      : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100"
                  }`}
                >
                  <TrendingUp size={16} />
                  Line
                </button>
                <button
                  onClick={() => setChartType("pie")}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${
                    chartType === "pie"
                      ? "bg-white dark:bg-gray-600 text-pink-600 dark:text-pink-400 shadow-sm"
                      : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100"
                  }`}
                >
                  <PieChartIcon size={16} />
                  Pie
                </button>
              </div>
            </div>
            
            <div className="w-full h-96">
              {renderChart()}
            </div>
          </div> */}
        </div>
      ) : showResult && results.length === 0 ? (
        <div className="p-8 text-center border-2 border-dashed rounded-xl bg-gray-50 dark:bg-gray-800/50 text-gray-500 dark:text-gray-400 border-gray-300 dark:border-gray-700">
          <AlertCircle className="mx-auto mb-3 text-gray-400 dark:text-gray-500" size={48} />
          <p className="text-base font-medium">No data found for this query.</p>
        </div>
      ) : (
        <div className="border-2 border-dashed rounded-xl p-12 text-center text-gray-400 dark:text-gray-500 bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-800/50 dark:to-blue-900/20 border-gray-300 dark:border-gray-700">
          <BarChart3 className="mx-auto mb-4 text-gray-300 dark:text-gray-600" size={64} />
          <p className="text-base font-medium mb-2">Ready to Query</p>
          <p className="text-sm">Submit a question to visualize census data.</p>
        </div>
      )}
    </div>
  );
}
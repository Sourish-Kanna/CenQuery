"use client";

import { Button } from "@/components/ui/button";
import { useState } from "react";
import { Copy, Loader2, Trash2 } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const dummyResult = [
  { district: "Mumbai", literacy: 89 },
  { district: "Pune", literacy: 87 },
  { district: "Nagpur", literacy: 82 },
  { district: "Nashik", literacy: 80 },
];

const exampleQuestions = [
  "Show literacy rate of districts in Maharashtra",
  "Compare male and female population in Tamil Nadu",
  "List top 5 districts by population",
];

export default function QueryPanel() {
  const [question, setQuestion] = useState("");
  const [sql, setSql] = useState("");
  const [showResult, setShowResult] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleGenerate = () => {
    setLoading(true);
    setShowResult(false);

    setTimeout(() => {
      setSql(
        "SELECT district, literacy_rate FROM census WHERE state = 'Maharashtra';"
      );
      setShowResult(true);
      setLoading(false);
    }, 1200);
  };

  const handleClear = () => {
    setQuestion("");
    setSql("");
    setShowResult(false);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(sql);
    alert("SQL copied to clipboard!");
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Example questions */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Example Questions
        </label>
        <select
          className="border rounded p-2 w-full"
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
          placeholder="Type your census-related question here..."
          className="w-full h-28 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Buttons */}
      <div className="flex gap-3">
        <Button onClick={handleGenerate} disabled={loading || !question}>
          {loading ? (
            <>
              <Loader2 className="animate-spin mr-2" size={16} />
              Generating...
            </>
          ) : (
            "Generate SQL"
          )}
        </Button>

        <Button variant="outline" onClick={handleClear}>
          <Trash2 size={16} className="mr-1" />
          Clear
        </Button>
      </div>

      {/* SQL Output */}
      <div>
        <div className="flex justify-between items-center mb-2">
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
        <pre className="bg-gray-100 p-3 rounded-lg text-sm overflow-x-auto">
{sql || "SQL query will appear here..."}
        </pre>
      </div>

      {/* Results */}
      {showResult ? (
        <>
          {/* Table */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Query Result (Table)
            </label>
            <table className="w-full border border-gray-200 rounded-lg overflow-hidden">
              <thead className="bg-gray-100">
                <tr>
                  <th className="text-left p-2 border">District</th>
                  <th className="text-left p-2 border">Literacy Rate (%)</th>
                </tr>
              </thead>
              <tbody>
                {dummyResult.map((row) => (
                  <tr key={row.district}>
                    <td className="p-2 border">{row.district}</td>
                    <td className="p-2 border">{row.literacy}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Chart */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Visualization
            </label>
            <div className="w-full h-64 border rounded-lg p-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dummyResult}>
                  <XAxis dataKey="district" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="literacy" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      ) : (
        <div className="border border-dashed rounded-lg p-6 text-center text-gray-500">
          <p className="text-sm">
            Ask a question about Indian Census data to see results here.
          </p>
          <p className="text-xs mt-1">
            Example:{" "}
            <span className="italic">
              "Show literacy rate of districts in Maharashtra"
            </span>
          </p>
        </div>
      )}
    </div>
  );
}

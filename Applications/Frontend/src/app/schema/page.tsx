"use client";

import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";
import Footer from "@/components/layout/Footer";
import AuthGuard from "@/components/auth/AuthGuard";
import { useState, useEffect } from "react";
import { Database, Key, Link as LinkIcon, Search, ChevronDown, ChevronUp } from "lucide-react";

interface Column {
  name: string;
  type: string;
  constraints: string[];
}

interface TableSchema {
  columns: Column[];
  primary_key: string[];
  foreign_keys: Array<{
    column: string;
    references_table: string;
    references_column: string;
  }>;
}

interface DatabaseSchema {
  [tableName: string]: TableSchema;
}

export default function SchemaPage() {
  const [schema, setSchema] = useState<DatabaseSchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set());

  useEffect(() => {
    // Load schema from the backend or public folder
    fetch("/database_schema.json")
      .then((res) => res.json())
      .then((data) => {
        setSchema(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load schema:", err);
        setLoading(false);
      });
  }, []);

  const toggleTable = (tableName: string) => {
    const newExpanded = new Set(expandedTables);
    if (newExpanded.has(tableName)) {
      newExpanded.delete(tableName);
    } else {
      newExpanded.add(tableName);
    }
    setExpandedTables(newExpanded);
  };

  const filteredTables = schema
    ? Object.keys(schema).filter((tableName) =>
        tableName.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : [];

  return (
    <AuthGuard>
      <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
        <Navbar />

        <div className="flex flex-1 overflow-hidden">
          <Sidebar />

          <main className="flex-1 p-6 overflow-y-auto">
            <div className="max-w-7xl mx-auto">
              <div className="mb-8">
                <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent">
                  Database Schema
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Explore the Indian Census database structure
                </p>
              </div>

              {/* Search Bar */}
              <div className="mb-6">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500" size={20} />
                  <input
                    type="text"
                    placeholder="Search tables..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 shadow-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                  />
                </div>
              </div>

              {loading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
                </div>
              ) : schema ? (
                <div className="space-y-4">
                  <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      <span className="font-semibold text-gray-800 dark:text-gray-200">{Object.keys(schema).length}</span> tables found
                      {searchTerm && (
                        <span> • <span className="font-semibold text-gray-800 dark:text-gray-200">{filteredTables.length}</span> matching your search</span>
                      )}
                    </p>
                  </div>

                  {filteredTables.map((tableName) => {
                    const table = schema[tableName];
                    const isExpanded = expandedTables.has(tableName);

                    return (
                      <div
                        key={tableName}
                        className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-lg transition-shadow"
                      >
                        {/* Table Header */}
                        <div
                          className="flex items-center justify-between p-4 cursor-pointer bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/30 dark:to-purple-900/30 hover:from-blue-100 hover:to-purple-100 dark:hover:from-blue-900/50 dark:hover:to-purple-900/50 transition-colors"
                          onClick={() => toggleTable(tableName)}
                        >
                          <div className="flex items-center gap-3">
                            <Database className="text-blue-600 dark:text-blue-400" size={20} />
                            <div>
                              <h3 className="font-semibold text-lg text-gray-800 dark:text-gray-200">
                                {tableName}
                              </h3>
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                {table.columns.length} columns
                                {table.foreign_keys.length > 0 && ` • ${table.foreign_keys.length} foreign keys`}
                              </p>
                            </div>
                          </div>
                          {isExpanded ? (
                            <ChevronUp className="text-gray-500 dark:text-gray-400" size={20} />
                          ) : (
                            <ChevronDown className="text-gray-500 dark:text-gray-400" size={20} />
                          )}
                        </div>

                        {/* Table Details */}
                        {isExpanded && (
                          <div className="p-4 space-y-4 bg-gray-50/50 dark:bg-gray-900/50">
                            {/* Columns Table */}
                            <div>
                              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                                <Database size={16} />
                                Columns
                              </h4>
                              <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                  <thead className="bg-gray-50 dark:bg-gray-700">
                                    <tr>
                                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 dark:text-gray-300 uppercase">
                                        Column Name
                                      </th>
                                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 dark:text-gray-300 uppercase">
                                        Data Type
                                      </th>
                                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 dark:text-gray-300 uppercase">
                                        Constraints
                                      </th>
                                    </tr>
                                  </thead>
                                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-800">
                                    {table.columns.map((col) => (
                                      <tr key={col.name} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                                        <td className="px-4 py-2 font-mono text-gray-800 dark:text-gray-200">
                                          {col.name}
                                          {table.primary_key.includes(col.name) && (
                                            <Key className="inline ml-2 text-yellow-600 dark:text-yellow-400" size={14} />
                                          )}
                                        </td>
                                        <td className="px-4 py-2 text-gray-600 dark:text-gray-400">
                                          <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded text-xs font-medium">
                                            {col.type}
                                          </span>
                                        </td>
                                        <td className="px-4 py-2 text-gray-600 dark:text-gray-400">
                                          {col.constraints.length > 0 ? (
                                            <div className="flex gap-1 flex-wrap">
                                              {col.constraints.map((constraint, idx) => (
                                                <span
                                                  key={idx}
                                                  className="px-2 py-1 bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300 rounded text-xs font-medium"
                                                >
                                                  {constraint}
                                                </span>
                                              ))}
                                            </div>
                                          ) : (
                                            <span className="text-gray-400 dark:text-gray-500 text-xs">None</span>
                                          )}
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </div>

                            {/* Primary Keys */}
                            {table.primary_key.length > 0 && (
                              <div className="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-lg border border-yellow-200 dark:border-yellow-800">
                                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1 flex items-center gap-2">
                                  <Key className="text-yellow-600 dark:text-yellow-400" size={16} />
                                  Primary Key
                                </h4>
                                <p className="text-sm text-gray-700 dark:text-gray-300 font-mono">
                                  {table.primary_key.join(", ")}
                                </p>
                              </div>
                            )}

                            {/* Foreign Keys */}
                            {table.foreign_keys.length > 0 && (
                              <div className="bg-purple-50 dark:bg-purple-900/20 p-3 rounded-lg border border-purple-200 dark:border-purple-800">
                                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                                  <LinkIcon className="text-purple-600 dark:text-purple-400" size={16} />
                                  Foreign Keys
                                </h4>
                                <div className="space-y-1">
                                  {table.foreign_keys.map((fk, idx) => (
                                    <p key={idx} className="text-sm text-gray-700 dark:text-gray-300">
                                      <span className="font-mono bg-white dark:bg-gray-700 px-2 py-1 rounded">
                                        {fk.column}
                                      </span>
                                      <span className="mx-2 text-purple-600 dark:text-purple-400">→</span>
                                      <span className="font-mono bg-white dark:bg-gray-700 px-2 py-1 rounded">
                                        {fk.references_table}.{fk.references_column}
                                      </span>
                                    </p>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}

                  {filteredTables.length === 0 && (
                    <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                      <Search className="mx-auto text-gray-400 dark:text-gray-500 mb-3" size={48} />
                      <p className="text-gray-500 dark:text-gray-400">No tables found matching &quot;{searchTerm}&quot;</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                  <p className="text-red-500 dark:text-red-400">Failed to load database schema</p>
                </div>
              )}
            </div>
          </main>
        </div>
        <Footer />
      </div>
    </AuthGuard>
  );
}

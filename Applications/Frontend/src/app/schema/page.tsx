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
      <div className="flex flex-col h-screen">
        <Navbar />

        <div className="flex flex-1 overflow-hidden">
          <Sidebar />

          <main className="flex-1 p-6 bg-gradient-to-br from-gray-50 to-blue-50 overflow-y-auto">
            <div className="max-w-7xl mx-auto">
              <div className="mb-8">
                <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Database Schema
                </h2>
                <p className="text-gray-600">
                  Explore the Indian Census database structure
                </p>
              </div>

              {/* Search Bar */}
              <div className="mb-6">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="text"
                    placeholder="Search tables..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
                  />
                </div>
              </div>

              {loading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
              ) : schema ? (
                <div className="space-y-4">
                  <div className="bg-white/80 backdrop-blur-sm p-4 rounded-lg shadow-sm border border-gray-200">
                    <p className="text-sm text-gray-600">
                      <span className="font-semibold text-gray-800">{Object.keys(schema).length}</span> tables found
                      {searchTerm && (
                        <span> • <span className="font-semibold text-gray-800">{filteredTables.length}</span> matching your search</span>
                      )}
                    </p>
                  </div>

                  {filteredTables.map((tableName) => {
                    const table = schema[tableName];
                    const isExpanded = expandedTables.has(tableName);

                    return (
                      <div
                        key={tableName}
                        className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow"
                      >
                        {/* Table Header */}
                        <div
                          className="flex items-center justify-between p-4 cursor-pointer bg-gradient-to-r from-blue-50 to-purple-50 hover:from-blue-100 hover:to-purple-100 transition-colors"
                          onClick={() => toggleTable(tableName)}
                        >
                          <div className="flex items-center gap-3">
                            <Database className="text-blue-600" size={20} />
                            <div>
                              <h3 className="font-semibold text-lg text-gray-800">
                                {tableName}
                              </h3>
                              <p className="text-xs text-gray-500">
                                {table.columns.length} columns
                                {table.foreign_keys.length > 0 && ` • ${table.foreign_keys.length} foreign keys`}
                              </p>
                            </div>
                          </div>
                          {isExpanded ? (
                            <ChevronUp className="text-gray-500" size={20} />
                          ) : (
                            <ChevronDown className="text-gray-500" size={20} />
                          )}
                        </div>

                        {/* Table Details */}
                        {isExpanded && (
                          <div className="p-4 space-y-4">
                            {/* Columns Table */}
                            <div>
                              <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                                <Database size={16} />
                                Columns
                              </h4>
                              <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                  <thead className="bg-gray-50">
                                    <tr>
                                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase">
                                        Column Name
                                      </th>
                                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase">
                                        Data Type
                                      </th>
                                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase">
                                        Constraints
                                      </th>
                                    </tr>
                                  </thead>
                                  <tbody className="divide-y divide-gray-200">
                                    {table.columns.map((col) => (
                                      <tr key={col.name} className="hover:bg-gray-50">
                                        <td className="px-4 py-2 font-mono text-gray-800">
                                          {col.name}
                                          {table.primary_key.includes(col.name) && (
                                            <Key className="inline ml-2 text-yellow-600" size={14} />
                                          )}
                                        </td>
                                        <td className="px-4 py-2 text-gray-600">
                                          <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                                            {col.type}
                                          </span>
                                        </td>
                                        <td className="px-4 py-2 text-gray-600">
                                          {col.constraints.length > 0 ? (
                                            <div className="flex gap-1 flex-wrap">
                                              {col.constraints.map((constraint, idx) => (
                                                <span
                                                  key={idx}
                                                  className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium"
                                                >
                                                  {constraint}
                                                </span>
                                              ))}
                                            </div>
                                          ) : (
                                            <span className="text-gray-400 text-xs">None</span>
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
                              <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
                                <h4 className="text-sm font-semibold text-gray-700 mb-1 flex items-center gap-2">
                                  <Key className="text-yellow-600" size={16} />
                                  Primary Key
                                </h4>
                                <p className="text-sm text-gray-700 font-mono">
                                  {table.primary_key.join(", ")}
                                </p>
                              </div>
                            )}

                            {/* Foreign Keys */}
                            {table.foreign_keys.length > 0 && (
                              <div className="bg-purple-50 p-3 rounded-lg border border-purple-200">
                                <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                                  <LinkIcon className="text-purple-600" size={16} />
                                  Foreign Keys
                                </h4>
                                <div className="space-y-1">
                                  {table.foreign_keys.map((fk, idx) => (
                                    <p key={idx} className="text-sm text-gray-700">
                                      <span className="font-mono bg-white px-2 py-1 rounded">
                                        {fk.column}
                                      </span>
                                      <span className="mx-2 text-purple-600">→</span>
                                      <span className="font-mono bg-white px-2 py-1 rounded">
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
                    <div className="text-center py-12 bg-white rounded-lg shadow-sm">
                      <Search className="mx-auto text-gray-400 mb-3" size={48} />
                      <p className="text-gray-500">No tables found matching &quot;{searchTerm}&quot;</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 bg-white rounded-lg shadow-sm">
                  <p className="text-red-500">Failed to load database schema</p>
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

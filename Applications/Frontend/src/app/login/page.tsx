"use client";

import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Eye, EyeOff, Lock, User, Sparkles, AlertCircle, CheckCircle, Moon, Sun } from "lucide-react";
import Link from "next/link";
import { useTheme } from "@/components/theme/ThemeProvider";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const { theme, toggleTheme } = useTheme();

  // Demo credentials - in production, this would be handled by backend
  const DEMO_CREDENTIALS = {
    username: "admin",
    password: "admin123",
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess(false);

    if (!username || !password) {
      setError("Please enter both username and password");
      return;
    }

    setLoading(true);

    // Simulate API call delay
    setTimeout(() => {
      // Basic authentication check
      if (username === DEMO_CREDENTIALS.username && password === DEMO_CREDENTIALS.password) {
        setSuccess(true);
        
        // Store session in localStorage
        localStorage.setItem("cenquery_user", JSON.stringify({
          username: username,
          loginTime: new Date().toISOString(),
          isAuthenticated: true
        }));

        // Redirect to dashboard after short delay
        setTimeout(() => {
          router.push("/dashboard");
        }, 1000);
      } else {
        setError("Invalid username or password");
        setLoading(false);
      }
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleLogin(e as any);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900 relative overflow-hidden">
      {/* Dark Mode Toggle (Top Right) */}
      <button
        onClick={toggleTheme}
        className="absolute top-6 right-6 p-3 rounded-full bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm shadow-lg hover:shadow-xl transition-all"
        aria-label="Toggle dark mode"
      >
        {theme === "dark" ? <Sun className="text-yellow-500" size={20} /> : <Moon className="text-blue-600" size={20} />}
      </button>

      {/* Decorative Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 dark:bg-blue-600 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-3xl opacity-30 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-200 dark:bg-purple-600 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-3xl opacity-30 animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-pink-200 dark:bg-pink-600 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-3xl opacity-20 animate-pulse delay-500"></div>
      </div>

      {/* Login Card */}
      <div className="relative z-10 w-full max-w-md px-6">
        {/* Logo and Title */}
        <div className="text-center mb-8 animate-in">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl shadow-lg mb-4">
            <Sparkles className="text-white" size={32} />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
            CenQuery
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Sign in to access the census query system
          </p>
        </div>

        {/* Login Form Card */}
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md p-8 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700">
          <form onSubmit={handleLogin} className="space-y-6">
            {/* Username Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Username
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="text-gray-400 dark:text-gray-500" size={20} />
                </div>
                <input
                  type="text"
                  placeholder="Enter your username"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent transition-all bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={loading}
                />
              </div>
            </div>

            {/* Password Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="text-gray-400 dark:text-gray-500" size={20} />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  className="w-full pl-10 pr-12 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent transition-all bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                  disabled={loading}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="flex items-center gap-2 p-3 text-red-700 dark:text-red-400 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg animate-in">
                <AlertCircle size={18} />
                <p className="text-sm">{error}</p>
              </div>
            )}

            {/* Success Message */}
            {success && (
              <div className="flex items-center gap-2 p-3 text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-lg animate-in">
                <CheckCircle size={18} />
                <p className="text-sm">Login successful! Redirecting...</p>
              </div>
            )}

            {/* Login Button */}
            <Button
              type="submit"
              className="w-full py-6 text-base font-semibold bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all duration-300"
              disabled={loading}
            >
              {loading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Signing in...
                </div>
              ) : (
                "Sign In"
              )}
            </Button>

            {/* Demo Credentials Info */}
            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg">
              <p className="text-xs font-semibold text-blue-900 dark:text-blue-300 mb-2">Demo Credentials:</p>
              <div className="space-y-1 text-xs text-blue-700 dark:text-blue-400">
                <p><span className="font-medium">Username:</span> admin</p>
                <p><span className="font-medium">Password:</span> admin123</p>
              </div>
            </div>
          </form>
        </div>

        {/* Back to Home Link */}
        <div className="text-center mt-6">
          <Link href="/" className="text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
            ← Back to Home
          </Link>
        </div>
      </div>
    </main>
  );
}

import React, { useState, useEffect, useCallback } from "react";

const PokemonPipeline = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [statusMessage, setStatusMessage] = useState(() => {
    const saved = sessionStorage.getItem("pokemonStatus");
    return saved
      ? JSON.parse(saved)
      : { type: "ready", text: "Ready to process your data" };
  });
  const [showFilters, setShowFilters] = useState(() => {
    return sessionStorage.getItem("showFilters") === "true";
  });
  const [showPokemon, setShowPokemon] = useState(() => {
    return sessionStorage.getItem("showPokemon") === "true";
  });
  const [pokemons, setPokemons] = useState(() => {
    const saved = sessionStorage.getItem("pokemons");
    return saved ? JSON.parse(saved) : [];
  });
  const [filters, setFilters] = useState(() => {
    const saved = sessionStorage.getItem("filters");
    return saved
      ? JSON.parse(saved)
      : { type: "", hpMin: "", isEvolved: false };
  });

  const loadFilteredPokemon = useCallback(async () => {
    const params = new URLSearchParams();
    if (filters.type.trim()) params.append("type_name", filters.type.trim());
    if (filters.hpMin) params.append("hp_min", filters.hpMin);
    if (filters.isEvolved) params.append("is_evolved", true);

    try {
      const response = await fetch(`http://localhost:8000/pokemon/filter_pokemons?${params.toString()}`);
      const data = await response.json();
      setPokemons(data);
      setShowPokemon(true);
    } catch (err) {
      setStatusMessage({
        type: "error",
        text: `Error loading Pokémon: ${err.message}`,
      });
    }
  }, [filters]);

  const handleRunPipeline = async () => {
    setIsProcessing(true);
    setStatusMessage({ type: "processing", text: "Running ETL Pipeline..." });
    setShowFilters(false);
    setShowPokemon(false);
    setPokemons([]);

    try {
      const response = await fetch("http://localhost:8000/pokemon/etl/run-pipeline", {
        method: "POST",
      });
      const data = await response.json();

      if (response.ok) {
        setStatusMessage({
          type: "success",
          text: data.detail || "Pipeline completed successfully!",
        });
        setShowFilters(true);
        await loadFilteredPokemon();
      } else {
        setStatusMessage({
          type: "error",
          text: data.detail || "Pipeline failed",
        });
      }
    } catch (err) {
      setStatusMessage({
        type: "error",
        text: `Error: ${err.message}`,
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters((prev) => ({ ...prev, [field]: value }));
  };

  useEffect(() => {
    if (showFilters) {
      loadFilteredPokemon();
    }
  }, [filters, showFilters, loadFilteredPokemon]);

  // Save state to sessionStorage whenever it changes
  useEffect(() => {
    sessionStorage.setItem("pokemonStatus", JSON.stringify(statusMessage));
  }, [statusMessage]);

  useEffect(() => {
    sessionStorage.setItem("showFilters", showFilters.toString());
  }, [showFilters]);

  useEffect(() => {
    sessionStorage.setItem("showPokemon", showPokemon.toString());
  }, [showPokemon]);

  useEffect(() => {
    sessionStorage.setItem("pokemons", JSON.stringify(pokemons));
  }, [pokemons]);

  useEffect(() => {
    sessionStorage.setItem("filters", JSON.stringify(filters));
  }, [filters]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-4 md:p-8 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob top-0 -left-20"></div>
        <div className="absolute w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000 top-20 right-20"></div>
        <div className="absolute w-96 h-96 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000 bottom-20 left-40"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12 animate-fade-in">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl mb-4 shadow-2xl transform hover:scale-110 transition-transform">
            <svg className="w-10 h-10" fill="currentColor" viewBox="0 0 20 20">
              <path d="M13 7H7v6h6V7z" />
              <path
                fillRule="evenodd"
                d="M7 2a1 1 0 012 0v1h2V2a1 1 0 112 0v1h2a2 2 0 012 2v2h1a1 1 0 110 2h-1v2h1a1 1 0 110 2h-1v2a2 2 0 01-2 2h-2v1a1 1 0 11-2 0v-1H9v1a1 1 0 11-2 0v-1H5a2 2 0 01-2-2v-2H2a1 1 0 110-2h1V9H2a1 1 0 010-2h1V5a2 2 0 012-2h2V2zM5 5h10v10H5V5z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <h1 className="text-5xl md:text-6xl font-black mb-3 bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
            Pokémon ETL Pipeline
          </h1>
          <p className="text-xl text-purple-300 font-medium">
            Extract • Transform • Load • Discover
          </p>
        </div>

        {/* Run Pipeline Button */}
        <div className="flex justify-center mb-10 animate-slide-up">
          <button
            onClick={handleRunPipeline}
            disabled={isProcessing}
            className="group relative px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl font-bold text-lg shadow-2xl hover:shadow-purple-500/50 transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            <span className="flex items-center gap-3">
              {isProcessing ? (
                <>
                  <svg
                    className="w-6 h-6 animate-spin"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Processing Pipeline...
                </>
              ) : (
                <>
                  <svg
                    className="w-6 h-6 group-hover:animate-pulse"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                  Execute ETL Pipeline
                </>
              )}
            </span>
          </button>
        </div>

        {/* Status Card */}
        <div className="bg-white/5 backdrop-blur-xl rounded-3xl p-8 mb-8 border border-white/10 shadow-2xl animate-fade-in">
          <div className="flex items-center gap-4">
            <div
              className={`w-16 h-16 rounded-2xl flex items-center justify-center ${
                statusMessage.type === "ready"
                  ? "bg-gradient-to-br from-blue-500 to-purple-500"
                  : statusMessage.type === "processing"
                  ? "bg-gradient-to-br from-yellow-500 to-orange-500"
                  : statusMessage.type === "success"
                  ? "bg-gradient-to-br from-green-500 to-emerald-500"
                  : "bg-gradient-to-br from-red-500 to-pink-500"
              }`}
            >
              {statusMessage.type === "processing" ? (
                <svg
                  className="w-8 h-8 animate-spin"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
              ) : statusMessage.type === "success" ||
                statusMessage.type === "ready" ? (
                <svg
                  className="w-8 h-8"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              ) : (
                <svg
                  className="w-8 h-8"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              )}
            </div>
            <p className="text-xl font-semibold">{statusMessage.text}</p>
          </div>
        </div>

        {/* Filter Section */}
        {showFilters && (
          <div className="bg-white/5 backdrop-blur-xl rounded-3xl p-8 mb-8 border border-white/10 shadow-2xl animate-slide-up">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-3xl font-bold flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                  <svg
                    className="w-6 h-6"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M3 3a1 1 0 011-1h12a1 1 0 011 1v3a1 1 0 01-.293.707L12 11.414V15a1 1 0 01-.293.707l-2 2A1 1 0 018 17v-5.586L3.293 6.707A1 1 0 013 6V3z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                Pokémon Filters
              </h2>
              <div className="px-6 py-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full font-bold shadow-lg">
                {pokemons.length} Found
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block mb-2 text-sm font-semibold text-purple-300 uppercase">
                  Type
                </label>
                <input
                  type="text"
                  value={filters.type}
                  onChange={(e) => handleFilterChange("type", e.target.value)}
                  placeholder="e.g., water, fire..."
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50 outline-none transition-all"
                />
              </div>
              <div>
                <label className="block mb-2 text-sm font-semibold text-purple-300 uppercase">
                  Min HP
                </label>
                <input
                  type="number"
                  value={filters.hpMin}
                  onChange={(e) => handleFilterChange("hpMin", e.target.value)}
                  placeholder="50"
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50 outline-none transition-all"
                />
              </div>
              <div className="flex items-end">
                <label className="flex items-center gap-3 cursor-pointer w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl hover:border-purple-500 transition-all">
                  <input
                    type="checkbox"
                    checked={filters.isEvolved}
                    onChange={(e) =>
                      handleFilterChange("isEvolved", e.target.checked)
                    }
                    className="w-5 h-5 rounded accent-purple-500"
                  />
                  <span className="font-semibold">Evolved Only</span>
                </label>
              </div>
            </div>
          </div>
        )}

        {/* Pokemon Grid */}
        {showPokemon && (
          <div className="animate-fade-in">
            {pokemons.length === 0 ? (
              <div className="bg-white/5 backdrop-blur-xl rounded-3xl p-16 text-center border border-white/10 shadow-2xl">
                <div className="w-24 h-24 mx-auto mb-4 bg-gradient-to-br from-gray-600 to-gray-800 rounded-full flex items-center justify-center">
                  <svg
                    className="w-12 h-12 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <p className="text-2xl text-gray-400 font-semibold">
                  No Pokémon match your filters
                </p>
                <p className="text-gray-500 mt-2">
                  Try adjusting your search criteria
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {pokemons.map((pokemon, idx) => (
                  <div
                    key={idx}
                    className="group bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10 hover:border-purple-500/50 shadow-xl hover:shadow-2xl hover:shadow-purple-500/20 transition-all duration-300 hover:-translate-y-2 animate-scale-in"
                    style={{ animationDelay: `${idx * 0.05}s` }}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center font-black text-2xl shadow-lg group-hover:scale-110 transition-transform">
                        {pokemon.name.charAt(0).toUpperCase()}
                      </div>
                    </div>

                    <h3 className="text-2xl font-bold mb-4 capitalize group-hover:text-purple-400 transition-colors">
                      {pokemon.name}
                    </h3>

                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-400 font-medium">
                          HP
                        </span>
                        <div className="flex items-center gap-2">
                          <div className="w-32 h-2 bg-white/10 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-green-500 to-emerald-500 rounded-full transition-all duration-1000"
                              style={{
                                width: `${Math.min(
                                  (pokemon.hp / 200) * 100,
                                  100
                                )}%`,
                              }}
                            ></div>
                          </div>
                          <span className="text-lg font-bold text-green-400 min-w-[3rem] text-right">
                            {pokemon.hp}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <style>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        
        .animate-blob {
          animation: blob 7s infinite;
        }
        
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        
        .animation-delay-4000 {
          animation-delay: 4s;
        }
        
        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        .animate-fade-in {
          animation: fade-in 0.6s ease-out;
        }
        
        @keyframes slide-up {
          from { 
            opacity: 0;
            transform: translateY(20px);
          }
          to { 
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-slide-up {
          animation: slide-up 0.5s ease-out;
        }
        
        @keyframes scale-in {
          from {
            opacity: 0;
            transform: scale(0.9);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        
        .animate-scale-in {
          animation: scale-in 0.4s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default PokemonPipeline;

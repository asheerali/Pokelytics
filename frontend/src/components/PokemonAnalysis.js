import React, { useState } from "react";
import Plot from "react-plotly.js";
import "./PokemonAnalysis.css";

const PokemonAnalysis = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);
  const [error, setError] = useState(null);

  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/pokemon/analysis");
      const data = await response.json();

      if (response.ok) {
        setAnalysisData(data.data); // Extract the data object
      } else {
        setError("Failed to generate analysis");
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Color palettes for different chart types
  const COLORS = [
    "#ff6b6b",
    "#4ecdc4",
    "#ffc371",
    "#ff8e53",
    "#44a08d",
    "#f38181",
    "#aa96da",
    "#fcbad3",
    "#a8e6cf",
    "#ffd3b6",
    "#ffaaa5",
    "#ff8b94",
    "#a8dadc",
    "#457b9d",
    "#1d3557",
  ];

  // Common plot layout settings for dark theme
  const getPlotLayout = (title) => ({
    title: {
      text: "",
      font: { color: "#ffffff" },
    },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: {
      color: "#94a3b8",
      family: "Space Grotesk, sans-serif",
    },
    margin: { t: 40, b: 80, l: 60, r: 40 },
    hovermode: "closest",
  });

  // Generate Radar Chart
  const generateRadarChart = (data) => {
    const stats = Object.keys(data);
    const values = Object.values(data);

    return {
      data: [
        {
          type: "scatterpolar",
          r: values,
          theta: stats.map((stat) => stat.replace(/-/g, " ").toUpperCase()),
          fill: "toself",
          fillcolor: "rgba(255, 107, 107, 0.5)",
          line: {
            color: "#ff6b6b",
            width: 2,
          },
          marker: {
            color: "#ff6b6b",
            size: 8,
          },
        },
      ],
      layout: {
        ...getPlotLayout(),
        polar: {
          radialaxis: {
            visible: true,
            range: [0, Math.max(...values) * 1.2],
            color: "#94a3b8",
            gridcolor: "rgba(255, 255, 255, 0.1)",
          },
          angularaxis: {
            color: "#94a3b8",
            gridcolor: "rgba(255, 255, 255, 0.1)",
          },
          bgcolor: "rgba(0,0,0,0)",
        },
        showlegend: false,
      },
    };
  };

  // Generate Pie Chart
  const generatePieChart = (data) => {
    const labels = Object.keys(data).map(
      (key) => key.charAt(0).toUpperCase() + key.slice(1)
    );
    const values = Object.values(data);

    return {
      data: [
        {
          type: "pie",
          labels: labels,
          values: values,
          marker: {
            colors: COLORS,
            line: {
              color: "#1e1e2e",
              width: 2,
            },
          },
          textinfo: "label+percent",
          textposition: "outside",
          automargin: true,
          hovertemplate:
            "<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
        },
      ],
      layout: {
        ...getPlotLayout(),
        showlegend: true,
        legend: {
          font: { color: "#94a3b8" },
          bgcolor: "rgba(0,0,0,0)",
        },
      },
    };
  };

  // Generate Bar Chart
  const generateBarChart = (data) => {
    const labels = Object.keys(data).map((key) =>
      key
        .replace(/-/g, " ")
        .split(" ")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ")
    );
    const values = Object.values(data);

    return {
      data: [
        {
          type: "bar",
          x: labels,
          y: values,
          marker: {
            color: "#4ecdc4",
            line: {
              color: "#44a08d",
              width: 1,
            },
          },
          hovertemplate: "<b>%{x}</b><br>Count: %{y}<extra></extra>",
        },
      ],
      layout: {
        ...getPlotLayout(),
        xaxis: {
          color: "#94a3b8",
          gridcolor: "rgba(255, 255, 255, 0.1)",
          tickangle: -45,
        },
        yaxis: {
          color: "#94a3b8",
          gridcolor: "rgba(255, 255, 255, 0.1)",
          title: "Count",
        },
      },
    };
  };

  // Render chart based on type
  const renderChart = (chartData, index) => {
    const { title, type, data } = chartData;

    let plotData = null;

    if (type === "radar") {
      plotData = generateRadarChart(data);
    } else if (type === "pie") {
      plotData = generatePieChart(data);
    } else if (type === "bar") {
      plotData = generateBarChart(data);
    }

    const getIcon = () => {
      if (type === "radar") return "radar-icon";
      if (type === "pie") return "pie-icon";
      return "bar-icon";
    };

    const getIconSvg = () => {
      if (type === "radar") {
        return (
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M13 10V3L4 14h7v7l9-11h-7z"
          />
        );
      }
      if (type === "pie") {
        return (
          <>
            <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
            <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
          </>
        );
      }
      return (
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        />
      );
    };

    return (
      <div
        key={index}
        className={`chart-card ${
          type === "bar" && Object.keys(data).length > 10
            ? "chart-card-wide"
            : ""
        }`}
        style={{ animationDelay: `${index * 0.1}s` }}
      >
        <div className="chart-header">
          <div className={`chart-icon ${getIcon()}`}>
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {getIconSvg()}
            </svg>
          </div>
          <h3 className="chart-title">{title}</h3>
        </div>
        <div className="chart-container">
          {plotData && (
            <Plot
              data={plotData.data}
              layout={plotData.layout}
              config={{
                responsive: true,
                displayModeBar: false,
              }}
              style={{ width: "100%", height: "400px" }}
              useResizeHandler={true}
            />
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="analysis-container">
      {/* Background elements */}
      <div className="analysis-bg-gradient"></div>
      <div className="grid-pattern"></div>

      {/* Animated circles */}
      {[...Array(4)].map((_, i) => (
        <div
          key={i}
          className="floating-circle"
          style={{
            left: `${25 * i}%`,
            animationDelay: `${i * 2}s`,
            animationDuration: `${15 + i * 3}s`,
          }}
        ></div>
      ))}

      <div className="analysis-content">
        {/* Header Section */}
        <div className="analysis-header fade-in">
          <div className="header-badge">
            <svg
              className="w-10 h-10"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
          <h1 className="analysis-title">Data Analytics Dashboard</h1>
          <p className="analysis-subtitle">
            Deep dive into your Pokémon statistics
          </p>
        </div>

        {/* Action Button */}
        <div className="button-container fade-in-delay">
          <button
            onClick={handleRunAnalysis}
            disabled={isAnalyzing}
            className="analyze-button"
          >
            <span className="button-content">
              {isAnalyzing ? (
                <>
                  <svg
                    className="button-icon spinner"
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
                  <span>Computing Analytics...</span>
                </>
              ) : (
                <>
                  <svg
                    className="button-icon"
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
                  <span>Run Analysis</span>
                </>
              )}
            </span>
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="error-card slide-up">
            <svg
              className="error-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <p>{error}</p>
          </div>
        )}

        {/* Charts Section */}
        {analysisData && (
          <div className="charts-section slide-up">
            <div className="section-header">
              <div className="section-icon">
                <svg
                  className="w-6 h-6"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
                  <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
                </svg>
              </div>
              <h2 className="section-title">Statistical Breakdown</h2>
            </div>

            <div className="charts-grid">
              {Object.entries(analysisData).map(([key, chartData], index) =>
                renderChart(chartData, index)
              )}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!analysisData && !error && !isAnalyzing && (
          <div className="empty-state-analysis fade-in">
            <div className="empty-illustration">
              <svg
                className="empty-icon"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <h3 className="empty-title">No Analysis Data Yet</h3>
            <p className="empty-description">
              Click the button above to generate comprehensive statistical
              analysis
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PokemonAnalysis;

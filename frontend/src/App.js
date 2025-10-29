import React, { useState } from 'react';
import './App.css';
import PokemonPipeline from './components/PokemonPipeline';
import PokemonAnalysis from './components/PokemonAnalysis';

function App() {
  const [currentView, setCurrentView] = useState('pipeline'); // 'pipeline' or 'analysis'

  return (
    <div className="App">
      {/* Navigation */}
      <nav className="app-nav">
        <div className="nav-container">
          <div className="nav-logo">
            <svg className="logo-svg" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
              <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd"/>
            </svg>
            <span>Pokémon Hub</span>
          </div>
          
          <div className="nav-links">
            <button
              className={`nav-link ${currentView === 'pipeline' ? 'active' : ''}`}
              onClick={() => setCurrentView('pipeline')}
            >
              <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"/>
              </svg>
              ETL Pipeline
            </button>
            
            <button
              className={`nav-link ${currentView === 'analysis' ? 'active' : ''}`}
              onClick={() => setCurrentView('analysis')}
            >
              <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
              Analytics
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className="app-content">
        {currentView === 'pipeline' ? <PokemonPipeline /> : <PokemonAnalysis />}
      </div>
    </div>
  );
}

export default App;
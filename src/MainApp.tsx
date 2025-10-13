import React, { useState } from 'react';
import App from './App';
import AnomalyDashboard from './AnomalyDashboard';
import SubexecutionDashboard from './SubexecutionDashboard';

type DashboardView = 'main' | 'anomaly' | 'subexecution';

function MainApp() {
  const [currentView, setCurrentView] = useState<DashboardView>('subexecution');

  return (
    <div>
      {/* Navigation Menu */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        backgroundColor: '#2e3138',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
        zIndex: 1000
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          padding: '16px 32px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          {/* Logo/Title */}
          <div style={{
            fontSize: '20px',
            fontWeight: '700',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <span style={{ fontSize: '24px' }}>📊</span>
            <span>Dashboard Orçamentário</span>
          </div>

          {/* Navigation Buttons */}
          <div style={{
            display: 'flex',
            gap: '12px'
          }}>
            <button
              onClick={() => setCurrentView('subexecution')}
              style={{
                padding: '10px 20px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: currentView === 'subexecution' ? '#9755fe' : 'transparent',
                color: '#ffffff',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
              onMouseEnter={(e) => {
                if (currentView !== 'subexecution') {
                  e.currentTarget.style.backgroundColor = 'rgba(151, 85, 254, 0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (currentView !== 'subexecution') {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
            >
              <span>🎯</span>
              <span>Ranking Subexecução</span>
            </button>

            <button
              onClick={() => setCurrentView('anomaly')}
              style={{
                padding: '10px 20px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: currentView === 'anomaly' ? '#9755fe' : 'transparent',
                color: '#ffffff',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
              onMouseEnter={(e) => {
                if (currentView !== 'anomaly') {
                  e.currentTarget.style.backgroundColor = 'rgba(151, 85, 254, 0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (currentView !== 'anomaly') {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
            >
              <span>🚨</span>
              <span>Análise de Anomalias</span>
            </button>

            <button
              onClick={() => setCurrentView('main')}
              style={{
                padding: '10px 20px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: currentView === 'main' ? '#9755fe' : 'transparent',
                color: '#ffffff',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
              onMouseEnter={(e) => {
                if (currentView !== 'main') {
                  e.currentTarget.style.backgroundColor = 'rgba(151, 85, 254, 0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (currentView !== 'main') {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
            >
              <span>📈</span>
              <span>Dashboard Principal</span>
            </button>
          </div>
        </div>
      </div>

      {/* Content Area with padding for fixed menu */}
      <div style={{ paddingTop: '72px' }}>
        {currentView === 'subexecution' && <SubexecutionDashboard />}
        {currentView === 'anomaly' && <AnomalyDashboard />}
        {currentView === 'main' && <App />}
      </div>
    </div>
  );
}

export default MainApp;

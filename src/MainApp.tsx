import React, { useState } from 'react';
import App from './App';
import AnomalyDashboard from './AnomalyDashboard';
import SubexecutionDashboard from './SubexecutionDashboard';
import AdvancedAnalysisDashboard from './AdvancedAnalysisDashboard';
import MunicipalityDetailDashboard from './MunicipalityDetailDashboard';
import StrategicDashboard from './StrategicDashboard';
import OportunidadesPage from './OportunidadesPage';

type DashboardView = 'main' | 'anomaly' | 'subexecution' | 'advanced' | 'detail' | 'strategic' | 'oportunidades';

function MainApp() {
  const [currentView, setCurrentView] = useState<DashboardView>('strategic');

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
            gap: '8px'
          }}>
            <button
              onClick={() => setCurrentView('strategic')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: currentView === 'strategic' ? '#9755fe' : 'transparent',
                color: '#ffffff',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
              onMouseEnter={(e) => {
                if (currentView !== 'strategic') {
                  e.currentTarget.style.backgroundColor = 'rgba(151, 85, 254, 0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (currentView !== 'strategic') {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
            >
              <span>⚡</span>
              <span>Painel Estratégico</span>
            </button>

            <button
              onClick={() => setCurrentView('detail')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: currentView === 'detail' ? '#9755fe' : 'transparent',
                color: '#ffffff',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
              onMouseEnter={(e) => {
                if (currentView !== 'detail') {
                  e.currentTarget.style.backgroundColor = 'rgba(151, 85, 254, 0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (currentView !== 'detail') {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
            >
              <span>🏛️</span>
              <span>Drill-Down</span>
            </button>

            <button
              onClick={() => setCurrentView('advanced')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: currentView === 'advanced' ? '#9755fe' : 'transparent',
                color: '#ffffff',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
              onMouseEnter={(e) => {
                if (currentView !== 'advanced') {
                  e.currentTarget.style.backgroundColor = 'rgba(151, 85, 254, 0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (currentView !== 'advanced') {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
            >
              <span>🧠</span>
              <span>ML</span>
            </button>

            <button
              onClick={() => setCurrentView('subexecution')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: currentView === 'subexecution' ? '#9755fe' : 'transparent',
                color: '#ffffff',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
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
              <span>Ranking</span>
            </button>

            <button
              onClick={() => setCurrentView('anomaly')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: currentView === 'anomaly' ? '#9755fe' : 'transparent',
                color: '#ffffff',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
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
              <span>Anomalias</span>
            </button>

            <button
              onClick={() => setCurrentView('oportunidades')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: currentView === 'oportunidades' ? '#9755fe' : 'transparent',
                color: '#ffffff',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
              onMouseEnter={(e) => {
                if (currentView !== 'oportunidades') {
                  e.currentTarget.style.backgroundColor = 'rgba(151, 85, 254, 0.2)';
                }
              }}
              onMouseLeave={(e) => {
                if (currentView !== 'oportunidades') {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
            >
              <span>💎</span>
              <span>Oportunidades</span>
            </button>

            <button
              onClick={() => setCurrentView('main')}
              style={{
                padding: '10px 16px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: currentView === 'main' ? '#9755fe' : 'transparent',
                color: '#ffffff',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
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
              <span>Principal</span>
            </button>
          </div>
        </div>
      </div>

      {/* Content Area with padding for fixed menu */}
      <div style={{ paddingTop: '72px' }}>
        {currentView === 'strategic' && <StrategicDashboard />}
        {currentView === 'detail' && <MunicipalityDetailDashboard />}
        {currentView === 'advanced' && <AdvancedAnalysisDashboard />}
        {currentView === 'subexecution' && <SubexecutionDashboard />}
        {currentView === 'anomaly' && <AnomalyDashboard />}
        {currentView === 'oportunidades' && <OportunidadesPage />}
        {currentView === 'main' && <App />}
      </div>
    </div>
  );
}

export default MainApp;

import React, { useState, useMemo } from 'react';
import Calendar from './components/Calendar';
import KPICard from './components/KPICard';
import ComparisonChart from './components/ComparisonChart';
import TrendAnalysisChart from './components/TrendAnalysisChart';
import TraditionalCharts from './components/TraditionalCharts';
import { mockData } from './mockData';
import { ComparisonType, IndicatorType, AnalysisMode } from './types';
import { getMonthName, calculateVariation } from './utils';

function App() {
  // Estados principais
  const [selectedYear, setSelectedYear] = useState(2024);
  const [selectedMonth, setSelectedMonth] = useState(6);
  const [showCalendar, setShowCalendar] = useState(false);
  const [comparisonType, setComparisonType] = useState<ComparisonType>('same-month-last-year');
  const [indicator, setIndicator] = useState<IndicatorType>('executed');
  const [selectedMonths, setSelectedMonths] = useState<number[]>([6]);
  const [analysisMode, setAnalysisMode] = useState<AnalysisMode>('absolute');

  // Dados filtrados
  const currentPeriodData = useMemo(() => {
    return mockData.filter(d => d.year === selectedYear && d.month === selectedMonth)[0];
  }, [selectedYear, selectedMonth]);

  const comparisonPeriodData = useMemo(() => {
    switch (comparisonType) {
      case 'same-month-last-year':
        return mockData.find(d => d.year === selectedYear - 1 && d.month === selectedMonth);
      case 'previous-month':
        const prevMonth = selectedMonth === 1 ? 12 : selectedMonth - 1;
        const prevYear = selectedMonth === 1 ? selectedYear - 1 : selectedYear;
        return mockData.find(d => d.year === prevYear && d.month === prevMonth);
      case 'electoral-period':
        // Encontra o último ano eleitoral anterior
        const previousElectionYear = selectedYear % 2 === 0 ? selectedYear - 2 : selectedYear - 1;
        return mockData.find(d => d.year === previousElectionYear && d.month === selectedMonth);
      default:
        return currentPeriodData;
    }
  }, [selectedYear, selectedMonth, comparisonType, currentPeriodData]);

  // Dados para gráfico de comparação
  const currentYearData = useMemo(() => {
    return mockData.filter(d => d.year === selectedYear);
  }, [selectedYear]);

  const comparisonYearData = useMemo(() => {
    const compYear = comparisonType === 'same-month-last-year' || comparisonType === 'electoral-period'
      ? selectedYear - 1
      : selectedYear;
    return mockData.filter(d => d.year === compYear);
  }, [selectedYear, comparisonType]);

  // Cálculos de variação
  const variation = useMemo(() => {
    if (!comparisonPeriodData) return 0;
    return calculateVariation(currentPeriodData.executed, comparisonPeriodData.executed);
  }, [currentPeriodData, comparisonPeriodData]);

  // Handlers
  const handleDateSelect = (year: number, month: number) => {
    setSelectedYear(year);
    setSelectedMonth(month);
  };

  const handleMonthToggle = (month: number) => {
    setSelectedMonths(prev =>
      prev.includes(month)
        ? prev.filter(m => m !== month)
        : [...prev, month].sort((a, b) => a - b)
    );
  };

  const getComparisonLabel = () => {
    switch (comparisonType) {
      case 'same-month-last-year':
        return `${getMonthName(selectedMonth)} ${selectedYear - 1}`;
      case 'previous-month':
        const prevMonth = selectedMonth === 1 ? 12 : selectedMonth - 1;
        return getMonthName(prevMonth);
      case 'electoral-period':
        return `Período Eleitoral ${selectedYear - 2}`;
      default:
        return 'Comparativo';
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f9f4ff',
      padding: '32px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    }}>
      {/* Header */}
      <div style={{
        marginBottom: '32px'
      }}>
        <h1 style={{
          fontSize: '32px',
          fontWeight: '700',
          color: '#2e3138',
          marginBottom: '8px'
        }}>
          Dashboard de Análise Orçamentária
        </h1>
        <p style={{
          fontSize: '16px',
          color: '#6b7280',
          margin: 0
        }}>
          Educação · Análise multidimensional de dados governamentais
        </p>
      </div>

      {/* Controles Principais */}
      <div style={{
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '24px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
        border: '1px solid #f5edff'
      }}>
        <div style={{
          display: 'flex',
          gap: '16px',
          flexWrap: 'wrap',
          alignItems: 'center'
        }}>
          {/* Botão de Período com Calendário */}
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setShowCalendar(!showCalendar)}
              style={{
                padding: '12px 20px',
                borderRadius: '8px',
                border: '2px solid #9755fe',
                backgroundColor: '#ffffff',
                color: '#3f127d',
                fontSize: '15px',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f5edff';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#ffffff';
              }}
            >
              📅 {getMonthName(selectedMonth)} {selectedYear}
            </button>
            {showCalendar && (
              <Calendar
                selectedYear={selectedYear}
                selectedMonth={selectedMonth}
                onDateSelect={handleDateSelect}
                onClose={() => setShowCalendar(false)}
              />
            )}
          </div>

          {/* Tipo de Comparação */}
          <select
            value={comparisonType}
            onChange={(e) => setComparisonType(e.target.value as ComparisonType)}
            style={{
              padding: '12px 16px',
              borderRadius: '8px',
              border: '1px solid #d1b3ff',
              backgroundColor: '#ffffff',
              color: '#2e3138',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              outline: 'none'
            }}
          >
            <option value="same-month-last-year">Mesmo mês ano anterior</option>
            <option value="previous-month">Mês anterior</option>
            <option value="electoral-period">Período eleitoral</option>
          </select>
        </div>
      </div>

      {/* KPIs */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '24px',
        marginBottom: '24px'
      }}>
        <KPICard
          title="Período Atual"
          currentValue={currentPeriodData.executed}
          comparisonValue={0}
          variation={0}
          isCurrentPeriod={true}
        />
        <KPICard
          title="Período Comparativo"
          currentValue={0}
          comparisonValue={comparisonPeriodData?.executed || 0}
          variation={0}
          isCurrentPeriod={true}
        />
        <KPICard
          title="Variação"
          currentValue={currentPeriodData.executed}
          comparisonValue={comparisonPeriodData?.executed || 0}
          variation={variation}
        />
      </div>

      {/* Gráfico de Comparação Dinâmica */}
      <div style={{ marginBottom: '24px' }}>
        <ComparisonChart
          currentData={currentYearData}
          comparisonData={comparisonYearData}
          indicator={indicator}
          selectedMonths={selectedMonths}
          onIndicatorChange={setIndicator}
          onMonthToggle={handleMonthToggle}
          currentLabel={`${selectedYear}`}
          comparisonLabel={getComparisonLabel()}
        />
      </div>

      {/* Gráfico de Análise de Tendências */}
      <div style={{ marginBottom: '24px' }}>
        <TrendAnalysisChart
          data={mockData}
          analysisMode={analysisMode}
          onModeChange={setAnalysisMode}
        />
      </div>

      {/* Gráficos Tradicionais */}
      <TraditionalCharts
        data={mockData}
        selectedYear={selectedYear}
      />

      {/* Footer */}
      <div style={{
        marginTop: '48px',
        padding: '24px',
        textAlign: 'center',
        color: '#6b7280',
        fontSize: '14px'
      }}>
        <p style={{ margin: 0 }}>
          Dashboard desenvolvido para análise de dados orçamentários governamentais
        </p>
        <p style={{ margin: '8px 0 0 0', fontSize: '12px' }}>
          Dados mock para fins de demonstração · {new Date().getFullYear()}
        </p>
      </div>
    </div>
  );
}

export default App;

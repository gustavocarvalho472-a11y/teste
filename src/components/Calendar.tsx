import React from 'react';
import { getMonthName } from '../utils';

interface CalendarProps {
  selectedYear: number;
  selectedMonth: number;
  onDateSelect: (year: number, month: number) => void;
  onClose: () => void;
}

const Calendar: React.FC<CalendarProps> = ({
  selectedYear,
  selectedMonth,
  onDateSelect,
  onClose
}) => {
  const years = [2020, 2021, 2022, 2023, 2024];
  const months = Array.from({ length: 12 }, (_, i) => i + 1);
  const electionYears = [2020, 2022, 2024];

  const handleDateClick = (year: number, month: number) => {
    onDateSelect(year, month);
    onClose();
  };

  return (
    <div style={{
      position: 'absolute',
      top: '60px',
      left: '0',
      backgroundColor: '#ffffff',
      border: '1px solid #d1b3ff',
      borderRadius: '8px',
      padding: '16px',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
      zIndex: 1000,
      minWidth: '320px'
    }}>
      {/* Anos */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{
          fontSize: '14px',
          fontWeight: '600',
          color: '#2e3138',
          marginBottom: '8px'
        }}>
          Ano
        </div>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(5, 1fr)',
          gap: '8px'
        }}>
          {years.map(year => (
            <button
              key={year}
              onClick={() => {
                if (year !== selectedYear) {
                  handleDateClick(year, selectedMonth);
                }
              }}
              style={{
                padding: '8px',
                borderRadius: '6px',
                border: selectedYear === year ? '2px solid #9755fe' : '1px solid #e1cdfe',
                backgroundColor: selectedYear === year ? '#f5edff' : '#ffffff',
                color: selectedYear === year ? '#3f127d' : '#2e3138',
                fontSize: '14px',
                fontWeight: selectedYear === year ? '600' : '400',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                if (selectedYear !== year) {
                  e.currentTarget.style.backgroundColor = '#f9f4ff';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedYear !== year) {
                  e.currentTarget.style.backgroundColor = '#ffffff';
                }
              }}
            >
              {year}
              {electionYears.includes(year) && ' 🗳️'}
            </button>
          ))}
        </div>
      </div>

      {/* Meses */}
      <div>
        <div style={{
          fontSize: '14px',
          fontWeight: '600',
          color: '#2e3138',
          marginBottom: '8px'
        }}>
          Mês
        </div>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '8px'
        }}>
          {months.map(month => (
            <button
              key={month}
              onClick={() => handleDateClick(selectedYear, month)}
              style={{
                padding: '8px',
                borderRadius: '6px',
                border: selectedMonth === month ? '2px solid #9755fe' : '1px solid #e1cdfe',
                backgroundColor: selectedMonth === month ? '#f5edff' : '#ffffff',
                color: selectedMonth === month ? '#3f127d' : '#2e3138',
                fontSize: '13px',
                fontWeight: selectedMonth === month ? '600' : '400',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                if (selectedMonth !== month) {
                  e.currentTarget.style.backgroundColor = '#f9f4ff';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedMonth !== month) {
                  e.currentTarget.style.backgroundColor = '#ffffff';
                }
              }}
            >
              {getMonthName(month).substring(0, 3)}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Calendar;

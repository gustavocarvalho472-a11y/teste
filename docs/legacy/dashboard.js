// Initialize Lucide icons
lucide.createIcons();

// Mock data for charts and visualizations
const mockData = {
    timeline: {
        years: [2016, 2017, 2018, 2019, 2020],
        approved: [2.8, 3.1, 3.2, 3.4, 4.0],
        committed: [2.6, 2.9, 3.0, 3.2, 3.8],
        executed: [2.4, 2.7, 2.8, 3.0, 3.6],
        electoralYears: [2016, 2020]
    },
    regions: {
        'Norte': { variation: '+12.3%', execution: '84.2%', municipalities: 450 },
        'Nordeste': { variation: '+15.7%', execution: '86.1%', municipalities: 1794 },
        'Centro-Oeste': { variation: '+22.1%', execution: '89.3%', municipalities: 467 },
        'Sudeste': { variation: '+18.9%', execution: '87.8%', municipalities: 1668 },
        'Sul': { variation: '+16.4%', execution: '85.6%', municipalities: 1191 }
    }
};

// Chart configuration
let timelineChart;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeChart();
    initializeFilters();
    initializeTooltips();
    initializeMapInteractions();
    initializeCTAButtons();
});

// Initialize timeline chart
function initializeChart() {
    const ctx = document.getElementById('timeline-chart').getContext('2d');
    
    timelineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: mockData.timeline.years,
            datasets: [
                {
                    label: 'Orçamento Aprovado',
                    data: mockData.timeline.approved,
                    borderColor: '#8352F5',
                    backgroundColor: 'rgba(131, 82, 245, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointBackgroundColor: function(context) {
                        const year = mockData.timeline.years[context.dataIndex];
                        return mockData.timeline.electoralYears.includes(year) ? '#8352F5' : '#AA80FF';
                    },
                    pointBorderColor: function(context) {
                        const year = mockData.timeline.years[context.dataIndex];
                        return mockData.timeline.electoralYears.includes(year) ? '#FFFFFF' : '#8352F5';
                    },
                    pointBorderWidth: function(context) {
                        const year = mockData.timeline.years[context.dataIndex];
                        return mockData.timeline.electoralYears.includes(year) ? 3 : 2;
                    }
                },
                {
                    label: 'Orçamento Empenhado',
                    data: mockData.timeline.committed,
                    borderColor: '#AA80FF',
                    backgroundColor: 'rgba(170, 128, 255, 0.1)',
                    fill: false,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'Orçamento Executado',
                    data: mockData.timeline.executed,
                    borderColor: '#CCB5FF',
                    backgroundColor: 'rgba(204, 181, 255, 0.1)',
                    fill: false,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        color: '#111827'
                    }
                },
                tooltip: {
                    backgroundColor: '#111827',
                    titleColor: '#FFFFFF',
                    bodyColor: '#FFFFFF',
                    borderColor: '#8352F5',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        title: function(context) {
                            const year = context[0].label;
                            const isElectoral = mockData.timeline.electoralYears.includes(parseInt(year));
                            return `${year}${isElectoral ? ' (Ano Eleitoral)' : ''}`;
                        },
                        label: function(context) {
                            return `${context.dataset.label}: R$ ${context.parsed.y.toFixed(1)}B`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Ano',
                        color: '#6B7280'
                    },
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#6B7280'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Orçamento (R$ Bilhões)',
                        color: '#6B7280'
                    },
                    grid: {
                        color: '#E5E7EB'
                    },
                    ticks: {
                        color: '#6B7280',
                        callback: function(value) {
                            return 'R$ ' + value.toFixed(1) + 'B';
                        }
                    }
                }
            }
        }
    });
}

// Initialize filters
function initializeFilters() {
    const periodFilter = document.getElementById('period-filter');
    const regionFilter = document.getElementById('region-filter');
    const indicatorsFilter = document.getElementById('indicators-filter');
    const applyButton = document.getElementById('apply-filters');
    const clearButton = document.getElementById('clear-filters');

    // Apply filters
    applyButton.addEventListener('click', function() {
        const selectedPeriods = Array.from(periodFilter.selectedOptions).map(option => option.value);
        const selectedRegion = regionFilter.value;
        const selectedIndicators = Array.from(indicatorsFilter.selectedOptions).map(option => option.value);
        
        // Simulate filter application
        showFilterFeedback('Filtros aplicados com sucesso!');
        updateChartData(selectedPeriods);
    });

    // Clear filters
    clearButton.addEventListener('click', function() {
        periodFilter.selectedIndex = -1;
        regionFilter.selectedIndex = 0;
        indicatorsFilter.selectedIndex = -1;
        
        // Reset to default selections
        Array.from(periodFilter.options).forEach(option => option.selected = true);
        Array.from(indicatorsFilter.options).forEach(option => option.selected = true);
        
        showFilterFeedback('Filtros limpos!');
        updateChartData(mockData.timeline.years);
    });
}

// Show filter feedback
function showFilterFeedback(message) {
    const feedback = document.createElement('div');
    feedback.textContent = message;
    feedback.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #22c55e;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 14px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(feedback);
    
    setTimeout(() => {
        feedback.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => feedback.remove(), 300);
    }, 2000);
}

// Update chart data based on filters
function updateChartData(periods) {
    if (!timelineChart) return;
    
    const filteredData = mockData.timeline.years.map((year, index) => {
        if (periods.includes(year.toString())) {
            return {
                approved: mockData.timeline.approved[index],
                committed: mockData.timeline.committed[index],
                executed: mockData.timeline.executed[index]
            };
        }
        return null;
    }).filter(Boolean);
    
    timelineChart.update();
}

// Initialize tooltips
function initializeTooltips() {
    const tooltip = document.getElementById('tooltip');
    const regions = document.querySelectorAll('.region');
    
    regions.forEach(region => {
        region.addEventListener('mouseenter', function(e) {
            const regionName = this.dataset.region;
            const variation = this.dataset.variation;
            const execution = this.dataset.execution;
            const regionData = mockData.regions[regionName];
            
            tooltip.innerHTML = `
                <div class="tooltip-content">
                    <strong>${regionName}</strong><br>
                    Variação: ${variation}<br>
                    Execução: ${execution}<br>
                    Municípios: ${regionData.municipalities}
                </div>
            `;
            
            tooltip.classList.add('visible');
            updateTooltipPosition(e);
        });
        
        region.addEventListener('mouseleave', function() {
            tooltip.classList.remove('visible');
        });
        
        region.addEventListener('mousemove', updateTooltipPosition);
    });
}

// Update tooltip position
function updateTooltipPosition(e) {
    const tooltip = document.getElementById('tooltip');
    const offset = 10;
    
    tooltip.style.left = (e.pageX + offset) + 'px';
    tooltip.style.top = (e.pageY + offset) + 'px';
}

// Initialize map interactions
function initializeMapInteractions() {
    const toggleButtons = document.querySelectorAll('.toggle-btn');
    const metricFilter = document.getElementById('metric-filter');
    
    // Toggle view (region/municipality)
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            toggleButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const view = this.dataset.view;
            updateMapView(view);
        });
    });
    
    // Metric filter change
    metricFilter.addEventListener('change', function() {
        const metric = this.value;
        updateMapMetric(metric);
    });
}

// Update map view
function updateMapView(view) {
    const mapContainer = document.querySelector('.brazil-map');
    
    if (view === 'municipality') {
        mapContainer.style.opacity = '0.7';
        // In a real implementation, you would load municipality data
        console.log('Switching to municipality view');
    } else {
        mapContainer.style.opacity = '1';
        console.log('Switching to region view');
    }
}

// Update map metric
function updateMapMetric(metric) {
    const regions = document.querySelectorAll('.region');
    
    // Simulate different color schemes based on metric
    regions.forEach(region => {
        switch(metric) {
            case 'execution':
                region.style.backgroundColor = '#22c55e';
                break;
            case 'infrastructure':
                region.style.backgroundColor = '#eab308';
                break;
            default:
                region.style.backgroundColor = '#84cc16';
        }
    });
}

// Initialize CTA buttons
function initializeCTAButtons() {
    const exploreButton = document.getElementById('explore-municipalities');
    
    exploreButton.addEventListener('click', function() {
        // Simulate navigation to detailed municipality analysis
        showFilterFeedback('Carregando análise detalhada dos municípios...');
        
        setTimeout(() => {
            alert('Em um sistema real, isso abriria uma página detalhada com análise de municípios prioritários baseada nos padrões eleitorais identificados.');
        }, 1000);
    });
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .comparison-card {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .comparison-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 10px 10px -5px rgb(0 0 0 / 0.04);
    }
    
    .region {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .region:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    }
    
    .btn {
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .btn:active {
        transform: scale(0.95);
    }
`;

document.head.appendChild(style);

// Utility functions for responsive behavior
function handleResize() {
    if (timelineChart) {
        timelineChart.resize();
    }
}

// Add resize listener
window.addEventListener('resize', handleResize);

// Add loading states
function showLoadingState(element) {
    element.style.opacity = '0.6';
    element.style.pointerEvents = 'none';
}

function hideLoadingState(element) {
    element.style.opacity = '1';
    element.style.pointerEvents = 'auto';
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('Dashboard error:', e.error);
    showFilterFeedback('Erro inesperado. Tente recarregar a página.');
});

// Performance optimization - lazy load heavy components
function lazyLoadComponents() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                
                if (element.classList.contains('map-section')) {
                    // Initialize map interactions when visible
                    initializeMapInteractions();
                }
                
                observer.unobserve(element);
            }
        });
    });
    
    document.querySelectorAll('.map-section').forEach(section => {
        observer.observe(section);
    });
}

// Initialize lazy loading
document.addEventListener('DOMContentLoaded', lazyLoadComponents);
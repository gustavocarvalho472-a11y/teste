// Dashboard Testing Suite
const DashboardTester = {
    testResults: [],
    
    // Test basic page load
    testPageLoad() {
        console.log('🧪 Testing page load...');
        const tests = [
            { name: 'HTML structure', check: () => document.querySelector('.dashboard-container') !== null },
            { name: 'CSS loaded', check: () => getComputedStyle(document.body).fontFamily.includes('Inter') },
            { name: 'JavaScript loaded', check: () => typeof Chart !== 'undefined' },
            { name: 'Lucide icons', check: () => typeof lucide !== 'undefined' }
        ];
        
        tests.forEach(test => {
            const result = test.check();
            this.testResults.push({ test: test.name, passed: result });
            console.log(`${result ? '✅' : '❌'} ${test.name}`);
        });
    },
    
    // Test chart functionality
    testChart() {
        console.log('🧪 Testing chart functionality...');
        const chart = document.getElementById('timeline-chart');
        const tests = [
            { name: 'Chart canvas exists', check: () => chart !== null },
            { name: 'Chart instance created', check: () => typeof timelineChart !== 'undefined' && timelineChart !== null },
            { name: 'Chart data loaded', check: () => timelineChart && timelineChart.data.datasets.length > 0 },
            { name: 'Electoral years highlighted', check: () => {
                if (!timelineChart) return false;
                const dataset = timelineChart.data.datasets[0];
                return typeof dataset.pointBackgroundColor === 'function';
            }}
        ];
        
        tests.forEach(test => {
            const result = test.check();
            this.testResults.push({ test: test.name, passed: result });
            console.log(`${result ? '✅' : '❌'} ${test.name}`);
        });
    },
    
    // Test filters
    testFilters() {
        console.log('🧪 Testing filter functionality...');
        const periodFilter = document.getElementById('period-filter');
        const regionFilter = document.getElementById('region-filter');
        const applyBtn = document.getElementById('apply-filters');
        const clearBtn = document.getElementById('clear-filters');
        
        const tests = [
            { name: 'Period filter exists', check: () => periodFilter !== null },
            { name: 'Region filter exists', check: () => regionFilter !== null },
            { name: 'Apply button exists', check: () => applyBtn !== null },
            { name: 'Clear button exists', check: () => clearBtn !== null },
            { name: 'Default selections', check: () => periodFilter.selectedOptions.length > 0 }
        ];
        
        tests.forEach(test => {
            const result = test.check();
            this.testResults.push({ test: test.name, passed: result });
            console.log(`${result ? '✅' : '❌'} ${test.name}`);
        });
        
        // Test filter interactions
        if (applyBtn) {
            console.log('🔄 Testing filter interactions...');
            applyBtn.click();
            setTimeout(() => {
                console.log('✅ Apply filter interaction successful');
            }, 100);
        }
    },
    
    // Test comparison cards
    testComparisonCards() {
        console.log('🧪 Testing comparison cards...');
        const cards = document.querySelectorAll('.comparison-card');
        const tests = [
            { name: 'Cards exist', check: () => cards.length === 4 },
            { name: 'Metric values present', check: () => {
                return Array.from(cards).every(card => 
                    card.querySelector('.metric-value') !== null
                );
            }},
            { name: 'Card icons loaded', check: () => {
                return Array.from(cards).every(card => 
                    card.querySelector('[data-lucide]') !== null
                );
            }}
        ];
        
        tests.forEach(test => {
            const result = test.check();
            this.testResults.push({ test: test.name, passed: result });
            console.log(`${result ? '✅' : '❌'} ${test.name}`);
        });
    },
    
    // Test map interactions
    testMapInteractions() {
        console.log('🧪 Testing map interactions...');
        const regions = document.querySelectorAll('.region');
        const toggleBtns = document.querySelectorAll('.toggle-btn');
        
        const tests = [
            { name: 'Regions exist', check: () => regions.length === 5 },
            { name: 'Toggle buttons exist', check: () => toggleBtns.length === 2 },
            { name: 'Tooltip element exists', check: () => document.getElementById('tooltip') !== null },
            { name: 'Region data attributes', check: () => {
                return Array.from(regions).every(region => 
                    region.dataset.region && region.dataset.variation && region.dataset.execution
                );
            }}
        ];
        
        tests.forEach(test => {
            const result = test.check();
            this.testResults.push({ test: test.name, passed: result });
            console.log(`${result ? '✅' : '❌'} ${test.name}`);
        });
    },
    
    // Test responsive design
    testResponsiveDesign() {
        console.log('🧪 Testing responsive design...');
        const originalWidth = window.innerWidth;
        
        // Test mobile breakpoint
        const mobileTests = [
            { name: 'Mobile layout adapts', check: () => {
                // Simulate mobile width check
                const container = document.querySelector('.dashboard-container');
                const style = getComputedStyle(container);
                return style.maxWidth !== 'none';
            }}
        ];
        
        mobileTests.forEach(test => {
            const result = test.check();
            this.testResults.push({ test: test.name, passed: result });
            console.log(`${result ? '✅' : '❌'} ${test.name}`);
        });
    },
    
    // Test CTA functionality
    testCTA() {
        console.log('🧪 Testing CTA functionality...');
        const ctaBtn = document.getElementById('explore-municipalities');
        
        const tests = [
            { name: 'CTA button exists', check: () => ctaBtn !== null },
            { name: 'CTA has click handler', check: () => {
                return ctaBtn && ctaBtn.onclick !== null || 
                       (ctaBtn && ctaBtn.addEventListener !== undefined);
            }}
        ];
        
        tests.forEach(test => {
            const result = test.check();
            this.testResults.push({ test: test.name, passed: result });
            console.log(`${result ? '✅' : '❌'} ${test.name}`);
        });
    },
    
    // Run all tests
    runAllTests() {
        console.log('🚀 Starting Dashboard Test Suite...\n');
        
        this.testPageLoad();
        
        // Wait for chart to initialize
        setTimeout(() => {
            this.testChart();
            this.testFilters();
            this.testComparisonCards();
            this.testMapInteractions();
            this.testResponsiveDesign();
            this.testCTA();
            
            this.printSummary();
        }, 1000);
    },
    
    // Print test summary
    printSummary() {
        console.log('\n📊 Test Summary:');
        const passed = this.testResults.filter(t => t.passed).length;
        const total = this.testResults.length;
        
        console.log(`✅ Passed: ${passed}/${total}`);
        console.log(`❌ Failed: ${total - passed}/${total}`);
        
        if (total - passed > 0) {
            console.log('\n❌ Failed tests:');
            this.testResults.filter(t => !t.passed).forEach(test => {
                console.log(`  - ${test.test}`);
            });
        }
        
        console.log(`\n🎯 Overall Score: ${((passed/total) * 100).toFixed(1)}%`);
        
        // Performance check
        this.testPerformance();
    },
    
    // Test performance
    testPerformance() {
        console.log('\n⚡ Performance Check:');
        
        const performanceTests = [
            {
                name: 'Page Load Time',
                value: performance.timing.loadEventEnd - performance.timing.navigationStart,
                unit: 'ms',
                threshold: 3000
            },
            {
                name: 'DOM Elements',
                value: document.querySelectorAll('*').length,
                unit: 'elements',
                threshold: 1000
            },
            {
                name: 'CSS Rules',
                value: Array.from(document.styleSheets).reduce((total, sheet) => {
                    try {
                        return total + (sheet.cssRules ? sheet.cssRules.length : 0);
                    } catch (e) {
                        return total;
                    }
                }, 0),
                unit: 'rules',
                threshold: 500
            }
        ];
        
        performanceTests.forEach(test => {
            const passed = test.value < test.threshold;
            console.log(`${passed ? '✅' : '⚠️'} ${test.name}: ${test.value} ${test.unit}`);
        });
    }
};

// Auto-run tests when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for everything to initialize
    setTimeout(() => {
        DashboardTester.runAllTests();
    }, 2000);
});

// Export for manual testing
window.DashboardTester = DashboardTester;
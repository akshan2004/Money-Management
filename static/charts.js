// charts.js - Chart initialization and rendering
// This file contains all JavaScript logic for the dashboard charts

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get data from hidden div data attributes
    var chartDataElement = document.getElementById('chartData');
    
    if (!chartDataElement) {
        console.error('Chart data element not found');
        return;
    }
    
    // Parse data from HTML attributes
    var categoryData = JSON.parse(chartDataElement.getAttribute('data-category'));
    var totalIncome = parseFloat(chartDataElement.getAttribute('data-income'));
    var totalExpense = parseFloat(chartDataElement.getAttribute('data-expense'));
    
    // Initialize both charts
    initializeCategoryChart(categoryData);
    initializeIncomeExpenseChart(totalIncome, totalExpense);
});

// Expense by Category Pie Chart
function initializeCategoryChart(categoryData) {
    var categoryChartElement = document.getElementById('categoryChart');
    
    if (!categoryChartElement) {
        console.error('Category chart canvas not found');
        return;
    }
    
    if (categoryData && categoryData.length > 0) {
        var categoryLabels = categoryData.map(function(item) {
            return item.category;
        });
        
        var categoryAmounts = categoryData.map(function(item) {
            return item.total;
        });
        
        var ctx = categoryChartElement.getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: categoryLabels,
                datasets: [{
                    data: categoryAmounts,
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF',
                        '#FF9F40'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ₹' + context.parsed;
                            }
                        }
                    }
                }
            }
        });
    } else {
        categoryChartElement.parentElement.innerHTML = 
            '<p class="text-muted text-center">No expense data available</p>';
    }
}

// Income vs Expense Bar Chart
function initializeIncomeExpenseChart(totalIncome, totalExpense) {
    var incomeExpenseChartElement = document.getElementById('incomeExpenseChart');
    
    if (!incomeExpenseChartElement) {
        console.error('Income/Expense chart canvas not found');
        return;
    }
    
    var ctx = incomeExpenseChartElement.getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Income', 'Expense'],
            datasets: [{
                label: 'Amount (₹)',
                data: [totalIncome, totalExpense],
                backgroundColor: [
                    '#28a745',
                    '#dc3545'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Amount: ₹' + context.parsed.y;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value;
                        }
                    }
                }
            }
        }
    });
}
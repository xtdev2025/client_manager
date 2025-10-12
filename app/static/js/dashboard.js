// Dashboard Enterprise JavaScript - GitHub Style

// Chart.js default configuration
Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#57606a';

// Global chart instances
let adminCharts = {};

// Admin Dashboard Functions
function loadAdminCharts() {
    console.log('Loading admin charts...');
    
    fetch('/dashboard/api/admin-stats')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Charts data received:', data);
            removeLoadingStates();
            createPlanDistributionChart(data.plan_distribution);
            createStatusDistributionChart(data.status_distribution);
        })
        .catch(error => {
            console.error('Error loading admin charts:', error);
            showChartError(['planChart', 'statusChart']);
        });
    
    // Load admin clicks chart
    loadAdminClicksChart();
}

function loadAdminClicksChart() {
    const ctx = document.getElementById('adminClicksChart');
    if (!ctx) {
        console.log('adminClicksChart canvas not found');
        return;
    }
    
    console.log('Loading admin clicks chart...');
    
    fetch('/dashboard/api/admin-clicks')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load admin clicks data');
            }
            return response.json();
        })
        .then(data => {
            console.log('Admin clicks data received:', data);
            
            if (adminCharts.adminClicksChart) {
                adminCharts.adminClicksChart.destroy();
            }
            
            adminCharts.adminClicksChart = new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: '#24292f',
                            padding: 12,
                            borderColor: '#d0d7de',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1,
                                color: '#57606a'
                            },
                            grid: {
                                color: '#d0d7de'
                            }
                        },
                        x: {
                            ticks: {
                                maxRotation: 45,
                                minRotation: 0,
                                color: '#57606a'
                            },
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading admin clicks chart:', error);
            showChartError(['adminClicksChart']);
        });
}

function removeLoadingStates() {
    ['planChart', 'statusChart'].forEach(id => {
        const container = document.getElementById(id)?.parentElement;
        if (container) {
            container.classList.remove('chart-loading');
        }
    });
}

function createPlanDistributionChart(data) {
    const ctx = document.getElementById('planChart');
    if (!ctx) {
        console.error('planChart canvas not found');
        return;
    }
    
    if (adminCharts.planChart) {
        adminCharts.planChart.destroy();
    }
    
    console.log('Creating plan distribution chart');
    
    adminCharts.planChart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        color: '#24292f',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#24292f',
                    padding: 12,
                    borderColor: '#d0d7de',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0;
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function createStatusDistributionChart(data) {
    const ctx = document.getElementById('statusChart');
    if (!ctx) {
        console.error('statusChart canvas not found');
        return;
    }
    
    if (adminCharts.statusChart) {
        adminCharts.statusChart.destroy();
    }
    
    console.log('Creating status distribution chart');
    
    adminCharts.statusChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#24292f',
                    padding: 12,
                    borderColor: '#d0d7de',
                    borderWidth: 1,
                    callbacks: {
                        title: function(context) {
                            return `Status: ${context[0].label}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        color: '#57606a'
                    },
                    grid: {
                        color: '#d0d7de'
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 0,
                        color: '#57606a'
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Error handling
function showChartError(chartIds) {
    chartIds.forEach(id => {
        const container = document.getElementById(id)?.parentElement;
        if (container) {
            container.classList.remove('chart-loading');
            container.innerHTML = '<div class="text-center text-danger py-5"><i class="fas fa-exclamation-triangle"></i> Erro ao carregar gráfico</div>';
        }
    });
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, checking for charts...');
    
    // Check if we're on admin dashboard
    const planChart = document.getElementById('planChart');
    const statusChart = document.getElementById('statusChart');
    
    // Check if we're on client dashboard
    const clicksChart = document.getElementById('clicksChart');
    const domainChart = document.getElementById('domainChart');
    
    if (planChart && statusChart) {
        console.log('Admin dashboard detected, loading charts...');
        loadAdminCharts();
    } else if (clicksChart || domainChart) {
        console.log('Client dashboard detected, loading charts...');
        loadClientCharts();
    } else {
        console.log('No charts detected on this page');
    }
});

// Client Dashboard Functions
let clientCharts = {};
let currentClicksPeriod = 30;

function loadClientCharts() {
    console.log('Loading client charts...');
    loadClicksChart(currentClicksPeriod);
    loadDomainChart();
}

function loadClicksChart(days = 30) {
    const ctx = document.getElementById('clicksChart');
    if (!ctx) {
        console.error('clicksChart canvas not found');
        return;
    }
    
    console.log(`Loading clicks chart for ${days} days...`);
    
    fetch(`/dashboard/api/clicks-chart?days=${days}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load clicks data');
            }
            return response.json();
        })
        .then(data => {
            console.log('Clicks data received:', data);
            
            if (clientCharts.clicksChart) {
                clientCharts.clicksChart.destroy();
            }
            
            clientCharts.clicksChart = new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: '#24292f',
                            padding: 12,
                            borderColor: '#d0d7de',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1,
                                color: '#57606a'
                            },
                            grid: {
                                color: '#d0d7de'
                            }
                        },
                        x: {
                            ticks: {
                                maxRotation: 45,
                                minRotation: 0,
                                color: '#57606a'
                            },
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading clicks chart:', error);
            showChartError(['clicksChart']);
        });
}

function loadDomainChart() {
    const ctx = document.getElementById('domainChart');
    if (!ctx) {
        console.error('domainChart canvas not found');
        return;
    }
    
    console.log('Loading domain chart...');
    
    fetch('/dashboard/api/domain-stats')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load domain stats');
            }
            return response.json();
        })
        .then(data => {
            console.log('Domain stats received:', data);
            
            if (clientCharts.domainChart) {
                clientCharts.domainChart.destroy();
            }
            
            clientCharts.domainChart = new Chart(ctx, {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: '#24292f',
                            padding: 12,
                            borderColor: '#d0d7de',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1,
                                color: '#57606a'
                            },
                            grid: {
                                color: '#d0d7de'
                            }
                        },
                        y: {
                            ticks: {
                                color: '#57606a'
                            },
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading domain chart:', error);
            showChartError(['domainChart']);
        });
}

function changeClicksPeriod(days, button) {
    currentClicksPeriod = days;
    
    // Update button states
    const buttons = button.parentElement.querySelectorAll('button');
    buttons.forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-primary');
    });
    button.classList.remove('btn-outline-primary');
    button.classList.add('btn-primary');
    
    // Reload chart
    loadClicksChart(days);
}

// Export for global access
window.DashboardJS = {
    loadAdminCharts,
    loadClientCharts,
    changeClicksPeriod
};

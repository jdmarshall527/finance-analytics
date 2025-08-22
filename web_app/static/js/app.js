// Portfolio Optimizer JavaScript Functions

// Tab navigation
function showTab(tabName) {
    // Remove active class from all tab buttons and content
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(tabName + '-tab').classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

// Input type toggle
function toggleInputType() {
    const inputType = document.getElementById('inputType').value;
    const weightsGroup = document.getElementById('weightsGroup');
    const dollarsGroup = document.getElementById('dollarsGroup');
    
    if (inputType === 'weights') {
        weightsGroup.style.display = 'block';
        dollarsGroup.style.display = 'none';
    } else {
        weightsGroup.style.display = 'none';
        dollarsGroup.style.display = 'block';
    }
}

// API health check
async function checkApiHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        const statusDiv = document.getElementById('apiStatus');
        if (response.ok) {
            statusDiv.innerHTML = '<span class="status-indicator status-healthy"></span><span>API is healthy and ready</span>';
        } else {
            throw new Error('API not healthy');
        }
    } catch (error) {
        const statusDiv = document.getElementById('apiStatus');
        statusDiv.innerHTML = '<span class="status-indicator status-error"></span><span>API is not available</span>';
    }
}

// Portfolio analysis
async function analyzePortfolio() {
    const tickers = document.getElementById('tickers').value.split(',').map(t => t.trim());
    const inputType = document.getElementById('inputType').value;
    const timePeriod = parseInt(document.getElementById('timePeriod').value);
    
    let weights;
    if (inputType === 'weights') {
        weights = document.getElementById('weights').value.split(',').map(w => parseFloat(w.trim()));
    } else {
        const dollars = document.getElementById('dollars').value.split(',').map(d => parseFloat(d.trim()));
        const total = dollars.reduce((sum, amount) => sum + amount, 0);
        weights = dollars.map(amount => amount / total);
    }
    
    if (tickers.length !== weights.length) {
        showError('analysisResults', 'Number of tickers must match number of inputs');
        return;
    }
    
    // Parse minimum exposure
    const minExposureInput = document.getElementById('minExposure').value.trim();
    let minExposure = null;
    if (minExposureInput) {
        const exposureValues = minExposureInput.split(',').map(v => parseFloat(v.trim()) / 100); // Convert % to decimal
        if (exposureValues.length === 1) {
            // Single value for all securities
            minExposure = exposureValues[0];
        } else if (exposureValues.length === tickers.length) {
            // Individual values for each security
            minExposure = exposureValues;
        } else {
            showError('analysisResults', 'Minimum exposure must be one number or match the number of tickers');
            return;
        }
    }
    
    // Show progress bar
    showProgress();
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tickers, weights, time_period: timePeriod, min_exposure: minExposure })
        });
        
        const data = await response.json();
        
        // Hide progress bar
        hideProgress();
        
        if (response.ok) {
            showAnalysisResults(data);
        } else {
            showError('analysisResults', data.error || 'Analysis failed');
        }
    } catch (error) {
        // Hide progress bar
        hideProgress();
        console.error('Error:', error);
        showError('analysisResults', 'Failed to connect to API: ' + error.message);
    }
}

// Portfolio optimization
async function optimizePortfolio() {
    const tickers = document.getElementById('tickers').value.split(',').map(t => t.trim());
    const constraint = document.getElementById('constraint').value;
    const inputType = document.getElementById('inputType').value;
    const timePeriod = parseInt(document.getElementById('timePeriod').value);
    
    let currentWeights;
    if (inputType === 'weights') {
        currentWeights = document.getElementById('weights').value.split(',').map(w => parseFloat(w.trim()));
    } else {
        const dollars = document.getElementById('dollars').value.split(',').map(d => parseFloat(d.trim()));
        const total = dollars.reduce((sum, amount) => sum + amount, 0);
        currentWeights = dollars.map(amount => amount / total);
    }
    
    if (tickers.length !== currentWeights.length) {
        showError('optimizationResults', 'Number of tickers must match number of inputs');
        return;
    }
    
    // Parse minimum exposure
    const minExposureInput = document.getElementById('minExposure').value.trim();
    let minExposure = null;
    if (minExposureInput) {
        const exposureValues = minExposureInput.split(',').map(v => parseFloat(v.trim()) / 100); // Convert % to decimal
        if (exposureValues.length === 1) {
            // Single value for all securities
            minExposure = exposureValues[0];
        } else if (exposureValues.length === tickers.length) {
            // Individual values for each security
            minExposure = exposureValues;
        } else {
            showError('optimizationResults', 'Minimum exposure must be one number or match the number of tickers');
            return;
        }
    }
    
    // Show progress bar
    showProgress();
    
    try {
        const response = await fetch('/api/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tickers, constraint, current_weights: currentWeights, time_period: timePeriod, min_exposure: minExposure })
        });
        
        const data = await response.json();
        
        // Hide progress bar
        hideProgress();
        
        if (response.ok) {
            showOptimizationResults(data);
        } else {
            showError('optimizationResults', data.error || 'Optimization failed');
        }
    } catch (error) {
        // Hide progress bar
        hideProgress();
        console.error('Error:', error);
        showError('optimizationResults', 'Failed to connect to API: ' + error.message);
    }
}

// Get sectors
async function getSectors() {
    try {
        const response = await fetch('/api/sectors');
        const data = await response.json();
        
        if (response.ok) {
            showSectorResults(data);
        } else {
            showError('sectorResults', data.error || 'Failed to get sectors');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('sectorResults', 'Failed to connect to API: ' + error.message);
    }
}

// Show analysis results
function showAnalysisResults(data) {
    const resultsDiv = document.getElementById('analysisResults');
    const analysisSection = document.getElementById('analysisSection');
    
    // Extract current portfolio stats
    const currentStats = data.current_portfolio.stats;
    const analysis = data.analysis;
    
    resultsDiv.innerHTML = `
        <div class="results success">
            <h3>Portfolio Analysis Results</h3>
            <p><strong>Analysis Period:</strong> ${analysis.time_period || '2 years'} of historical data</p>
            <p><strong>Inflation Rate:</strong> ${(currentStats.inflation_rate * 100).toFixed(1)}% (used for real return calculations)</p>
            <h4>Current Portfolio Performance:</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0;">
                <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #3498db;">
                    <h5 style="margin: 0 0 10px 0; color: #2c3e50;">Nominal Returns</h5>
                    <p><strong>Expected Return:</strong> ${(currentStats.return * 100).toFixed(2)}%</p>
                    <p><strong>Volatility:</strong> ${(currentStats.volatility * 100).toFixed(2)}%</p>
                    <p><strong>Sharpe Ratio:</strong> ${currentStats.sharpe_ratio.toFixed(3)}</p>
                </div>
                <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #e74c3c;">
                    <h5 style="margin: 0 0 10px 0; color: #2c3e50;">Inflation-Adjusted (Real) Returns</h5>
                    <p><strong>Real Return:</strong> ${(currentStats.real_return * 100).toFixed(2)}%</p>
                    <p><strong>Volatility:</strong> ${(currentStats.volatility * 100).toFixed(2)}%</p>
                    <p><strong>Real Sharpe Ratio:</strong> ${currentStats.real_sharpe_ratio.toFixed(3)}</p>
                </div>
            </div>
            <p><strong>Risk Level:</strong> ${analysis.risk_level}</p>
            
            <h4>Optimal Portfolio (Max Sharpe Ratio):</h4>
            <p><strong>Expected Return:</strong> ${(data.optimal_portfolio.stats.return * 100).toFixed(2)}%</p>
            <p><strong>Volatility:</strong> ${(data.optimal_portfolio.stats.volatility * 100).toFixed(2)}%</p>
            <p><strong>Sharpe Ratio:</strong> ${data.optimal_portfolio.stats.sharpe_ratio.toFixed(3)}</p>
            
            <h4>Optimal Allocation:</h4>
            <ul>
                ${Object.entries(data.optimal_portfolio.allocation).map(([ticker, weight]) => 
                    `<li><strong>${ticker}:</strong> ${(weight * 100).toFixed(2)}%</li>`
                ).join('')}
            </ul>
            
            ${data.recommendations.length > 0 ? `
                <h4>Diversification Recommendations:</h4>
                <div style="display: grid; gap: 15px; margin-top: 15px;">
                    ${data.recommendations.slice(0, 5).map(rec => {
                        const returnChange = ((rec.new_return - currentStats.return) * 100).toFixed(2);
                        const volatilityChange = ((rec.new_volatility - currentStats.volatility) * 100).toFixed(2);
                        const returnChangeColor = returnChange >= 0 ? '#27ae60' : '#e74c3c';
                        const volatilityChangeColor = volatilityChange <= 0 ? '#27ae60' : '#e74c3c';
                        
                        return `
                            <div style="border: 1px solid #e1e8ed; border-radius: 8px; padding: 15px; background: #f8f9fa;">
                                <h5 style="margin: 0 0 10px 0; color: #2c3e50;">
                                    ${rec.ticker} - ${rec.name}
                                </h5>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px;">
                                    <div>
                                        <strong>Nominal Return:</strong> ${(rec.new_return * 100).toFixed(2)}%
                                        <span style="color: ${returnChangeColor};">(${returnChange >= 0 ? '+' : ''}${returnChange}%)</span>
                                    </div>
                                    <div>
                                        <strong>Real Return:</strong> ${((rec.new_return - currentStats.inflation_rate) * 100).toFixed(2)}%
                                    </div>
                                    <div>
                                        <strong>Volatility:</strong> ${(rec.new_volatility * 100).toFixed(2)}%
                                        <span style="color: ${volatilityChangeColor};">(${volatilityChange >= 0 ? '+' : ''}${volatilityChange}%)</span>
                                    </div>
                                    <div>
                                        <strong>Sharpe Ratio:</strong> ${rec.new_return / rec.new_volatility > 0 ? (rec.new_return / rec.new_volatility).toFixed(3) : 'N/A'}
                                        <span style="color: #27ae60;">(+${rec.sharpe_improvement.toFixed(3)})</span>
                                    </div>
                                    <div>
                                        <strong>Correlation:</strong> ${rec.correlation.toFixed(3)}
                                    </div>
                                    <div>
                                        <strong>Inflation Rate:</strong> ${(currentStats.inflation_rate * 100).toFixed(1)}%
                                    </div>
                                </div>
                                <div style="margin-top: 10px; font-size: 12px; color: #7f8c8d;">
                                    <strong>Impact:</strong> Adding 10% ${rec.ticker} to your portfolio
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            ` : ''}
        </div>
        
        <div class="results success">
            <h3>Efficient Frontier Analysis</h3>
            <div id="efficientFrontierPlot"></div>
        </div>
    `;
    
    // Show the analysis section
    analysisSection.style.display = 'block';
    
    // Ensure the section is expanded when showing results
    const content = analysisSection.querySelector('.collapsible-content');
    const header = analysisSection.querySelector('.collapsible-header');
    const icon = header.querySelector('.toggle-icon');
    
    content.classList.add('show');
    header.classList.add('active');
    icon.classList.add('rotated');
    
    // Create efficient frontier plot if data is available
    if (data.efficient_frontier_plot) {
        createEfficientFrontierPlot(data.efficient_frontier_plot, currentStats);
    }
}

// Show optimization results
function showOptimizationResults(data) {
    const resultsDiv = document.getElementById('optimizationResults');
    const optimizationSection = document.getElementById('optimizationSection');
    const allocation = data.allocation;
    const stats = data.optimal_stats;
    const alternativeAllocation = data.alternative_allocation;
    const alternativeStats = data.alternative_stats;
    
    let allocationHtml = '<h4>Optimal Allocation (May include 0% allocations):</h4><ul>';
    for (const [ticker, weight] of Object.entries(allocation)) {
        allocationHtml += `<li><strong>${ticker}:</strong> ${(weight * 100).toFixed(2)}%</li>`;
    }
    allocationHtml += '</ul>';
    
    let alternativeAllocationHtml = '<h4>Alternative Allocation (Minimum 1% per asset):</h4><ul>';
    for (const [ticker, weight] of Object.entries(alternativeAllocation)) {
        alternativeAllocationHtml += `<li><strong>${ticker}:</strong> ${(weight * 100).toFixed(2)}%</li>`;
    }
    alternativeAllocationHtml += '</ul>';
    
    let currentStatsHtml = '';
    if (data.current_stats) {
        currentStatsHtml = `
            <h4>Current Portfolio Performance:</h4>
            <p><strong>Expected Return:</strong> ${(data.current_stats.return * 100).toFixed(2)}%</p>
            <p><strong>Volatility:</strong> ${(data.current_stats.volatility * 100).toFixed(2)}%</p>
            <p><strong>Sharpe Ratio:</strong> ${data.current_stats.sharpe_ratio.toFixed(3)}</p>
        `;
    }
    
    // Calculate performance difference
    const returnDiff = ((alternativeStats.return - stats.return) * 100).toFixed(2);
    const volatilityDiff = ((alternativeStats.volatility - stats.volatility) * 100).toFixed(2);
    const sharpeDiff = (alternativeStats.sharpe_ratio - stats.sharpe_ratio).toFixed(3);
    
    resultsDiv.innerHTML = `
        <div class="results success">
            <h3>Portfolio Optimization Results</h3>
            <p><strong>Strategy:</strong> ${data.constraint_used.replace('_', ' ').toUpperCase()}</p>
            <p><strong>Analysis Period:</strong> ${data.time_period || 2} year${data.time_period > 1 ? 's' : ''} of historical data</p>
            <p><strong>Minimum Exposure:</strong> ${formatMinExposure(data.min_exposure_used)}</p>
            ${currentStatsHtml}
            
            <div style="display: flex; gap: 20px; margin: 20px 0;">
                <div style="flex: 1; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #3498db;">
                    <h4>Optimal Portfolio Performance:</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0;">
                        <div>
                            <h5 style="margin: 0 0 5px 0; font-size: 14px; color: #2c3e50;">Nominal</h5>
                            <p style="margin: 5px 0; font-size: 13px;"><strong>Return:</strong> ${(stats.return * 100).toFixed(2)}%</p>
                            <p style="margin: 5px 0; font-size: 13px;"><strong>Sharpe:</strong> ${stats.sharpe_ratio.toFixed(3)}</p>
                        </div>
                        <div>
                            <h5 style="margin: 0 0 5px 0; font-size: 14px; color: #2c3e50;">Real</h5>
                            <p style="margin: 5px 0; font-size: 13px;"><strong>Return:</strong> ${(stats.real_return * 100).toFixed(2)}%</p>
                            <p style="margin: 5px 0; font-size: 13px;"><strong>Sharpe:</strong> ${stats.real_sharpe_ratio.toFixed(3)}</p>
                        </div>
                    </div>
                    <p style="margin: 10px 0 0 0;"><strong>Volatility:</strong> ${(stats.volatility * 100).toFixed(2)}%</p>
                    ${allocationHtml}
                </div>
                
                <div style="flex: 1; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #e74c3c;">
                    <h4>Alternative Portfolio Performance:</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0;">
                        <div>
                            <h5 style="margin: 0 0 5px 0; font-size: 14px; color: #2c3e50;">Nominal</h5>
                            <p style="margin: 5px 0; font-size: 13px;"><strong>Return:</strong> ${(alternativeStats.return * 100).toFixed(2)}% <span style="color: ${returnDiff >= 0 ? '#27ae60' : '#e74c3c'}">(${returnDiff >= 0 ? '+' : ''}${returnDiff}%)</span></p>
                            <p style="margin: 5px 0; font-size: 13px;"><strong>Sharpe:</strong> ${alternativeStats.sharpe_ratio.toFixed(3)} <span style="color: ${sharpeDiff >= 0 ? '#27ae60' : '#e74c3c'}">(${sharpeDiff >= 0 ? '+' : ''}${sharpeDiff})</span></p>
                        </div>
                        <div>
                            <h5 style="margin: 0 0 5px 0; font-size: 14px; color: #2c3e50;">Real</h5>
                            <p style="margin: 5px 0; font-size: 13px;"><strong>Return:</strong> ${(alternativeStats.real_return * 100).toFixed(2)}%</p>
                            <p style="margin: 5px 0; font-size: 13px;"><strong>Sharpe:</strong> ${alternativeStats.real_sharpe_ratio.toFixed(3)}</p>
                        </div>
                    </div>
                    <p style="margin: 10px 0 0 0;"><strong>Volatility:</strong> ${(alternativeStats.volatility * 100).toFixed(2)}% <span style="color: ${volatilityDiff <= 0 ? '#27ae60' : '#e74c3c'}">(${volatilityDiff >= 0 ? '+' : ''}${volatilityDiff}%)</span></p>
                    ${alternativeAllocationHtml}
                </div>
            </div>
            
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 20px 0;">
                <h4>💡 Allocation Comparison</h4>
                <p><strong>Optimal Allocation:</strong> Maximizes ${data.constraint_used.replace('_', ' ')} but may exclude some assets (0% allocation).</p>
                <p><strong>Alternative Allocation:</strong> Ensures at least 1% exposure to each asset while staying close to optimal performance.</p>
                <p><strong>Performance Impact:</strong> The alternative allocation shows the trade-off between diversification and optimal performance.</p>
            </div>
        </div>
        
        <div class="results success">
            <h3>Efficient Frontier Analysis</h3>
            <div id="optimizationFrontierPlot"></div>
        </div>
    `;
    
    // Ensure the section is expanded when showing results
    const content = optimizationSection.querySelector('.collapsible-content');
    const header = optimizationSection.querySelector('.collapsible-header');
    const icon = header.querySelector('.toggle-icon');
    
    content.classList.add('show');
    header.classList.add('active');
    icon.classList.add('rotated');
    
    // Create efficient frontier plot if data is available
    if (data.efficient_frontier_plot) {
        createOptimizationFrontierPlot(data.efficient_frontier_plot, data.current_stats, stats);
    }
}

// Show sector results
function showSectorResults(data) {
    const resultsDiv = document.getElementById('sectorResults');
    let sectorsHtml = '<h4>Available Sector ETFs:</h4><ul>';
    for (const [sector, etf] of Object.entries(data.sectors)) {
        sectorsHtml += `<li><strong>${sector}:</strong> ${etf}</li>`;
    }
    sectorsHtml += '</ul>';
    
    resultsDiv.innerHTML = `
        <div class="results success">
            ${sectorsHtml}
        </div>
    `;
}

// Show error
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="error">${message}</div>`;
    
    // Show the appropriate section when there's an error
    if (elementId === 'analysisResults') {
        document.getElementById('analysisSection').style.display = 'block';
    }
}

// Progress bar functions
function showProgress() {
    const progressContainer = document.getElementById('progressContainer');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    progressContainer.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = 'Initializing analysis...';
    
    // Simulate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        
        progressFill.style.width = progress + '%';
        
        if (progress < 30) {
            progressText.textContent = 'Fetching market data...';
        } else if (progress < 60) {
            progressText.textContent = 'Calculating portfolio statistics...';
        } else if (progress < 90) {
            progressText.textContent = 'Generating efficient frontier...';
        }
    }, 200);
    
    // Store interval ID for cleanup
    progressContainer.dataset.intervalId = progressInterval;
}

function hideProgress() {
    const progressContainer = document.getElementById('progressContainer');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    // Complete the progress bar
    progressFill.style.width = '100%';
    progressText.textContent = 'Analysis complete!';
    
    // Clear the interval
    if (progressContainer.dataset.intervalId) {
        clearInterval(parseInt(progressContainer.dataset.intervalId));
    }
    
    // Hide after a short delay
    setTimeout(() => {
        progressContainer.style.display = 'none';
    }, 1000);
}

// Collapsible section toggle
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const header = section.querySelector('.collapsible-header');
    const content = section.querySelector('.collapsible-content');
    const icon = header.querySelector('.toggle-icon');
    
    // Toggle the content
    content.classList.toggle('show');
    
    // Toggle the header active state
    header.classList.toggle('active');
    
    // Rotate the icon
    icon.classList.toggle('rotated');
}

// Format minimum exposure
function formatMinExposure(minExposure) {
    if (minExposure === null || minExposure === undefined) {
        return '1% (default)';
    } else if (typeof minExposure === 'number') {
        return `${(minExposure * 100).toFixed(1)}% for all securities`;
    } else if (Array.isArray(minExposure)) {
        return minExposure.map(exposure => `${(exposure * 100).toFixed(1)}%`).join(', ') + ' (individual)';
    } else {
        return '1% (default)';
    }
}

// Create efficient frontier plot for analysis
function createEfficientFrontierPlot(frontierData, currentStats) {
    const ef = frontierData.efficient_frontier;
    const cal = frontierData.capital_allocation_line;
    const tangency = frontierData.tangency_portfolio;
    
    // Prepare data for plotting
    const efVolatility = ef.map(p => p.volatility * 100);
    const efReturns = ef.map(p => p.return * 100);
    const calVolatility = cal.map(p => p.volatility * 100);
    const calReturns = cal.map(p => p.return * 100);
    
    const traces = [
        {
            x: efVolatility,
            y: efReturns,
            type: 'scatter',
            mode: 'lines',
            name: 'Efficient Frontier',
            line: { color: '#2E86AB', width: 3 },
            hovertemplate: 'Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
        },
        {
            x: calVolatility,
            y: calReturns,
            type: 'scatter',
            mode: 'lines',
            name: 'Capital Allocation Line',
            line: { color: '#A23B72', width: 2, dash: 'dash' },
            hovertemplate: 'Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
        },
        {
            x: [tangency.volatility * 100],
            y: [tangency.return * 100],
            type: 'scatter',
            mode: 'markers',
            name: 'Tangency Portfolio',
            marker: { 
                color: '#F18F01', 
                size: 12,
                symbol: 'star'
            },
            hovertemplate: 'Tangency Portfolio<br>Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
        },
        {
            x: [currentStats.volatility * 100],
            y: [currentStats.return * 100],
            type: 'scatter',
            mode: 'markers',
            name: 'Current Portfolio',
            marker: { 
                color: '#C73E1D', 
                size: 12,
                symbol: 'circle'
            },
            hovertemplate: 'Current Portfolio<br>Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
        }
    ];
    
    const layout = {
        title: 'Efficient Frontier with Capital Allocation Line',
        xaxis: {
            title: 'Portfolio Volatility (%)',
            gridcolor: '#E5E5E5'
        },
        yaxis: {
            title: 'Expected Annual Return (%)',
            gridcolor: '#E5E5E5'
        },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        font: { color: '#2C3E50' },
        legend: {
            x: 0.02,
            y: 0.98,
            bgcolor: 'rgba(255,255,255,0.8)',
            bordercolor: '#E5E5E5'
        },
        margin: { l: 60, r: 30, t: 60, b: 60 }
    };
    
    Plotly.newPlot('efficientFrontierPlot', traces, layout, {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
    });
}

// Create efficient frontier plot for optimization
function createOptimizationFrontierPlot(frontierData, currentStats, optimalStats) {
    const ef = frontierData.efficient_frontier;
    const cal = frontierData.capital_allocation_line;
    const tangency = frontierData.tangency_portfolio;
    
    // Prepare data for plotting
    const efVolatility = ef.map(p => p.volatility * 100);
    const efReturns = ef.map(p => p.return * 100);
    const calVolatility = cal.map(p => p.volatility * 100);
    const calReturns = cal.map(p => p.return * 100);
    
    const traces = [
        {
            x: efVolatility,
            y: efReturns,
            type: 'scatter',
            mode: 'lines',
            name: 'Efficient Frontier',
            line: { color: '#2E86AB', width: 3 },
            hovertemplate: 'Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
        },
        {
            x: calVolatility,
            y: calReturns,
            type: 'scatter',
            mode: 'lines',
            name: 'Capital Allocation Line',
            line: { color: '#A23B72', width: 2, dash: 'dash' },
            hovertemplate: 'Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
        },
        {
            x: [tangency.volatility * 100],
            y: [tangency.return * 100],
            type: 'scatter',
            mode: 'markers',
            name: 'Tangency Portfolio',
            marker: { 
                color: '#F18F01', 
                size: 12,
                symbol: 'star'
            },
            hovertemplate: 'Tangency Portfolio<br>Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
        },
        {
            x: [optimalStats.volatility * 100],
            y: [optimalStats.return * 100],
            type: 'scatter',
            mode: 'markers',
            name: 'Optimal Portfolio',
            marker: { 
                color: '#27AE60', 
                size: 12,
                symbol: 'diamond'
            },
            hovertemplate: 'Optimal Portfolio<br>Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
        }
    ];
    
    // Add current portfolio if available
    if (currentStats) {
        traces.push({
            x: [currentStats.volatility * 100],
            y: [currentStats.return * 100],
            type: 'scatter',
            mode: 'markers',
            name: 'Current Portfolio',
            marker: { 
                color: '#C73E1D', 
                size: 12,
                symbol: 'circle'
            },
            hovertemplate: 'Current Portfolio<br>Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<extra></extra>'
        });
    }
    
    const layout = {
        title: 'Efficient Frontier with Capital Allocation Line',
        xaxis: {
            title: 'Portfolio Volatility (%)',
            gridcolor: '#E5E5E5'
        },
        yaxis: {
            title: 'Expected Annual Return (%)',
            gridcolor: '#E5E5E5'
        },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        font: { color: '#2C3E50' },
        legend: {
            x: 0.02,
            y: 0.98,
            bgcolor: 'rgba(255,255,255,0.8)',
            bordercolor: '#E5E5E5'
        },
        margin: { l: 60, r: 30, t: 60, b: 60 }
    };
    
    Plotly.newPlot('optimizationFrontierPlot', traces, layout, {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
    });
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Check API health on page load
    checkApiHealth();
    
    // Set up input type toggle
    toggleInputType();
});

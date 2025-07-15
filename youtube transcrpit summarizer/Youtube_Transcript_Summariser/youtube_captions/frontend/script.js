document.addEventListener('DOMContentLoaded', function() {
    // Theme handling
    const themeToggle = document.getElementById('themeToggle');
    let isDarkTheme = localStorage.getItem('theme') === 'dark';
    
    function updateTheme() {
        document.body.dataset.theme = isDarkTheme ? 'dark' : 'light';
        localStorage.setItem('theme', isDarkTheme ? 'dark' : 'light');
    }
    
    // Initialize theme
    updateTheme();
    
    themeToggle.addEventListener('click', () => {
        isDarkTheme = !isDarkTheme;
        updateTheme();
    });

    // URL input handling
    const videoUrlInput = document.getElementById('videoUrl');
    const pasteBtn = document.getElementById('pasteUrl');
    const clearBtn = document.getElementById('clearBtn');
    const summarizeBtn = document.getElementById('summarizeBtn');
    const loader = document.getElementById('loader');
    
    pasteBtn.addEventListener('click', async () => {
        try {
            const text = await navigator.clipboard.readText();
            videoUrlInput.value = text;
        } catch (err) {
            console.error('Failed to read clipboard:', err);
            showToast('Failed to read clipboard');
        }
    });
    
    clearBtn.addEventListener('click', () => {
        videoUrlInput.value = '';
        document.getElementById('result').innerHTML = '';
    });

    // Process video
    summarizeBtn.addEventListener('click', async () => {
        const videoUrl = videoUrlInput.value.trim();
        if (!videoUrl) {
            showToast('Please enter a YouTube URL');
            return;
        }

        const summaryLength = document.querySelector('input[name="length"]:checked').value;
        const language = document.getElementById('language').value;
        // Show loader
        loader.classList.remove('hidden');
        summarizeBtn.disabled = true;
        
        try {
            const response = await fetch('/api/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: videoUrl,
                    length: summaryLength,
                    language: language
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to process video');
            }

            // Add to history
            addToHistory({
                title: data.title,
                url: videoUrl,
                timestamp: Date.now()
            });

            // Update result based on current tab
            updateResult(data);
            
        } catch (error) {
            console.error('Error:', error);
            showToast(error.message);
            document.getElementById('result').innerHTML = `<p class="error">${error.message}</p>`;
        } finally {
            loader.classList.add('hidden');
            summarizeBtn.disabled = false;
        }
    });

    // Tab handling
    const tabs = document.querySelectorAll('.tab-btn');
    let currentTab = 'summary';
    let currentData = null;
    let historyData = JSON.parse(localStorage.getItem('summarizeHistory') || '[]');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentTab = tab.dataset.tab;
            updateTabContent();
        });
    });

    function updateResult(data) {
        currentData = data;
        updateTabContent();
    }

    function updateTabContent() {
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = '';

        switch(currentTab) {
            case 'summary':
                if (currentData) {
                    resultDiv.innerHTML = `<div class="summary-content">${currentData.summary}</div>`;
                }
                break;
            case 'transcript':
                if (currentData) {
                    resultDiv.innerHTML = `<div class="transcript-content">${currentData.transcript}</div>`;
                }
                break;
            case 'history':
                displayHistory();
                break;
        }
    }

    function addToHistory(item) {
        historyData.unshift(item);
        // Keep only last 10 items
        historyData = historyData.slice(0, 10);
        localStorage.setItem('summarizeHistory', JSON.stringify(historyData));
    }

    function displayHistory() {
        const resultDiv = document.getElementById('result');
        if (historyData.length === 0) {
            resultDiv.innerHTML = '<p>No history available</p>';
            return;
        }

        const historyHtml = historyData.map(item => `
            <div class="history-item">
                <h3>${item.title}</h3>
                <p>Processed: ${new Date(item.timestamp).toLocaleString()}</p>
                <a href="${item.url}" target="_blank">View Video</a>
            </div>
        `).join('');

        resultDiv.innerHTML = historyHtml;
    }

    // Speak functionality
    const speakBtn = document.getElementById('speakBtn');
    const audioPlayer = document.getElementById('audioPlayer');
    speakBtn.addEventListener('click', async () => {
        if (!currentData || !currentData.summary) {
            showToast('No summary to speak!');
            return;
        }
        const language = document.getElementById('language').value;
        speakBtn.disabled = true;
        speakBtn.textContent = '🔊 Speaking...';
        try {
            const response = await fetch('/api/speak', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: currentData.summary,
                    language: language
                })
            });
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.error || 'Failed to generate speech');
            }
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            audioPlayer.src = url;
            // Move audio element right after speakBtn and show it
            speakBtn.parentNode.insertBefore(audioPlayer, speakBtn.nextSibling);
            audioPlayer.style.display = 'inline-block';
            audioPlayer.play();
        } catch (err) {
            showToast('Speech error: ' + err.message);
        } finally {
            speakBtn.disabled = false;
            speakBtn.textContent = '🔊 Speak Summary';
        }
    });

    // Copy and Save functionality
    const copyBtn = document.getElementById('copyBtn');
    const saveBtn = document.getElementById('saveBtn');
    const openVideoBtn = document.getElementById('openVideoBtn');

    copyBtn.addEventListener('click', async () => {
        const content = document.getElementById('result').textContent;
        const notification = document.getElementById('copyNotification');
        try {
            await navigator.clipboard.writeText(content);
            // Show notification overlay
            notification.classList.add('show');
            notification.style.display = 'block';
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    notification.style.display = 'none';
                }, 400);
            }, 2000);
        } catch (err) {
            showToast('Failed to copy content');
        }
    });

    saveBtn.addEventListener('click', () => {
        if (!currentData) return;
        
        const content = currentTab === 'summary' ? currentData.summary : currentData.transcript;
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${currentTab}_${new Date().toISOString().slice(0,10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    openVideoBtn.addEventListener('click', () => {
        const videoUrl = videoUrlInput.value;
        if (videoUrl) {
            window.open(videoUrl, '_blank');
        }
    });

    // Toast notification
    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }

    // View Toggle Functionality
    const viewToggle = document.getElementById('viewToggle');
    const container = document.querySelector('.container');
    
    function toggleView() {
        const isMobile = container.classList.contains('mobile-view');
        if (isMobile) {
            container.classList.remove('mobile-view');
            container.classList.add('desktop-view');
            viewToggle.querySelector('.view-label').textContent = 'Switch to Mobile View';
            localStorage.setItem('viewMode', 'desktop');
        } else {
            container.classList.remove('desktop-view');
            container.classList.add('mobile-view');
            viewToggle.querySelector('.view-label').textContent = 'Switch to Desktop View';
            localStorage.setItem('viewMode', 'mobile');
        }
    }

    viewToggle.addEventListener('click', toggleView);

    // Set initial view based on screen size and saved preference
    function setInitialView() {
        const savedViewMode = localStorage.getItem('viewMode');
        const isMobileScreen = window.innerWidth <= 768;
        
        if (savedViewMode) {
            if (savedViewMode === 'mobile') {
                container.classList.add('mobile-view');
                viewToggle.querySelector('.view-label').textContent = 'Switch to Desktop View';
            } else {
                container.classList.add('desktop-view');
                viewToggle.querySelector('.view-label').textContent = 'Switch to Mobile View';
            }
        } else {
            if (isMobileScreen) {
                container.classList.add('mobile-view');
                viewToggle.querySelector('.view-label').textContent = 'Switch to Desktop View';
                localStorage.setItem('viewMode', 'mobile');
            } else {
                container.classList.add('desktop-view');
                viewToggle.querySelector('.view-label').textContent = 'Switch to Mobile View';
                localStorage.setItem('viewMode', 'desktop');
            }
        }
    }

    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            const isMobileScreen = window.innerWidth <= 768;
            const currentView = container.classList.contains('mobile-view') ? 'mobile' : 'desktop';
            
            if (isMobileScreen && currentView === 'desktop') {
                toggleView();
            } else if (!isMobileScreen && currentView === 'mobile') {
                toggleView();
            }
        }, 250);
    });

    setInitialView();
});
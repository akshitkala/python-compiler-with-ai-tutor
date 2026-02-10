document.addEventListener('DOMContentLoaded', () => {
    const runBtn = document.getElementById('run-btn');
    const clearBtn = document.getElementById('clear-btn');
    const outputEl = document.getElementById('output-content');
    const aiEl = document.getElementById('ai-content');

    // Helper: Set Output
    function setOutput(text, isError = false) {
        outputEl.textContent = text;
        outputEl.className = isError ? 'error' : 'success';
        if (text === '') outputEl.classList.add('placeholder');
    }

    // Helper: Render AI UI
    function setAI(data) {
        if (!data) {
            aiEl.innerHTML = `<div class="placeholder">I'm ready to explain any errors you encounter!</div>`;
            return;
        }
        
        // Parse Markdown
        let htmlContent;
        if (typeof marked !== 'undefined' && marked.parse) {
            htmlContent = marked.parse(data.ai_explanation);
        } else {
            console.warn('Marked.js not loaded. Falling back to text.');
            htmlContent = data.ai_explanation.replace(/\n/g, '<br>');
        }

        // Post-process: Wrap sections in semantic containers
        if (typeof document !== 'undefined') {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = htmlContent;
            
            const newContainer = document.createElement('div');
            let currentSection = null;
            
            Array.from(tempDiv.childNodes).forEach(node => {
                if (node.nodeName === 'H3') {
                    const text = node.textContent || "";
                    let className = 'ai-section';
                    if (text.includes('What went wrong')) className += ' error';
                    else if (text.includes('Concept involved')) className += ' concept';
                    else if (text.includes('How to fix')) className += ' fix';
                    else if (text.includes('Corrected code')) className += ' success';
                    else if (text.includes('Quick tip')) className += ' tip';
                    
                    currentSection = document.createElement('div');
                    currentSection.className = className;
                    newContainer.appendChild(currentSection);
                    currentSection.appendChild(node.cloneNode(true));
                } else {
                    if (currentSection) {
                        currentSection.appendChild(node.cloneNode(true));
                    } else if (node.textContent.trim() !== "") {
                        // Intro text before first header
                        if (!newContainer.lastChild || !newContainer.lastChild.classList.contains('ai-section')) {
                             const intro = document.createElement('div');
                             intro.className = 'ai-intro';
                             newContainer.appendChild(intro);
                             intro.appendChild(node.cloneNode(true));
                        } else {
                             // Should not happen if prompt follows structure, but safe fallback
                             newContainer.lastChild.appendChild(node.cloneNode(true));
                        }
                    }
                }
            });
            htmlContent = newContainer.innerHTML;
        }

        const html = `
            <div class="fade-in">
                <div class="ai-content-markdown">
                    ${htmlContent}
                </div>
            </div>
        `;
        aiEl.innerHTML = html;
    }

    // Run Code
    runBtn.addEventListener('click', async () => {
        if (!window.editor) return;

        // UI Loading State
        runBtn.disabled = true;
        runBtn.innerHTML = '<span class="icon">⏳</span> Running...';
        setOutput('Executing code...');
        setAI(null); // Clear previous AI help

        const code = window.editor.getValue();

        try {
            const response = await fetch('/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: code })
            });

            const result = await response.json();

            if (result.success) {
                setOutput(result.output || '(No output)');
            } else {
                // Determine what to show in execution output panel
                let errorMsg = `Error: ${result.error}\n${result.message}`;
                if (result.traceback) {
                    errorMsg += `\n\n${result.traceback}`;
                }
                setOutput(errorMsg, true);

                // Show AI Analysis
                if (result.analysis) {
                    setAI(result.analysis);
                }
            }

        } catch (err) {
            setOutput('Network or Server Error: ' + err.message, true);
        } finally {
            runBtn.disabled = false;
            runBtn.innerHTML = '<span class="icon">▶</span> Run Code';
        }
    });

    // Clear Output
    clearBtn.addEventListener('click', () => {
        setOutput('Run your code to see output here...');
        setAI(null);
    });
});

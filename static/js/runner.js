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

        // Post-process: Wrap sections in semantic containers (emoji + text mapping)
        if (typeof document !== 'undefined') {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = htmlContent;
            
            const newContainer = document.createElement('div');
            let currentSection = null;
            
            function getSectionClass(text) {
                if (!text || typeof text !== 'string') return 'ai-section';
                const t = text.trim();
                if (t.includes('⚠️') || t.includes('What went wrong')) return 'ai-section error';
                if (t.includes('🧠') || t.includes('Concept involved')) return 'ai-section concept';
                if (t.includes('🛠️') || t.includes('How to fix')) return 'ai-section fix';
                if (t.includes('✅') || t.includes('Corrected code')) return 'ai-section success';
                if (t.includes('💡') || t.includes('Quick tip')) return 'ai-section tip';
                return 'ai-section';
            }
            
            Array.from(tempDiv.childNodes).forEach(node => {
                if (node.nodeName === 'H3') {
                    const text = node.textContent || "";
                    const sectionClass = getSectionClass(text);
                    
                    currentSection = document.createElement('div');
                    currentSection.className = sectionClass;
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

        runBtn.disabled = true;
        runBtn.innerHTML = '<span class="icon">⏳</span> Running...';
        setOutput('Executing code...');
        setAI(null);

        const code = window.editor.getValue();

        try {
            const response = await fetch('/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: code })
            });

            const text = await response.text();
            let result;

            try {
                result = JSON.parse(text);
            } catch (_) {
                // Server returned non-JSON (e.g. HTML error page from proxy)
                const preview = text.length > 300 ? text.slice(0, 300) + '...' : text;
                setOutput(`Server returned invalid response (expected JSON):\n\n${preview}`, true);
                return;
            }

            if (result.success) {
                setOutput(result.output || '(No output)');
            } else {
                let errorMsg = `Error: ${result.error || result.message || 'Unknown'}\n${result.message || ''}`;
                if (result.line) errorMsg += `\nLine: ${result.line}`;
                if (result.traceback) errorMsg += `\n\n${result.traceback}`;
                setOutput(errorMsg.trim(), true);

                if (result.analysis) {
                    setAI(result.analysis);
                }
            }
        } catch (err) {
            setOutput(`Network or Server Error: ${err.message}`, true);
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

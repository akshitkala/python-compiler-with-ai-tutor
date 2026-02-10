require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.38.0/min/vs' }});

require(['vs/editor/editor.main'], function() {
    // 1. Initialize Editor
    window.editor = monaco.editor.create(document.getElementById('editor-container'), {
        value: window.EDITOR_SNIPPETS['for'] || "print('Hello, AI Compiler!')",
        language: 'python',
        theme: 'vs-dark',
        automaticLayout: true,
        fontSize: 14,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        padding: { top: 15, bottom: 15 }
    });

    // 2. Register Custom Completion Item Provider
    monaco.languages.registerCompletionItemProvider('python', {
        provideCompletionItems: function(model, position) {
            var suggestions = [];
            
            // Add Snippets
            for (const [label, code] of Object.entries(window.EDITOR_SNIPPETS)) {
                suggestions.push({
                    label: label,
                    kind: monaco.languages.CompletionItemKind.Snippet,
                    insertText: code,
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Custom AI Compiler Snippet'
                });
            }

            return { suggestions: suggestions };
        }
    });

    // 3. Configure Language Defaults if in config
    // Note: Monaco handles basic Python types/indentation automatically.
});

/**
 * Este script observa los cambios en el DOM para detectar nuevas respuestas de los agentes,
 * extrae la información de trazabilidad (si existe) y la muestra en la consola del navegador.
 */

(function() {
    'use strict';

    console.log('Trace Logger Activado: Escuchando respuestas de los agentes...');

    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            if (mutation.addedNodes.length) {
                mutation.addedNodes.forEach(node => {
                    // Nos aseguramos de que el nodo sea un elemento HTML
                    if (node.nodeType === 1) {
                        // Buscamos el span de trazabilidad dentro del nuevo nodo
                        const traceElement = node.querySelector('span[data-trace-info]');
                        
                        if (traceElement) {
                            try {
                                const traceData = JSON.parse(traceElement.getAttribute('data-trace-info'));

                                // --- Imprimir en la consola con un estilo claro ---
                                console.groupCollapsed(`%c[Trace] Respuesta de: ${traceData.agent_name}`, 'color: #4CAF50; font-weight: bold;');
                                console.log(`%cAgente:`, 'font-weight: bold;', traceData.agent_name);
                                console.log(`%cFuente:`, 'font-weight: bold;', traceData.source);
                                console.log(`%cHerramienta:`, 'font-weight: bold;', traceData.tool_used);
                                
                                if (traceData.source === 'RAG') {
                                    console.groupCollapsed('Contexto RAG Utilizado');
                                    console.log(traceData.rag_context);
                                    console.groupEnd();
                                } else {
                                    console.log(`%cContexto RAG:`, 'font-weight: bold;', 'N/A');
                                }
                                console.groupEnd();

                                // Eliminar el elemento del DOM para que no sea visible
                                traceElement.remove();

                            } catch (e) {
                                console.error('Error al parsear los datos de trazabilidad:', e);
                            }
                        }
                    }
                });
            }
        });
    });

    // Empezar a observar el cuerpo del documento para cualquier cambio en los nodos hijos
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

})();

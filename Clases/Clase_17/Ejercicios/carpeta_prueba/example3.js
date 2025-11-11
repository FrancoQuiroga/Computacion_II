document.addEventListener('DOMContentLoaded', function() {
    
    // Obtener referencias a los elementos del DOM
    const mensajeParrafo = document.getElementById('mensaje');
    const boton = document.getElementById('miBoton');
    
    // --- Lógica inicial al cargar la página ---
    
    // 1. Cambiar el texto del párrafo
    mensajeParrafo.textContent = "¡Hola! JavaScript ha modificado este contenido al cargar.";
    
    // 2. Aplicar un estilo CSS adicional (definido en example2.css)
    mensajeParrafo.classList.add('js-activo');

    // --- Lógica al hacer clic en el botón ---
    
    boton.addEventListener('click', function() {
        const imagen = document.getElementById('myImage');
        
        // 3. Cambiar el texto del botón y el borde de la imagen
        if (boton.textContent === "Haz clic aquí") {
            boton.textContent = "¡Clickeado!";
            imagen.style.borderColor = 'red';
        } else {
            boton.textContent = "Haz clic aquí";
            imagen.style.borderColor = '#007bff';
        }
        
        console.log("El usuario hizo clic en el botón.");
    });
});
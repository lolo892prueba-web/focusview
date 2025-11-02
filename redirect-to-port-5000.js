// Script para redirigir automáticamente al puerto 5000
(function() {
    // Verificar si estamos en el puerto correcto
    const currentPort = window.location.port;
    const currentHost = window.location.hostname;
    const currentPath = window.location.pathname;
    
    // Lista de puertos desde los que queremos redirigir (no incluir 5000)
    const unwantedPorts = ['5500', '5001', '3000', '8080', '8000'];

    // Si estamos en un puerto no deseado, redirigir al 5000
    if (currentPort && unwantedPorts.includes(currentPort)) {
        console.log('🔄 Redirigiendo desde puerto', currentPort, 'al puerto 5000...');

        // Construir nueva URL apuntando al puerto 5000
        let newUrl;
        if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
            newUrl = `http://localhost:5000${currentPath}${window.location.search}${window.location.hash}`;
        } else {
            newUrl = `http://${currentHost}:5000${currentPath}${window.location.search}${window.location.hash}`;
        }

        // Redirigir inmediatamente
        window.location.replace(newUrl);
        return;
    }
    
    // Si estamos en localhost sin puerto, redirigir al 5000
    if ((currentHost === 'localhost' || currentHost === '127.0.0.1') && (currentPort === '' || !currentPort)) {
        console.log('🔄 Redirigiendo al puerto 5000...');
        const newUrl = `http://localhost:5000${currentPath}${window.location.search}${window.location.hash}`;
        window.location.replace(newUrl);
        return;
    }
    
    // Si estamos en el puerto 5000, todo está bien
    if (currentPort === '5000') {
        console.log('✅ Ejecutándose en el puerto correcto (5000)');
        return;
    }
    
    // Para otros casos, mostrar información
    console.log('ℹ️ Puerto actual:', currentPort || 'sin puerto');
    console.log('ℹ️ Host actual:', currentHost);
})();

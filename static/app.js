let map = L.map('map').setView([10.0647, -69.3570], 13); // Centrado en Barquisimeto

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
}).addTo(map);

let origenCoords = null;
let destinoCoords = null;
let origenMarker = null;
let destinoMarker = null;
let tipoServicio = 'moto';

document.querySelectorAll('.btn-servicio').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.btn-servicio').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        tipoServicio = btn.dataset.tipo;
        cotizar();
    });
});

map.on('click', function(e) {
    if (!origenCoords) {
        origenCoords = e.latlng;
        document.getElementById('origen').value = `${origenCoords.lat.toFixed(4)}, ${origenCoords.lng.toFixed(4)}`;
        origenMarker = L.marker(origenCoords).addTo(map).bindPopup("Origen").openPopup();
    } else if (!destinoCoords) {
        destinoCoords = e.latlng;
        document.getElementById('destino').value = `${destinoCoords.lat.toFixed(4)}, ${destinoCoords.lng.toFixed(4)}`;
        destinoMarker = L.marker(destinoCoords).addTo(map).bindPopup("Destino").openPopup();
        cotizar();
    }
});

async function cotizar() {
    if (!origenCoords || !destinoCoords) return;

    const response = await fetch('/api/cotizar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            lat_origen: origenCoords.lat,
            lng_origen: origenCoords.lng,
            lat_destino: destinoCoords.lat,
            lng_destino: destinoCoords.lng,
            tipo_servicio: tipoServicio
        })
    });

    const data = await response.json();
    document.getElementById('monto').innerText = `$${data.monto_estimado} USD`;
    document.getElementById('btnSolicitar').disabled = false;
}

document.getElementById('btnSolicitar').addEventListener('click', async () => {
    const response = await fetch('/api/solicitar-viaje', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            origen_texto: document.getElementById('origen').value,
            destino_texto: document.getElementById('destino').value,
            lat_origen: origenCoords.lat,
            lng_origen: origenCoords.lng,
            lat_destino: destinoCoords.lat,
            lng_destino: destinoCoords.lng,
            tipo_servicio: tipoServicio,
            metodo_pago: document.getElementById('pago').value,
            monto: parseFloat(document.getElementById('monto').innerText.replace('$', ''))
        })
    });

    const res = await response.json();
    alert(`¡Voy Pa' Ya solicitado con éxito! Código: ${res.id_viaje}\n${res.mensaje}`);
});
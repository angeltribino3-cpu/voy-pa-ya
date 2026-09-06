from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Voy Pa' Ya API")

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Gestor de conexiones en tiempo real para Pasajeros y Conductores
class ConnectionManager:
    def __init__(self):
        self.conductores: list[WebSocket] = []
        self.pasajeros: list[WebSocket] = []

    async def conectar_conductor(self, websocket: WebSocket):
        await websocket.accept()
        self.conductores.append(websocket)
        print("🟢 Conductor conectado vía WebSocket")

    def desconectar_conductor(self, websocket: WebSocket):
        if websocket in self.conductores:
            self.conductores.remove(websocket)
            print("🔴 Conductor desconectado")

    async def conectar_pasajero(self, websocket: WebSocket):
        await websocket.accept()
        self.pasajeros.append(websocket)
        print("🟢 Pasajero conectado vía WebSocket")

    def desconectar_pasajero(self, websocket: WebSocket):
        if websocket in self.pasajeros:
            self.pasajeros.remove(websocket)
            print("🔴 Pasajero desconectado")

    async def notificar_conductores(self, mensaje: dict):
        print(f"📡 Transmitiendo viaje a {len(self.conductores)} conductores activos...")
        for conductor in self.conductores:
            try:
                await conductor.send_json(mensaje)
            except Exception as e:
                print(f"Error enviando a conductor: {e}")

manager = ConnectionManager()

class SolicitudViaje(BaseModel):
    origen_texto: str
    destino_texto: str
    tipo_servicio: str
    monto: float
    metodo_pago: str

# Rutas web
@app.get("/")
async def get_cliente():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/conductor")
async def get_conductor():
    with open("static/conductor.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/admin")
async def get_admin():
    with open("static/admin.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/login")
async def get_login():
    with open("static/login.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# API para procesar y disparar el viaje
@app.post("/api/solicitar-viaje")
async def solicitar_viaje(solicitud: SolicitudViaje):
    monto_total = solicitud.monto
    comision = monto_total * 0.20
    ganancia = monto_total - comision

    evento_viaje = {
        "evento": "NUEVO_VIAJE",
        "origen": solicitud.origen_texto,
        "destino": solicitud.destino_texto,
        "tipo_servicio": solicitud.tipo_servicio.upper(),
        "monto_total": monto_total,
        "comision_app": comision,
        "ganancia_conductor": ganancia,
        "metodo_pago": solicitud.metodo_pago
    }

    await manager.notificar_conductores(evento_viaje)
    return {"status": "ok", "mensaje": "Viaje transmitido con éxito"}

# WebSockets
@app.websocket("/ws/conductor")
async def websocket_conductor(websocket: WebSocket):
    await manager.conectar_conductor(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.desconectar_conductor(websocket)

@app.websocket("/ws/pasajero")
async def websocket_pasajero(websocket: WebSocket):
    await manager.conectar_pasajero(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.desconectar_pasajero(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
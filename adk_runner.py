# adk_runner.py
import os
import asyncio
import vertexai
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from agents.coordinator.adk_coordinator import root_coordinator

# Configuración centralizada de Vertex AI
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "maitre-digital")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=project_id, location=location)

# Configuración de la aplicación
APP_NAME = "sumy_v3_adk_gastronomy"
DEFAULT_USER_ID = "guest_user"

class StatefulGastronomyRunner:
    """
    Runner mejorado con gestión de estado y sesiones para el sistema gastronómico.
    Implementa mejores prácticas de ADK con session service stateful.
    """
    
    def __init__(self):
        # Servicios de sesión y artefactos
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()
        
        # Runner principal con coordinador
        self.runner = Runner(
            agent=root_coordinator,
            app_name=APP_NAME,
            session_service=self.session_service,
            artifact_service=self.artifact_service
        )
        
        # Estado de la aplicación
        self.active_sessions = {}
        self.user_preferences = {}
        
        print("🚀 StatefulGastronomyRunner inicializado correctamente")
        print(f"📱 App: {APP_NAME}")
        print(f"🤖 Coordinador: {self.runner.agent.name}")
        print(f"👥 Sub-agentes: {len(self.runner.agent.sub_agents)}")
    
    async def create_session(self, user_id: str = None, session_id: str = None):
        """
        Crea una nueva sesión con estado inicial.
        """
        user_id = user_id or DEFAULT_USER_ID
        session_id = session_id or f"session_{len(self.active_sessions) + 1}"
        
        try:
            # Crear sesión con estado inicial
            session = await self.session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id,
                state={
                    "user_preferences": {},
                    "conversation_history": [],
                    "specialist_interactions": [],
                    "last_recommendations": {},
                    "session_metadata": {
                        "created_at": "now",
                        "user_type": "guest",
                        "experience_level": "beginner"
                    }
                }
            )
            
            # Registrar sesión activa
            self.active_sessions[session_id] = {
                "user_id": user_id,
                "session": session,
                "created_at": "now"
            }
            
            print(f"✅ Sesión creada: {session_id} para usuario {user_id}")
            return session
            
        except Exception as e:
            print(f"❌ Error creando sesión: {e}")
            raise
    
    async def run_query(self, query: str, user_id: str = None, session_id: str = None):
        """
        Ejecuta una consulta gastronómica con gestión de estado.
        """
        user_id = user_id or DEFAULT_USER_ID
        session_id = session_id or f"session_{len(self.active_sessions) + 1}"
        
        try:
            # Asegurar que existe la sesión
            if session_id not in self.active_sessions:
                await self.create_session(user_id, session_id)
            
            print(f"🔄 Procesando consulta: '{query}' (Usuario: {user_id}, Sesión: {session_id})")
            
            # Ejecutar consulta directamente usando las herramientas del coordinador
            response_events = []
            try:
                # Usar la herramienta de coordinación directamente
                coord_tool = self.runner.agent.tools[0]  # coordinate_gastronomy_experience
                result = coord_tool(query)
                
                print(f"🎭 Coordinador: {result}")
                
                # Crear evento con el resultado
                class ADKEvent:
                    def __init__(self, author, content):
                        self.author = author
                        self.content = content
                
                if isinstance(result, dict):
                    content = result.get('context', str(result))
                    status = result.get('status', 'processed')
                    
                    # Si hay delegación, mostrar información
                    if 'delegate_to' in status:
                        specialist = status.replace('delegate_to_', '')
                        content += f"\n\n🎯 Delegando a especialista: {specialist}"
                        
                    response_events = [ADKEvent("gastronomy_coordinator", content)]
                else:
                    response_events = [ADKEvent("gastronomy_coordinator", str(result))]
                    
            except Exception as e:
                print(f"❌ Error ejecutando coordinador: {e}")
                import traceback
                traceback.print_exc()
                
                # Fallback: respuesta de error
                class ErrorEvent:
                    def __init__(self, author, content):
                        self.author = author
                        self.content = content
                
                response_events = [ErrorEvent("gastronomy_coordinator", f"Error procesando consulta: {str(e)}")]
            
            # Obtener estado actualizado de la sesión
            updated_session = await self.session_service.get_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id
            )
            
            # Actualizar registro de sesión activa
            self.active_sessions[session_id]["session"] = updated_session
            
            return response_events
            
        except Exception as e:
            print(f"❌ Error ejecutando consulta: {e}")
            raise
    
    async def get_session_state(self, user_id: str, session_id: str):
        """
        Obtiene el estado actual de una sesión.
        """
        try:
            session = await self.session_service.get_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id
            )
            return session.state
            
        except Exception as e:
            print(f"❌ Error obteniendo estado de sesión: {e}")
            return None
    
    async def list_active_sessions(self):
        """
        Lista todas las sesiones activas.
        """
        return {
            "active_sessions": len(self.active_sessions),
            "sessions": list(self.active_sessions.keys())
        }
    
    async def cleanup_session(self, session_id: str):
        """
        Limpia una sesión específica.
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            print(f"🧹 Sesión {session_id} limpiada")
        else:
            print(f"⚠️ Sesión {session_id} no encontrada")

# Funciones de conveniencia para uso directo
async def quick_gastronomy_query(query: str, user_id: str = None):
    """
    Función de conveniencia para consultas rápidas.
    """
    runner = StatefulGastronomyRunner()
    return await runner.run_query(query, user_id)

async def interactive_gastronomy_session():
    """
    Sesión interactiva para pruebas y desarrollo.
    """
    runner = StatefulGastronomyRunner()
    session_id = "interactive_session"
    user_id = "developer"
    
    print("🎩 Bienvenido a la sesión gastronómica interactiva ADK")
    print("Escriba 'salir' para terminar")
    
    await runner.create_session(user_id, session_id)
    
    while True:
        try:
            query = input("\n🍽️ Consulta gastronómica: ").strip()
            
            if query.lower() in ['salir', 'exit', 'quit']:
                await runner.cleanup_session(session_id)
                print("👋 Sesión terminada")
                break
            
            if not query:
                continue
            
            # Ejecutar consulta
            await runner.run_query(query, user_id, session_id)
            
            # Mostrar estado de la sesión
            state = await runner.get_session_state(user_id, session_id)
            if state:
                interactions = len(state.get("specialist_interactions", []))
                print(f"📊 Interacciones con especialistas: {interactions}")
        
        except KeyboardInterrupt:
            await runner.cleanup_session(session_id)
            print("\n👋 Sesión terminada por el usuario")
            break
        except Exception as e:
            print(f"❌ Error en sesión interactiva: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    print("🚀 Inicializando sistema gastronómico ADK...")
    
    # Ejecutar sesión interactiva
    asyncio.run(interactive_gastronomy_session())
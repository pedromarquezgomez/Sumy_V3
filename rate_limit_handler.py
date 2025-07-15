# rate_limit_handler.py - Manejador de rate limiting para Sumy_V3 ADK
import time
from typing import Dict, Any
from functools import wraps

class RateLimitHandler:
    """Manejador inteligente de rate limiting para el nivel gratuito"""
    
    def __init__(self):
        self.last_request_time = 0
        self.min_interval = 5  # 5 segundos mínimo entre requests
        self.friendly_messages = [
            "⏳ **Nivel gratuito de la app** - Estás usando el nivel gratuito de Sumy_V3 ADK. "
            "Para evitar saturar los servidores, espera un minuto y vuelve a intentarlo. "
            "¡Tu consulta gastronómica será procesada en breve! 🍷✨",
            
            "🍷 **Paciencia, estimado comensal** - Nuestro sistema gratuito está procesando muchas consultas. "
            "Como un buen vino, las mejores respuestas requieren un poco de tiempo. "
            "Inténtalo nuevamente en unos momentos. 🎩",
            
            "🥗 **Servicio premium en preparación** - El nivel gratuito tiene límites para garantizar "
            "un servicio de calidad para todos. Por favor, espera un minuto antes de continuar. "
            "¡Nuestro equipo gastronómico te atenderá pronto! 🍳",
            
            "⭐ **Experiencia gastronómica gratuita** - Para mantener la calidad del servicio, "
            "limitamos las consultas simultáneas. Espera un momento y podrás disfrutar de "
            "nuestras recomendaciones culinarias. 🌟"
        ]
        self.message_index = 0
    
    def get_friendly_message(self) -> str:
        """Obtiene un mensaje amigable rotativo"""
        message = self.friendly_messages[self.message_index]
        self.message_index = (self.message_index + 1) % len(self.friendly_messages)
        return message
    
    def should_throttle(self) -> bool:
        """Determina si debe aplicar throttling"""
        current_time = time.time()
        if current_time - self.last_request_time < self.min_interval:
            return True
        self.last_request_time = current_time
        return False
    
    def is_rate_limit_error(self, error_str: str) -> bool:
        """Detecta si es un error de rate limiting"""
        rate_limit_indicators = [
            "429",
            "RESOURCE_EXHAUSTED", 
            "Resource exhausted",
            "rate limit",
            "quota exceeded",
            "too many requests"
        ]
        return any(indicator in error_str for indicator in rate_limit_indicators)
    
    def handle_rate_limit_response(self, error_str: str = None) -> Dict[str, Any]:
        """Genera respuesta amigable para rate limiting"""
        if error_str and self.is_rate_limit_error(error_str):
            return {
                "status": "rate_limited",
                "message": self.get_friendly_message(),
                "retry_after": 60,  # Sugerir esperar 60 segundos
                "type": "resource_exhausted"
            }
        else:
            return {
                "status": "error",
                "message": f"Error procesando consulta: {error_str}",
                "type": "general_error"
            }

# Instancia global del manejador
rate_handler = RateLimitHandler()

def rate_limit_decorator(func):
    """Decorador para manejar rate limiting automáticamente"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if rate_handler.should_throttle():
            return rate_handler.handle_rate_limit_response("throttled")
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if rate_handler.is_rate_limit_error(str(e)):
                return rate_handler.handle_rate_limit_response(str(e))
            else:
                raise e
    return wrapper
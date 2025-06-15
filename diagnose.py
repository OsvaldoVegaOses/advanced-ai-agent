#!/usr/bin/env python3
"""
Diagnóstico del sistema Advanced AI Agent
Para identificar problemas en el backend
"""

import sys
import os
import traceback
from datetime import datetime

def log_diagnostic(message, level="INFO"):
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {level}: {message}")

def test_imports():
    """Probar imports críticos"""
    log_diagnostic("=== TESTING IMPORTS ===")
    
    imports = [
        ("sys", "System module"),
        ("os", "OS module"),
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("openai", "OpenAI client"),
        ("azure.identity", "Azure authentication")
    ]
    
    results = {}
    for module, desc in imports:
        try:
            __import__(module)
            log_diagnostic(f"✅ {desc} ({module})")
            results[module] = True
        except ImportError as e:
            log_diagnostic(f"❌ {desc} ({module}): {e}", "ERROR")
            results[module] = False
    
    return results

def test_app_creation():
    """Probar creación de la app FastAPI"""
    log_diagnostic("=== TESTING APP CREATION ===")
    
    try:
        sys.path.append(os.path.dirname(__file__))
        from app import app
        log_diagnostic("✅ FastAPI app created successfully")
        
        # Listar rutas registradas
        log_diagnostic("📋 Registered routes:")
        if hasattr(app, 'routes'):
            # FastAPI app routes
            for route in app.routes:
                if hasattr(route, 'methods') and hasattr(route, 'path'):
                    methods = list(route.methods)
                    log_diagnostic(f"   {methods} {route.path}")
        elif hasattr(app, 'routes') and isinstance(app.routes, list):
            # Simple app routes
            for method, path, func in app.routes:
                log_diagnostic(f"   [{method}] {path} -> {func.__name__}")
        
        return True
    except Exception as e:
        log_diagnostic(f"❌ Failed to create app: {e}", "ERROR")
        traceback.print_exc()
        return False

def test_environment():
    """Verificar variables de entorno"""
    log_diagnostic("=== TESTING ENVIRONMENT ===")
    
    env_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY", 
        "AZURE_OPENAI_VERSION",
        "AZURE_CHAT_DEPLOYMENT",
        "ENVIRONMENT",
        "PORT"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Ocultar valores sensibles
            if "KEY" in var or "SECRET" in var:
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            log_diagnostic(f"✅ {var}={display_value}")
        else:
            log_diagnostic(f"⚠️ {var} not set")

def test_azure_openai():
    """Probar conexión a Azure OpenAI"""
    log_diagnostic("=== TESTING AZURE OPENAI ===")
    
    try:
        from openai import AsyncAzureOpenAI
        
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        if not endpoint or not api_key:
            log_diagnostic("⚠️ Azure OpenAI credentials not configured")
            return False
        
        log_diagnostic("✅ Azure OpenAI client can be created")
        return True
    except Exception as e:
        log_diagnostic(f"❌ Azure OpenAI test failed: {e}", "ERROR")
        return False

def test_fallback_mode():
    """Probar modo fallback"""
    log_diagnostic("=== TESTING FALLBACK MODE ===")
    
    try:
        sys.path.append(os.path.dirname(__file__))
        
        # Simular falta de AI modules
        original_modules = {}
        modules_to_hide = ['core.config', 'core.ai.model_manager']
        
        for mod in modules_to_hide:
            if mod in sys.modules:
                original_modules[mod] = sys.modules[mod]
                del sys.modules[mod]
        
        # Importar app en modo fallback
        if 'app' in sys.modules:
            del sys.modules['app']
        
        from app import app
        log_diagnostic("✅ App works in fallback mode")
        
        # Restaurar módulos
        for mod, module in original_modules.items():
            sys.modules[mod] = module
        
        return True
    except Exception as e:
        log_diagnostic(f"❌ Fallback mode failed: {e}", "ERROR")
        return False

def main():
    """Ejecutar diagnóstico completo"""
    log_diagnostic("🔍 ADVANCED AI AGENT DIAGNOSTIC")
    log_diagnostic("================================")
    
    # Test imports
    import_results = test_imports()
    
    # Test environment
    test_environment()
    
    # Test Azure OpenAI
    azure_openai_ok = test_azure_openai()
    
    # Test app creation
    app_ok = test_app_creation()
    
    # Test fallback
    fallback_ok = test_fallback_mode()
    
    # Summary
    log_diagnostic("=== DIAGNOSTIC SUMMARY ===")
    log_diagnostic(f"FastAPI: {'✅' if import_results.get('fastapi', False) else '❌'}")
    log_diagnostic(f"OpenAI: {'✅' if import_results.get('openai', False) else '❌'}")
    log_diagnostic(f"Azure: {'✅' if import_results.get('azure.identity', False) else '❌'}")
    log_diagnostic(f"App Creation: {'✅' if app_ok else '❌'}")
    log_diagnostic(f"Azure OpenAI: {'✅' if azure_openai_ok else '❌'}")
    log_diagnostic(f"Fallback Mode: {'✅' if fallback_ok else '❌'}")
    
    if app_ok:
        log_diagnostic("🎉 Backend should be working correctly!")
    else:
        log_diagnostic("⚠️ Backend has issues that need to be resolved")

if __name__ == "__main__":
    main()
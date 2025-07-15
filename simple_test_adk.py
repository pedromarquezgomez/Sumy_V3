# simple_test_adk.py
import asyncio
import sys
import os

# Verificar que los módulos se importen correctamente
print("🧪 Iniciando pruebas básicas de arquitectura ADK...")

def test_imports():
    """Prueba que todos los módulos se importen correctamente"""
    try:
        # Importar agentes especializados
        from agents.sumiller.adk_agent import sumiller_agent
        from agents.culinary.adk_agent import culinary_agent
        from agents.nutrition.adk_agent import nutrition_agent
        
        print("✅ Agentes especializados importados correctamente")
        print(f"   🍷 Sumiller: {sumiller_agent.name}")
        print(f"   🍳 Chef: {culinary_agent.name}")
        print(f"   🥗 Nutricionista: {nutrition_agent.name}")
        
        # Importar coordinador
        from agents.coordinator.adk_coordinator import root_coordinator
        print("✅ Coordinador importado correctamente")
        print(f"   🎩 Coordinador: {root_coordinator.name}")
        print(f"   👥 Sub-agentes: {len(root_coordinator.sub_agents)}")
        
        # Importar runner
        from adk_runner import StatefulGastronomyRunner
        print("✅ Runner importado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return False

def test_agent_configuration():
    """Prueba la configuración de los agentes"""
    try:
        from agents.coordinator.adk_coordinator import root_coordinator
        
        # Verificar coordinador
        assert root_coordinator.name == "gastronomy_coordinator"
        assert len(root_coordinator.sub_agents) == 3
        assert len(root_coordinator.tools) == 3
        
        # Verificar sub-agentes
        agent_names = [agent.name for agent in root_coordinator.sub_agents]
        expected_names = ["sumiller_specialist", "chef_specialist", "nutrition_specialist"]
        
        for expected in expected_names:
            assert expected in agent_names
        
        print("✅ Configuración de agentes validada")
        print(f"   🎯 Coordinador: {root_coordinator.name}")
        print(f"   🔧 Herramientas: {len(root_coordinator.tools)}")
        print(f"   👥 Sub-agentes: {agent_names}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def test_tools_configuration():
    """Prueba la configuración de herramientas"""
    try:
        from agents.sumiller.adk_agent import sumiller_agent
        from agents.culinary.adk_agent import culinary_agent
        from agents.nutrition.adk_agent import nutrition_agent
        
        # Verificar herramientas del sumiller
        assert len(sumiller_agent.tools) == 2
        tool_names = [tool.__name__ for tool in sumiller_agent.tools]
        assert "query_wine_knowledge" in tool_names
        assert "recommend_wine_pairing" in tool_names
        
        # Verificar herramientas del chef
        assert len(culinary_agent.tools) == 3
        tool_names = [tool.__name__ for tool in culinary_agent.tools]
        assert "query_culinary_knowledge" in tool_names
        assert "get_recipe_details" in tool_names
        assert "suggest_cooking_technique" in tool_names
        
        # Verificar herramientas del nutricionista
        assert len(nutrition_agent.tools) == 3
        tool_names = [tool.__name__ for tool in nutrition_agent.tools]
        assert "query_nutrition_knowledge" in tool_names
        assert "get_usda_nutrition_data" in tool_names
        assert "analyze_nutritional_content" in tool_names
        
        print("✅ Configuración de herramientas validada")
        print(f"   🍷 Sumiller: {len(sumiller_agent.tools)} herramientas")
        print(f"   🍳 Chef: {len(culinary_agent.tools)} herramientas")
        print(f"   🥗 Nutricionista: {len(nutrition_agent.tools)} herramientas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en herramientas: {e}")
        return False

def test_knowledge_bases():
    """Prueba que las bases de conocimientos se carguen"""
    try:
        # Verificar archivos de índices
        indexes = [
            "./indexes/enology_index",
            "./indexes/culinary_index", 
            "./indexes/nutrition_index"
        ]
        
        for index_path in indexes:
            if os.path.exists(index_path):
                print(f"✅ Índice encontrado: {index_path}")
            else:
                print(f"⚠️ Índice no encontrado: {index_path}")
        
        # Verificar que los agentes tengan acceso a sus bases
        from agents.sumiller.adk_agent import enology_kb
        from agents.culinary.adk_agent import culinary_kb
        from agents.nutrition.adk_agent import nutrition_kb
        
        kb_status = {
            "enology_kb": enology_kb is not None,
            "culinary_kb": culinary_kb is not None,
            "nutrition_kb": nutrition_kb is not None
        }
        
        print("✅ Estado de bases de conocimientos:")
        for kb_name, status in kb_status.items():
            print(f"   {'✅' if status else '❌'} {kb_name}: {'Cargada' if status else 'No disponible'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en bases de conocimientos: {e}")
        return False

async def test_basic_runner():
    """Prueba básica del runner"""
    try:
        from adk_runner import StatefulGastronomyRunner
        
        # Crear runner
        runner = StatefulGastronomyRunner()
        
        # Verificar inicialización
        assert runner.session_service is not None
        assert runner.runner.agent.name == "gastronomy_coordinator"
        assert len(runner.runner.agent.sub_agents) == 3
        
        # Crear sesión de prueba
        session = await runner.create_session("test_user", "test_session")
        assert session is not None
        assert session.id == "test_session"
        
        print("✅ Runner básico funcionando")
        print(f"   🎯 Agente: {runner.runner.agent.name}")
        print(f"   👥 Sub-agentes: {len(runner.runner.agent.sub_agents)}")
        print(f"   📋 Sesión creada: {session.id}")
        
        # Limpiar sesión
        await runner.cleanup_session("test_session")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en runner básico: {e}")
        return False

def test_file_structure():
    """Prueba que todos los archivos estén en su lugar"""
    try:
        files_to_check = [
            "agents/sumiller/adk_agent.py",
            "agents/culinary/adk_agent.py", 
            "agents/nutrition/adk_agent.py",
            "agents/coordinator/adk_coordinator.py",
            "adk_runner.py",
            "adk_config.py",
            "main.py",
            "README.md"
        ]
        
        all_exist = True
        for file_path in files_to_check:
            if os.path.exists(file_path):
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} - No encontrado")
                all_exist = False
        
        if all_exist:
            print("✅ Estructura de archivos completa")
        else:
            print("⚠️ Algunos archivos faltantes")
            
        return all_exist
        
    except Exception as e:
        print(f"❌ Error verificando archivos: {e}")
        return False

async def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("🚀 Iniciando suite de pruebas ADK simplificada...")
    print("=" * 50)
    
    tests = [
        ("Estructura de archivos", test_file_structure),
        ("Imports de módulos", test_imports),
        ("Configuración de agentes", test_agent_configuration),
        ("Configuración de herramientas", test_tools_configuration), 
        ("Bases de conocimientos", test_knowledge_bases),
        ("Runner básico", test_basic_runner)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 Ejecutando: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} - FAILED")
                
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} - ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ¡Todas las pruebas pasaron! Arquitectura ADK validada.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar configuración.")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
/**
 * CONNECTION TESTER MODULE
 * Módulo independiente para probar conectividad básica al backend
 */
class ConnectionTester {
  constructor() {
    this.backendUrl = 'https://advanced-ai-agent-0003.azurewebsites.net';
    this.testResults = {
      directConnection: null,
      proxyConnection: null,
      corsSupport: null,
      timestamp: null
    };
  }

  /**
   * Probar conexión directa al backend
   */
  async testDirectConnection() {
    console.log('🔍 Testing direct connection to backend...');
    
    try {
      const response = await fetch(`${this.backendUrl}/health`, {
        method: 'GET',
        mode: 'cors',
        credentials: 'omit',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      const isJson = response.headers.get('content-type')?.includes('application/json');
      const data = isJson ? await response.json() : await response.text();
      
      this.testResults.directConnection = {
        success: response.ok && isJson,
        status: response.status,
        contentType: response.headers.get('content-type'),
        data: data,
        error: response.ok && isJson ? null : 'Invalid content type or status'
      };
      
      console.log('✅ Direct connection test completed:', this.testResults.directConnection);
      return this.testResults.directConnection;
      
    } catch (error) {
      this.testResults.directConnection = {
        success: false,
        error: error.message,
        errorType: error.name
      };
      
      console.log('❌ Direct connection failed:', this.testResults.directConnection);
      return this.testResults.directConnection;
    }
  }

  /**
   * Probar conexión a través del proxy de Azure Static Web Apps
   */
  async testProxyConnection() {
    console.log('🔍 Testing proxy connection through /api/...');
    
    try {
      const response = await fetch('/api/health', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      const isJson = response.headers.get('content-type')?.includes('application/json');
      const data = isJson ? await response.json() : await response.text();
      
      this.testResults.proxyConnection = {
        success: response.ok && isJson,
        status: response.status,
        contentType: response.headers.get('content-type'),
        data: data,
        error: response.ok && isJson ? null : 'Proxy returning HTML instead of JSON'
      };
      
      console.log('✅ Proxy connection test completed:', this.testResults.proxyConnection);
      return this.testResults.proxyConnection;
      
    } catch (error) {
      this.testResults.proxyConnection = {
        success: false,
        error: error.message,
        errorType: error.name
      };
      
      console.log('❌ Proxy connection failed:', this.testResults.proxyConnection);
      return this.testResults.proxyConnection;
    }
  }

  /**
   * Probar soporte CORS con preflight
   */
  async testCorsSupport() {
    console.log('🔍 Testing CORS support...');
    
    try {
      // Test OPTIONS preflight
      const optionsResponse = await fetch(`${this.backendUrl}/health`, {
        method: 'OPTIONS',
        mode: 'cors',
        headers: {
          'Origin': window.location.origin,
          'Access-Control-Request-Method': 'GET',
          'Access-Control-Request-Headers': 'Content-Type'
        }
      });

      this.testResults.corsSupport = {
        success: optionsResponse.ok,
        status: optionsResponse.status,
        allowOrigin: optionsResponse.headers.get('Access-Control-Allow-Origin'),
        allowMethods: optionsResponse.headers.get('Access-Control-Allow-Methods'),
        allowHeaders: optionsResponse.headers.get('Access-Control-Allow-Headers'),
        error: optionsResponse.ok ? null : `OPTIONS failed with ${optionsResponse.status}`
      };

      console.log('✅ CORS test completed:', this.testResults.corsSupport);
      return this.testResults.corsSupport;

    } catch (error) {
      this.testResults.corsSupport = {
        success: false,
        error: error.message,
        errorType: error.name
      };

      console.log('❌ CORS test failed:', this.testResults.corsSupport);
      return this.testResults.corsSupport;
    }
  }

  /**
   * Ejecutar todos los tests
   */
  async runAllTests() {
    console.log('🚀 Running comprehensive connection tests...');
    this.testResults.timestamp = new Date().toISOString();

    await this.testDirectConnection();
    await this.testProxyConnection(); 
    await this.testCorsSupport();

    return this.getReport();
  }

  /**
   * Obtener reporte completo
   */
  getReport() {
    const report = {
      timestamp: this.testResults.timestamp,
      summary: {
        directWorks: this.testResults.directConnection?.success || false,
        proxyWorks: this.testResults.proxyConnection?.success || false,
        corsWorks: this.testResults.corsSupport?.success || false
      },
      recommendations: [],
      details: this.testResults
    };

    // Generar recomendaciones basadas en resultados
    if (report.summary.proxyWorks) {
      report.recommendations.push('✅ Use proxy connection (/api/*)');
    } else if (report.summary.directWorks && report.summary.corsWorks) {
      report.recommendations.push('✅ Use direct connection with CORS');
    } else if (report.summary.directWorks && !report.summary.corsWorks) {
      report.recommendations.push('⚠️ Backend works but CORS issues - consider JSONP or server proxy');
    } else {
      report.recommendations.push('❌ No working connection found - check backend status');
    }

    console.log('📊 Connection Test Report:', report);
    return report;
  }

  /**
   * Obtener el mejor método de conexión disponible
   */
  getBestConnectionMethod() {
    if (this.testResults.proxyConnection?.success) {
      return {
        method: 'proxy',
        baseUrl: '',
        prefix: '/api'
      };
    } else if (this.testResults.directConnection?.success && this.testResults.corsSupport?.success) {
      return {
        method: 'direct',
        baseUrl: this.backendUrl,
        prefix: ''
      };
    }
    return {
      method: 'none',
      baseUrl: null,
      prefix: null
    };
  }
}

// Export para uso global
window.ConnectionTester = ConnectionTester;
# Advanced AI Agent - Frontend

Frontend moderno desarrollado con **Next.js 14**, **TypeScript** y **TailwindCSS** para el Advanced AI Agent.

## 🚀 Características

- ✨ **Interfaz de chat moderna** con soporte para markdown y código
- 🎨 **Diseño responsive** optimizado para desktop y móvil
- 🔄 **Respuestas en tiempo real** con streaming
- 💾 **Persistencia de conversaciones** con Zustand
- 🎯 **TypeScript** para desarrollo robusto
- 🌈 **TailwindCSS** para estilos elegantes
- 🔔 **Sistema de notificaciones** integrado

## 🛠️ Tecnologías

- **Next.js 14** - Framework React con SSR/SSG
- **TypeScript** - Tipado estático
- **TailwindCSS** - Framework CSS utility-first
- **Zustand** - Gestión de estado simple y eficiente
- **Axios** - Cliente HTTP
- **React Markdown** - Renderizado de markdown
- **Framer Motion** - Animaciones fluidas
- **Heroicons** - Iconos SVG

## 📦 Instalación

\`\`\`bash
# Instalar dependencias
npm install

# Desarrollo
npm run dev

# Construcción para producción
npm run build

# Iniciar en producción
npm start

# Verificar tipos
npm run type-check

# Linting
npm run lint
\`\`\`

## 🏗️ Estructura del Proyecto

\`\`\`
src/
├── app/                    # Rutas de Next.js 14 (App Router)
│   ├── globals.css        # Estilos globales
│   ├── layout.tsx         # Layout principal
│   └── page.tsx           # Página principal
├── components/            # Componentes React
│   ├── chat/             # Componentes de chat
│   ├── layout/           # Componentes de layout
│   └── ui/               # Componentes UI reutilizables
├── hooks/                # Hooks personalizados
├── lib/                  # Utilidades y configuraciones
├── store/                # Store de Zustand
└── types/                # Definiciones TypeScript
\`\`\`

## 🔧 Configuración

### Variables de Entorno

Crea un archivo \`.env.local\`:

\`\`\`env
NEXT_PUBLIC_API_URL=https://advanced-ai-agent-0003.azurewebsites.net
\`\`\`

### Configuración del Backend

El frontend está configurado para conectarse automáticamente al backend desplegado en Azure App Services.

## 🎨 Personalización

### Temas y Colores

Los colores se definen en \`tailwind.config.js\`:

\`\`\`javascript
colors: {
  primary: { /* Azul principal */ },
  secondary: { /* Grises */ },
  accent: { /* Púrpura de acento */ }
}
\`\`\`

### Componentes

Todos los componentes están tipados con TypeScript y siguen patrones consistentes:

- **Props interfaces** definidas en \`types/index.ts\`
- **Styles** con TailwindCSS
- **Estado** gestionado con Zustand
- **Accesibilidad** con ARIA labels

## 📱 Responsive Design

El frontend está optimizado para:

- 📱 **Móvil**: Sidebar colapsible, navegación touch-friendly
- 💻 **Desktop**: Sidebar fijo, atajos de teclado
- 🖥️ **Tablet**: Diseño adaptativo

## 🔗 Integración con Backend

### API Client

\`\`\`typescript
import { apiClient } from '@/lib/api';

// Enviar mensaje
const response = await apiClient.sendMessage({
  message: 'Hola',
  conversationId: 'conv-123'
});

// Stream de respuestas
for await (const chunk of apiClient.streamMessage(request)) {
  console.log(chunk);
}
\`\`\`

### Store de Estado

\`\`\`typescript
import { useAppStore } from '@/store/useAppStore';

const { chat, sendMessage, addNotification } = useAppStore();
\`\`\`

## 🚀 Despliegue

### Azure Static Web Apps

1. **Construir el proyecto**:
   \`\`\`bash
   npm run build
   \`\`\`

2. **Configurar GitHub Actions** (automático)

3. **Variables de entorno** en Azure Portal

### Vercel (Alternativo)

\`\`\`bash
npx vercel --prod
\`\`\`

## 🔧 Desarrollo

### Comandos Útiles

\`\`\`bash
# Desarrollo con hot reload
npm run dev

# Verificar tipos sin compilar
npm run type-check

# Linting y formato
npm run lint

# Análisis de bundle
npm run analyze
\`\`\`

### Debugging

- **React DevTools** para componentes
- **Zustand DevTools** para estado
- **Network tab** para API calls

## 📚 Documentación Adicional

- [Next.js Documentation](https://nextjs.org/docs)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama feature (\`git checkout -b feature/nueva-funcionalidad\`)
3. Commit tus cambios (\`git commit -am 'Add nueva funcionalidad'\`)
4. Push a la rama (\`git push origin feature/nueva-funcionalidad\`)
5. Crea un Pull Request

## 📄 Licencia

MIT License - ver archivo [LICENSE](../LICENSE) para detalles.

---

Desarrollado con ❤️ por [Osvaldo Vega](https://github.com/OsvaldoVegaOses)
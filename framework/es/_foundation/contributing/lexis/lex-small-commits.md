# Lexis: Commits Atómicos Obligatorios

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Todos los commits en repositorios Guardia

## Propósito

Los commits pequeños y atómicos facilitan la revisión, reducen el riesgo de errores, mantienen un historial claro y permiten reversiones seguras. Los commits grandes que mezclan múltiples cambios dificultan el code review y hacen riesgosa la depuración.

Esta Lexis garantiza que cada commit represente una única unidad lógica de trabajo, conforme lo recomendado por el CONTRIBUTING de Guardia.

## Ley

> **Todo commit DEBE ser atómico — representando un único cambio lógico que puede integrarse independientemente.**

## Reglas

### 1. Un cambio por commit

Cada commit DEBE contener cambios relacionados con un único propósito. No se deben mezclar:
- Feature + corrección de error
- Refactorización + nueva funcionalidad
- Formato + cambio de lógica

### 2. Funcionalidad aislada

Cada commit DEBE dejar el código en estado funcional. El proyecto DEBE compilar y las pruebas existentes DEBEN pasar después de cada commit individual.

### 3. Granularidad adecuada

Si un commit es demasiado grande, DEBE dividirse en commits más pequeños. Si un commit es demasiado trivial (ej: renombrar una variable en un único lugar), puede agruparse con cambios relacionados.

### 4. Independencia

Cada commit DEBE poder comprenderse y, si es necesario, revertirse sin impactar partes no relacionadas del código.

## Alcance

- **Se aplica a:** todos los repositorios Guardia
- **Agentes vinculados:** todos
- **Excepciones:** Ninguna. Las Lexis no admiten excepciones.

## Consecuencias de Violación

1. **Bloqueo automático:** PR con commits mixtos puede ser solicitado a ser reorganizado
2. **Alerta:** el revisor solicita squash o rebase para separar cambios
3. **Remediación:** utilizar `git rebase -i` para dividir commits o reorganizar el historial

## Ejemplos

### Correcto

```
# Commit 1: solo la feature
feat(auth): add OAuth2 client configuration

# Commit 2: solo las pruebas
test(auth): add unit tests for OAuth2 flow

# Commit 3: solo la documentación
docs(auth): document OAuth2 setup instructions
```

### Incorrecto

```
# Un commit con todo mezclado — VIOLA LA LEY
feat(auth): add OAuth2, fix header bug, update README, refactor utils

# Este commit realiza 4 acciones no relacionadas:
# 1. Agrega OAuth2 (feat)
# 2. Corrige error en el header (fix)
# 3. Actualiza README (docs)
# 4. Refactoriza utils (refactor)
# Debería ser 4 commits separados.
```

## Validación Automatizada

- **Herramienta:** revisión humana + análisis de diff por agente de IA
- **Momento:** code review en el PR
- **Métrica:** cada commit debe tener un único tipo Conventional Commits y afectar un alcance coherente

## Referencias

- [CONTRIBUTING de Guardia](https://hub.guardia.finance/docs/community/CONTRIBUTING/)
- `lex-conventional-commits` — Formato obligatorio de commits
- `codex-commit-standards` — Guía completa de estándares de commit
- `kata-commit` — Procedimiento para realizar commits conformes

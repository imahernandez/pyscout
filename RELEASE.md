# Cómo publicar una nueva versión de PyScout

## Antes de empezar
Asegurate de tener en la raíz del proyecto:
- `ffmpeg.exe` (requerido para el instalador)
- `libmpv-2.dll`
- Las imágenes `lateral.png` y `chica.png`

---

## Paso 1 — Actualizar el número de versión

Cambiar el mismo número en **3 archivos**:

| Archivo | Línea | Qué cambiar |
|---|---|---|
| `utils/updater.py` | 5 | `CURRENT_VERSION = "1.0.X"` |
| `installer.iss` | 2 | `MyAppVersion = "1.0.X"` |
| `version.json` | 2 | `"version": "1.0.X"` |

También actualizar en `version.json`:
- `download_url` → reemplazar el número viejo por el nuevo en la URL
- `changelog` → escribir los cambios de esta versión

---

## Paso 2 — Compilar la app con Nuitka

Abrir cmd en la raíz del proyecto y ejecutar:

```
python -m nuitka --standalone --enable-plugin=pyside6 --windows-icon-from-ico=ico.ico --windows-console-mode=disable --include-data-files=ico.ico=ico.ico --include-data-files=ico_4k.png=ico_4k.png --include-data-files=splash.png=splash.png --include-data-files=lateral.png=lateral.png --include-data-files=chica.png=chica.png --include-data-files=libmpv-2.dll=libmpv-2.dll --include-data-dir=icons=icons --include-data-dir=fonts=fonts --include-package=translations --include-package=utils --output-dir=build main.py
```

Verificar que existe `build\main.dist\main.exe` antes de continuar.

---

## Paso 3 — Compilar el instalador con Inno Setup

```
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

Verificar que existe `dist\PyScout-Setup.exe` antes de continuar.

---

## Paso 4 — Subir el código fuente a GitHub

```
git add .
git commit -m "release: v1.0.X"
git push origin main
```

---

## Paso 5 — Crear el Release en GitHub y subir el instalador

```
gh release create v1.0.X "dist\PyScout-Setup.exe#PyScout-Setup.exe" --title "PyScout 1.0.X" --notes "- Cambio 1"
```

Reemplazar `v1.0.X` con la versión real y escribir los cambios en `--notes`.

Después verificar en el browser que el release tiene el `.exe` adjunto:
`https://github.com/imahernandez/pyscout/releases`

---

## Paso 6 — Verificar que el updater funciona

Esperar 1-2 minutos y abrir en el browser:
`https://imahernandez.github.io/pyscout/version.json`

Tiene que mostrar el número de versión nuevo. Si lo muestra, el updater
va a detectar la actualización automáticamente en el próximo arranque de la app.

---

## Checklist rápido

- [ ] `CURRENT_VERSION` en `utils/updater.py` actualizado
- [ ] `MyAppVersion` en `installer.iss` actualizado
- [ ] `version.json` actualizado (version + download_url + changelog)
- [ ] `build\main.dist\main.exe` existe (compilación Nuitka OK)
- [ ] `dist\PyScout-Setup.exe` existe (Inno Setup OK)
- [ ] Release creado en GitHub con el `.exe` adjunto
- [ ] `https://imahernandez.github.io/pyscout/version.json` muestra la versión nueva

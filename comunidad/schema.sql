-- Precios que carga la comunidad. Ninguna columna guarda la IP ni datos personales.
CREATE TABLE IF NOT EXISTS reportes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  creado TEXT NOT NULL DEFAULT (datetime('now')),
  fecha TEXT NOT NULL,                         -- día en que se vio el precio (AAAA-MM-DD)
  ean TEXT,                                    -- código de barras; vacío para frescos o sueltos
  producto TEXT NOT NULL,
  unidad TEXT NOT NULL DEFAULT 'unidad',       -- unidad | kg | litro
  tienda TEXT NOT NULL,
  provincia TEXT NOT NULL,
  localidad TEXT,
  precio REAL NOT NULL,
  oferta INTEGER NOT NULL DEFAULT 0,
  foto BLOB,                                   -- JPEG achicado en el navegador (máx. 300 KB)
  ip_hash TEXT NOT NULL,                       -- hash con sal: solo sirve para no contar dos veces a la misma persona
  estado TEXT NOT NULL DEFAULT 'pendiente'     -- pendiente | confirmado | aprobado | rechazado
);
CREATE INDEX IF NOT EXISTS idx_reportes_busqueda ON reportes (provincia, fecha, ean);
CREATE INDEX IF NOT EXISTS idx_reportes_estado ON reportes (estado);
CREATE INDEX IF NOT EXISTS idx_reportes_ip ON reportes (ip_hash, creado);
